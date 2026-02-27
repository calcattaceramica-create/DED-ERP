"""
Tenant Mixin for Multi-Tenant Support
======================================

This mixin adds tenant_id to models and provides automatic filtering.
"""

from flask import g, has_request_context
from sqlalchemy import event, true as sa_true
from sqlalchemy.orm import Query, with_loader_criteria, Session
from app import db


class TenantMixin:
    """
    Mixin to add tenant_id to models and enable automatic tenant filtering
    
    Usage:
        class MyModel(TenantMixin, db.Model):
            __tablename__ = 'my_table'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100))
    """
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Relationship to Tenant (will be added to all models)
    # tenant = db.relationship('Tenant', backref=db.backref('...', lazy='dynamic'))
    
    @staticmethod
    def get_current_tenant_id():
        """Get current tenant ID from Flask g object"""
        if has_request_context() and hasattr(g, 'current_tenant_id'):
            return g.current_tenant_id
        return None
    
    @classmethod
    def query_with_tenant(cls):
        """Query with automatic tenant filtering"""
        tenant_id = cls.get_current_tenant_id()
        if tenant_id:
            return cls.query.filter_by(tenant_id=tenant_id)
        return cls.query


class TenantQuery(Query):
    """
    Custom Query class that automatically filters by tenant_id
    """
    
    def get(self, ident):
        """Override get to add tenant filter"""
        tenant_id = TenantMixin.get_current_tenant_id()
        if tenant_id and hasattr(self._mapper_zero().class_, 'tenant_id'):
            return self.filter_by(tenant_id=tenant_id).filter_by(id=ident).first()
        return super().get(ident)
    
    def __iter__(self):
        """Override iteration to add tenant filter"""
        tenant_id = TenantMixin.get_current_tenant_id()
        if tenant_id and hasattr(self._mapper_zero().class_, 'tenant_id'):
            # Check if tenant_id filter is already applied
            if not self._has_tenant_filter():
                return super(TenantQuery, self.filter_by(tenant_id=tenant_id)).__iter__()
        return super().__iter__()
    
    def _has_tenant_filter(self):
        """Check if tenant_id filter is already applied"""
        # This is a simplified check - in production you might want more sophisticated logic
        if self.whereclause is not None:
            return 'tenant_id' in str(self.whereclause)
        return False


def set_tenant_id_on_insert(mapper, connection, target):
    """
    SQLAlchemy event listener to automatically set tenant_id on insert
    """
    if hasattr(target, 'tenant_id') and target.tenant_id is None:
        tenant_id = TenantMixin.get_current_tenant_id()
        if tenant_id:
            target.tenant_id = tenant_id


def validate_tenant_on_update(mapper, connection, target):
    """
    SQLAlchemy event listener to prevent changing tenant_id
    """
    if hasattr(target, 'tenant_id'):
        # Get the original tenant_id from the database
        state = db.inspect(target)
        history = state.get_history('tenant_id', True)
        
        if history.has_changes():
            # Tenant ID is being changed - this should not be allowed
            raise ValueError("Cannot change tenant_id of an existing record")


def register_tenant_events(model_class):
    """
    Register tenant-related events for a model class
    
    Args:
        model_class: The model class to register events for
    """
    if hasattr(model_class, 'tenant_id'):
        # Auto-set tenant_id on insert
        event.listen(model_class, 'before_insert', set_tenant_id_on_insert)
        
        # Prevent tenant_id changes on update
        event.listen(model_class, 'before_update', validate_tenant_on_update)


def setup_tenant_query_filter():
    """
    Register SQLAlchemy do_orm_execute event to automatically filter
    all SELECT queries by the current tenant_id.
    This is the core of multi-tenant data isolation.
    """

    @event.listens_for(Session, 'do_orm_execute')
    def _add_tenant_filter(orm_execute_state):
        # Only apply to SELECT statements, skip relationship loads
        if (not orm_execute_state.is_select
                or orm_execute_state.is_relationship_load
                or orm_execute_state.execution_options.get('skip_tenant_filter', False)):
            return

        # Get current tenant from request context
        tenant_id = None
        if has_request_context():
            tenant_id = getattr(g, 'current_tenant_id', None)

        if tenant_id is None:
            return

        # Build per-class criteria: filter by tenant_id only for models that have it,
        # and never filter the Tenant table itself (to avoid recursion).
        # track_closure_variables=False: tells SQLAlchemy not to cache-key
        # the query based on the closure variable `tenant_id` (it changes
        # per request). The bind value is still read from the closure on
        # every execution, so isolation is maintained correctly.
        def _make_criteria(cls):
            if (hasattr(cls, 'tenant_id')
                    and getattr(cls, '__tablename__', None) != 'tenants'):
                return cls.tenant_id == tenant_id
            return sa_true()

        orm_execute_state.statement = orm_execute_state.statement.options(
            with_loader_criteria(
                db.Model,
                _make_criteria,
                include_aliases=True,
                track_closure_variables=False,
            )
        )


def init_tenant_support(app):
    """
    Initialize tenant support for the application.
    This should be called after all models are defined.
    """
    from app import db

    # Register automatic query filtering (the main isolation mechanism)
    setup_tenant_query_filter()

    # Register before_insert events for all models with tenant_id
    for mapper in db.Model.registry.mappers:
        model_class = mapper.class_
        if hasattr(model_class, 'tenant_id'):
            register_tenant_events(model_class)

    app.logger.info("Multi-tenant support initialized with automatic query filtering")


# Utility functions for tenant management

def set_current_tenant(tenant_id):
    """Set the current tenant ID in Flask g object"""
    if has_request_context():
        g.current_tenant_id = tenant_id


def get_current_tenant():
    """Get the current tenant object"""
    tenant_id = TenantMixin.get_current_tenant_id()
    if tenant_id:
        from app.models_tenant import Tenant
        return Tenant.query.get(tenant_id)
    return None


def clear_current_tenant():
    """Clear the current tenant from Flask g object"""
    if has_request_context() and hasattr(g, 'current_tenant_id'):
        delattr(g, 'current_tenant_id')


def with_tenant(tenant_id):
    """
    Context manager to temporarily set a different tenant
    
    Usage:
        with with_tenant(5):
            # All queries here will use tenant_id=5
            users = User.query.all()
    """
    class TenantContext:
        def __init__(self, tenant_id):
            self.tenant_id = tenant_id
            self.previous_tenant_id = None
        
        def __enter__(self):
            self.previous_tenant_id = TenantMixin.get_current_tenant_id()
            set_current_tenant(self.tenant_id)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.previous_tenant_id:
                set_current_tenant(self.previous_tenant_id)
            else:
                clear_current_tenant()
    
    return TenantContext(tenant_id)


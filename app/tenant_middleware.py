"""
Tenant Middleware for Multi-Tenant Support
==========================================

This middleware identifies the current tenant based on:
1. Subdomain (e.g., company1.example.com)
2. Session (for logged-in users)
3. Custom header (for API requests)
"""

from flask import g, request, session, redirect, url_for, abort
from app.models_tenant import Tenant
from app.tenant_mixin import set_current_tenant, clear_current_tenant
import re


class TenantMiddleware:
    """
    Middleware to identify and set the current tenant for each request
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    @staticmethod
    def before_request():
        """
        Called before each request to identify the tenant
        """
        # Clear any previous tenant
        clear_current_tenant()
        
        # Skip tenant identification for certain routes
        if TenantMiddleware._should_skip_tenant_check():
            return None
        
        # Try to identify tenant from different sources
        tenant = None
        
        # 1. Try to get tenant from subdomain
        tenant = TenantMiddleware._get_tenant_from_subdomain()
        
        # 2. If not found, try to get from session (logged-in user)
        if not tenant:
            tenant = TenantMiddleware._get_tenant_from_session()
        
        # 3. If not found, try to get from custom header (API requests)
        if not tenant:
            tenant = TenantMiddleware._get_tenant_from_header()
        
        # 4. If still not found and user is logged in, get from user
        if not tenant:
            tenant = TenantMiddleware._get_tenant_from_user()
        
        # Set the current tenant
        if tenant:
            if not tenant.is_active:
                abort(403, description="Tenant account is inactive")
            
            if not tenant.is_subscription_active():
                # Redirect to subscription page or show error
                if request.endpoint and 'subscription' not in request.endpoint:
                    return redirect(url_for('main.subscription_expired'))
            
            set_current_tenant(tenant.id)
            g.current_tenant = tenant
        else:
            # No tenant found - redirect to tenant selection or registration
            if request.endpoint and request.endpoint not in ['auth.login', 'auth.register', 'auth.select_tenant', 'static']:
                # For now, we'll allow access without tenant for backward compatibility
                # In production, you might want to redirect to tenant selection
                pass
        
        return None
    
    @staticmethod
    def after_request(response):
        """Called after each request"""
        return response
    
    @staticmethod
    def teardown_request(exception=None):
        """Called when request context is torn down"""
        clear_current_tenant()
    
    @staticmethod
    def _should_skip_tenant_check():
        """Check if tenant identification should be skipped for this request"""
        # Skip for static files
        if request.endpoint == 'static':
            return True
        
        # Skip for certain auth routes
        skip_endpoints = [
            'auth.register_tenant',
            'auth.select_tenant',
        ]
        
        if request.endpoint in skip_endpoints:
            return True
        
        return False
    
    @staticmethod
    def _get_tenant_from_subdomain():
        """
        Extract tenant from subdomain
        
        Examples:
            - company1.localhost:5000 -> company1
            - company1.example.com -> company1
        """
        host = request.host.lower()
        
        # Remove port if present
        host = host.split(':')[0]
        
        # Split by dots
        parts = host.split('.')
        
        # If we have at least 2 parts (subdomain.domain), extract subdomain
        if len(parts) >= 2:
            subdomain = parts[0]
            
            # Skip common non-tenant subdomains
            if subdomain in ['www', 'api', 'admin', 'localhost', '127']:
                return None
            
            # Look up tenant by subdomain
            tenant = Tenant.query.filter_by(subdomain=subdomain).first()
            return tenant
        
        return None
    
    @staticmethod
    def _get_tenant_from_session():
        """Get tenant from session"""
        tenant_id = session.get('tenant_id')
        if tenant_id:
            return Tenant.query.get(tenant_id)
        return None
    
    @staticmethod
    def _get_tenant_from_header():
        """Get tenant from custom HTTP header"""
        # Check for X-Tenant-ID header
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                return Tenant.query.get(int(tenant_id))
            except (ValueError, TypeError):
                pass
        
        # Check for X-Tenant-Code header
        tenant_code = request.headers.get('X-Tenant-Code')
        if tenant_code:
            return Tenant.query.filter_by(code=tenant_code).first()
        
        return None
    
    @staticmethod
    def _get_tenant_from_user():
        """Get tenant from logged-in user"""
        from flask_login import current_user
        
        if current_user and current_user.is_authenticated:
            if hasattr(current_user, 'tenant_id') and current_user.tenant_id:
                return Tenant.query.get(current_user.tenant_id)
        
        return None


def get_tenant_url(tenant, path=''):
    """
    Generate URL for a specific tenant
    
    Args:
        tenant: Tenant object or subdomain string
        path: Path to append to the URL
    
    Returns:
        Full URL with tenant subdomain
    """
    if isinstance(tenant, Tenant):
        subdomain = tenant.subdomain
    else:
        subdomain = tenant
    
    # Get the base URL from request
    scheme = request.scheme
    host = request.host
    
    # Remove any existing subdomain
    host_parts = host.split('.')
    if len(host_parts) > 2:
        # Remove first part (subdomain)
        host = '.'.join(host_parts[1:])
    
    # Add new subdomain
    full_host = f"{subdomain}.{host}"
    
    # Build URL
    url = f"{scheme}://{full_host}{path}"
    
    return url


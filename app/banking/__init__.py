from flask import Blueprint

bp = Blueprint('banking', __name__, url_prefix='/banking')

from app.banking import routes


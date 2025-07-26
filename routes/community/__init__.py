from flask import Blueprint

community_bp = Blueprint('community', __name__, url_prefix='/community')

from . import views  # views 등록
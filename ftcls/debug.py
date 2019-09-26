from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ftcls import debug_only
from ftcls.auth import login_required
from ftcls.db_sqlite import get_db

bp = Blueprint('debug', __name__, url_prefix='/debug')


@bp.route('/show_projs')
@debug_only
def index():
    db = get_db()
    projects = db.execute(
        'SELECT id, title, description, created, admin_uid'
        ' FROM project'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('debug/show_projs.html', projects=projects)

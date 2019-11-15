from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask
)
from werkzeug.exceptions import abort

from ftcls import debug_only
from ftcls.auth import login_required
from ftcls.db_sqlite import get_db

bp = Blueprint('debug', __name__, url_prefix='/debug')


@bp.route('/all_proj')
@debug_only
def all_proj():
    db = get_db()
    projects = db.execute(
        'SELECT id, title, description, created, admin_uid'
        ' FROM project'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('debug/all_proj.html', projects=projects)


@bp.route('/all_user')
@debug_only
def all_user():
    db = get_db()
    users = db.execute(
        'SELECT id, username, password, org_id'
        ' FROM user'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('debug/all_user.html', users=users)



@bp.route('/')
@debug_only
def portal():
    flash("You are not supposed to be here unless you are a developer or hacker.", "danger")
    temp_app = Flask(__name__)
    temp_app.register_blueprint(bp)
    portals = [str(p) for p in temp_app.url_map.iter_rules()]
    return render_template('debug/index.html', portals=portals[:-2])



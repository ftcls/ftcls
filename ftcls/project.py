from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ftcls.auth import login_required
from ftcls.db_sqlite import get_db

bp = Blueprint('project', __name__, url_prefix='/project')


@bp.route('/')
@login_required
def index():
    db = get_db()
    projects = db.execute(
        'SELECT p.id, title, description, created, admin_uid, username'
        ' FROM project p JOIN user u ON p.admin_uid = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('project/index.html', projects=projects)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO project (title, description, admin_uid)'
                ' VALUES (?, ?, ?)',
                (title, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('project.index'))

    return render_template('project/create.html')


@bp.route('/dataset')
@login_required
def dataset():
    abort(501)


@bp.route('/edit')
@login_required
def edit():
    abort(501)


@bp.route('/annotate')
@login_required
def annotate():
    abort(501)

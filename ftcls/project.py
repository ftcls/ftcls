from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ftcls.auth import login_required
from ftcls.db_sqlite import get_db

bp = Blueprint('project', __name__, url_prefix='/project')


def get_proj(pid, check_author=True):
    proj = get_db().execute(
        'SELECT p.id, title, description, created, admin_uid, u.username'
        ' FROM project p, user u WHERE p.id = ? and p.admin_uid = u.id'
        ' ORDER BY created DESC',
        (pid,)
    ).fetchone()

    if proj is None:
        abort(404, "Project id {0} doesn't exist.".format(id))

    if check_author and proj['admin_uid'] != g.user['id']:
        abort(403, "Operation only allowed for project creator.")

    return proj


@bp.route('/')
@login_required
def index():
    db = get_db()
    projects = db.execute(
        'SELECT p.id, title, description, created, admin_uid, u.username'
        ' FROM project p, user u WHERE p.admin_uid = ? and p.admin_uid = u.id' # JOIN user u ON p.admin_uid = u.id'
        ' ORDER BY created DESC', (g.user['id'],)
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


@bp.route('/<int:pid>')
@login_required
def annotate(pid):
    flash("Merge .annotator here.", "info")
    return render_template('project/annotate.html', anno_data={"data":500})
    # abort(501)


@bp.route('/dataset')
@login_required
def dataset():
    flash("Dataset management page here, providing funcs like setting up "
          "training/dev/validate sets or splitting folds.", "info")
    abort(501)


@bp.route('/<int:pid>/edit', methods=('GET', 'POST'))
@login_required
def edit(pid):
    proj = get_proj(pid)

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
                'UPDATE proj SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, description, pid)
            )
            db.commit()
            return redirect(url_for('project.index'))

    return render_template('project/edit.html', proj=proj)


# @bp.route('/annotate')
# @login_required
# def annotate():
#     abort(501)


@bp.route('/delete')
@login_required
def delete():
    flash("Delete proj. Also removes related datasets or provide other options", "info")
    abort(501)

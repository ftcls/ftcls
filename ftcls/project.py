 # -*- coding: utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ftcls.auth import login_required
from ftcls.db_sqlite import get_db
from ftcls.ioutil import *

bp = Blueprint('project', __name__, url_prefix='/project')
_CONFIG_PREFIX = 'instance/conf/'
_INSTANCE_CONF = Profile(_CONFIG_PREFIX, "conf.json", {"pid_alloc": 0, "dsind_alloc": 0})


# Project
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
    # proj_prof = ProjectProfile(pid).load()

    return proj


@bp.route('/')
@login_required
def index():
    db = get_db()
    projects = db.execute(
        'SELECT p.id, title, description, created, admin_uid, u.username'
        ' FROM project p, user u WHERE p.admin_uid = ? and p.admin_uid = u.id'  # JOIN user u ON p.admin_uid = u.id'
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
            pid = _INSTANCE_CONF.get_key("pid_alloc") + 1  # TODO: potential hazard here. Use lock or switch to Redis
            _INSTANCE_CONF.set_key("pid_alloc", pid)
            ProjectProfile(pid)
            return redirect(url_for('project.index'))

    return render_template('project/create.html')


@bp.route('/<int:pid>')
@login_required
def annotate(pid):
    flash("Merge .annotator here.", "info")
    return render_template('project/annotate.html', pid=pid, data=
                                                    {"text": ["占位文本", "日本語も", "カタカナ", "ひらがな", "Lorem Ipsum",
                                                     "该项真命", "周会变需", "不知何出", "板啥是啥", "A1らB何cQu+=-"]})
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

# Dataset
@bp.route('/<int:pid>/import')
@login_required
def import_dataset(pid):
    flash("How will the data submitted to backend look like?", "info")
    abort(501)


@bp.route('/todo')
def todo():
    flash("Route placeholder", "info")
    abort(501)

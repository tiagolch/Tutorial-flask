from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required


bp = Blueprint('blog', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, p.created_at, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY p.created_at DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)  


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        created_at = datetime.now()
        updated_at = datetime.now()
        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, created_at, updated_at)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, body, g.user['id'], created_at, updated_at)
            )
            db.commit()
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, p.created_at, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        updated_at = datetime.now()
        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, updated_at = ?'
                ' WHERE id = ?',
                (title, body, updated_at, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
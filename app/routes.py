import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, cache
from app.models import User, Task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@bp.route('/')
@cache.cached(timeout=300)
def index():
    logger.info("Homepage accessed")
    return render_template('index.html')

@bp.route('/health')
@cache.cached(timeout=60)
def health():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy", "service": "task-manager"}), 200

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.info(f"Login attempt for user: {username}")

        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user created: {username}")

        if user.password == password:
            login_user(user)
            logger.info(f"User logged in: {username}")
            return redirect(url_for('main.tasks'))

        logger.warning(f"Failed login for user: {username}")
        flash('Invalid credentials')

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logger.info(f"User logged out: {current_user.username}")
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/tasks')
@login_required
def tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    logger.info(f"Tasks viewed by {current_user.username}: {len(user_tasks)} tasks")
    return render_template('tasks.html', tasks=user_tasks)

@bp.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')

    if title:
        new_task = Task(title=title, description=description, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        logger.info(f"Task created by {current_user.username}: {title}")
        flash('Task added successfully!')

    return redirect(url_for('main.tasks'))

@bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.completed = not task.completed
        db.session.commit()
        status = "completed" if task.completed else "uncompleted"
        logger.info(f"Task {status} by {current_user.username}: {task.title}")
    return redirect(url_for('main.tasks'))

@bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        logger.info(f"Task deleted by {current_user.username}: {task.title}")
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted!')
    return redirect(url_for('main.tasks'))

# Error handlers
@bp.app_errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return render_template('index.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    db.session.rollback()
    return "Internal Server Error", 500

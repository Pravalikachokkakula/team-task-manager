from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from extensions import db
from models import Task, Project, User
from datetime import datetime
from utils import send_task_notification

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
def list_tasks():
    if not g.user:
        return redirect(url_for('auth.login'))
        
    project_id = request.args.get('project_id')
    status_filter = request.args.get('status')
    search_query = request.args.get('q')
    
    page = request.args.get('page', 1, type=int)
    
    query = Task.query
    if g.user.role != 'Admin':
        query = query.filter_by(user_id=g.user.id)
        
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search_query:
        query = query.filter(Task.title.ilike(f'%{search_query}%'))
        
    if g.user.role == 'Admin':
        projects = Project.query.all()
    else:
        projects = Project.query.filter(Project.members.any(id=g.user.id)).all()
        
    tasks = query.order_by(Task.due_date.asc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('tasks.html', tasks=tasks, today=datetime.today().date(), projects=projects)

@tasks_bp.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    if not g.user or g.user.role != 'Admin':
        flash('Access denied. Only Admins can create tasks.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Task title is required.', 'danger')
            return redirect(url_for('tasks.create_task'))
            
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        project_id = request.form.get('project_id')
        user_id = request.form.get('user_id')
        
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('tasks.create_task'))
            
        task = Task(title=title, description=description, due_date=due_date, 
                    project_id=project_id, user_id=user_id if user_id else None)
        db.session.add(task)
        db.session.commit()
        
        if task.user_id:
            assignee = User.query.get(task.user_id)
            project = Project.query.get(task.project_id)
            if assignee and project:
                send_task_notification(assignee.email, task.title, project.name, task.due_date.strftime('%Y-%m-%d'))
                
        flash('Task assigned successfully.', 'success')
        return redirect(url_for('tasks.list_tasks'))
        
    projects = Project.query.all()
    users = User.query.all()
    return render_template('task_form.html', projects=projects, users=users)

@tasks_bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if not g.user or g.user.role != 'Admin':
        flash('Access denied. Only Admins can edit tasks.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
        
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        original_user_id = task.user_id
        
        title = request.form.get('title', '').strip()
        if not title:
            flash('Task title is required.', 'danger')
            return redirect(url_for('tasks.edit_task', task_id=task.id))
            
        task.title = title
        task.description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        task.project_id = request.form.get('project_id')
        user_id = request.form.get('user_id')
        task.user_id = user_id if user_id else None
        
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('tasks.edit_task', task_id=task.id))
            
        db.session.commit()
        
        if task.user_id and task.user_id != original_user_id:
            assignee = User.query.get(task.user_id)
            project = Project.query.get(task.project_id)
            if assignee and project:
                send_task_notification(assignee.email, task.title, project.name, task.due_date.strftime('%Y-%m-%d'))
                
        flash('Task updated successfully.', 'success')
        return redirect(url_for('tasks.list_tasks'))
        
    projects = Project.query.all()
    users = User.query.all()
    return render_template('task_form.html', task=task, projects=projects, users=users)

@tasks_bp.route('/tasks/update/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    if not g.user:
        return redirect(url_for('auth.login'))
        
    task = Task.query.get_or_404(task_id)
    if g.user.role != 'Admin' and task.user_id != g.user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
        
    status = request.form.get('status')
    if status in ['Pending', 'In Progress', 'Completed']:
        task.status = status
        db.session.commit()
        flash('Task status updated.', 'success')
        
    return redirect(request.referrer or url_for('tasks.list_tasks'))

@tasks_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if not g.user or g.user.role != 'Admin':
        flash('Access denied. Only Admins can delete tasks.', 'danger')
        return redirect(url_for('tasks.list_tasks'))
        
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'success')
    return redirect(request.referrer or url_for('tasks.list_tasks'))

@tasks_bp.route('/kanban')
def kanban():
    if not g.user:
        return redirect(url_for('auth.login'))
        
    query = Task.query
    if g.user.role != 'Admin':
        query = query.filter_by(user_id=g.user.id)
        
    tasks = query.order_by(Task.due_date.asc()).all()
    
    pending_tasks = [t for t in tasks if t.status == 'Pending']
    in_progress_tasks = [t for t in tasks if t.status == 'In Progress']
    completed_tasks = [t for t in tasks if t.status == 'Completed']
    
    return render_template('kanban.html', 
                           pending_tasks=pending_tasks, 
                           in_progress_tasks=in_progress_tasks, 
                           completed_tasks=completed_tasks,
                           today=datetime.today().date())

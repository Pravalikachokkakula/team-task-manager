from flask import Blueprint, render_template, g, redirect, url_for
from models import Task, Project
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('auth.login'))
        
    if g.user.role == 'Admin':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(user_id=g.user.id).all()
        
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == 'Completed'])
    pending_tasks = len([t for t in tasks if t.status in ['Pending', 'In Progress']])
    today = date.today()
    overdue_tasks = len([t for t in tasks if t.due_date < today and t.status != 'Completed'])
    
    # Calculate progress
    progress = 0
    if total_tasks > 0:
        progress = int((completed_tasks / total_tasks) * 100)
    
    recent_tasks = tasks[:5] if tasks else []
    
    return render_template('dashboard.html', 
        total=total_tasks, completed=completed_tasks, 
        pending=pending_tasks, overdue=overdue_tasks,
        progress=progress, recent_tasks=recent_tasks, today=today)

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from extensions import db
from models import Project, User

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
def list_projects():
    if not g.user:
        return redirect(url_for('auth.login'))
    page = request.args.get('page', 1, type=int)
    if g.user.role == 'Admin':
        query = Project.query
    else:
        query = Project.query.filter(Project.members.any(id=g.user.id))
    projects = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('projects.html', projects=projects)

@projects_bp.route('/projects/create', methods=['GET', 'POST'])
def create_project():
    if not g.user or g.user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('projects.list_projects'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Project name is required.', 'danger')
            return redirect(url_for('projects.create_project'))
            
        description = request.form.get('description')
        member_ids = request.form.getlist('members')
        
        project = Project(name=name, description=description, admin_id=g.user.id)
        project.members.append(g.user) # Add admin as member
        
        for mid in member_ids:
            member = User.query.get(mid)
            if member and member not in project.members:
                project.members.append(member)
                
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully.', 'success')
        return redirect(url_for('projects.list_projects'))
        
    users = User.query.filter(User.id != g.user.id).all()
    return render_template('project_form.html', users=users)

@projects_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if not g.user or g.user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('projects.list_projects'))
        
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.name = request.form.get('name', '').strip()
        if not project.name:
            flash('Project name is required.', 'danger')
            return redirect(url_for('projects.edit_project', project_id=project.id))
            
        project.description = request.form.get('description')
        member_ids = request.form.getlist('members')
        
        project.members = [g.user] # Keep admin
        for mid in member_ids:
            member = User.query.get(mid)
            if member and member not in project.members:
                project.members.append(member)
                
        db.session.commit()
        flash('Project updated successfully.', 'success')
        return redirect(url_for('projects.list_projects'))
        
    users = User.query.filter(User.id != g.user.id).all()
    return render_template('project_form.html', project=project, users=users)

@projects_bp.route('/projects/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if not g.user or g.user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('projects.list_projects'))
        
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully.', 'success')
    return redirect(url_for('projects.list_projects'))
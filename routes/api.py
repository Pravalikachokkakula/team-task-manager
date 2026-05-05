from flask import Blueprint, jsonify, request
from extensions import db, bcrypt
from models import Project, Task, User
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
        
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
        
    return jsonify({'error': 'Invalid username or password'}), 401

@api_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = int(get_jwt_identity())
    current_user = User.query.get_or_404(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if current_user.role == 'Admin':
        query = Project.query
    else:
        query = Project.query.filter(Project.members.any(id=current_user.id))
        
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "items": [p.to_dict() for p in paginated.items],
        "page": paginated.page,
        "pages": paginated.pages,
        "total": paginated.total,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev
    })

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    current_user = User.query.get_or_404(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    project_id = request.args.get('project_id')
    status_filter = request.args.get('status')
    search_query = request.args.get('q')
    
    if current_user.role == 'Admin':
        query = Task.query
    else:
        query = Task.query.filter_by(user_id=current_user.id)
        
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search_query:
        query = query.filter(Task.title.ilike(f'%{search_query}%'))
        
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "items": [t.to_dict() for t in paginated.items],
        "page": paginated.page,
        "pages": paginated.pages,
        "total": paginated.total,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev
    })

@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    current_user = User.query.get_or_404(user_id)
    
    if current_user.role != 'Admin':
        return jsonify({'error': 'Only admins can create tasks via API'}), 403
        
    data = request.get_json()
    if not data or not data.get('title') or not data.get('project_id') or not data.get('due_date'):
        return jsonify({'error': 'Missing required fields: title, project_id, due_date'}), 400
        
    try:
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        due_date=due_date,
        project_id=data['project_id'],
        user_id=data.get('user_id')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get_or_404(user_id)
    
    task = Task.query.get_or_404(task_id)
    
    # Permission check
    if current_user.role != 'Admin' and task.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    if 'status' in data:
        if data['status'] not in ['Pending', 'In Progress', 'Completed']:
            return jsonify({'error': 'Invalid status'}), 400
        task.status = data['status']
        
    if current_user.role == 'Admin':
        if 'title' in data: task.title = data['title']
        if 'description' in data: task.description = data['description']
        if 'user_id' in data: task.user_id = data['user_id']
        if 'due_date' in data:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
                
    db.session.commit()
    return jsonify(task.to_dict())

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get_or_404(user_id)
    
    if current_user.role != 'Admin':
        return jsonify({'error': 'Only admins can delete tasks'}), 403
        
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})

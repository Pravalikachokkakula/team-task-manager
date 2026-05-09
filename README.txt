TEAM TASK MANAGER

A production-ready, full-stack project management application built with Flask and Python. It enables users to create projects, assign tasks, and track progress using role-based access control, Kanban boards, and REST APIs.

LIVE DEMO

https://your-app-name.up.railway.app

FEATURES
Role-Based Access Control (Admin / Member)
Secure Authentication (Session + JWT)
Kanban Board for task tracking
Dashboard with task statistics
Asynchronous Email Notifications
Pagination, Search, and Filtering
Responsive UI with Dark/Light mode

TECH STACK
Backend: Python, Flask, SQLAlchemy, Bcrypt, JWT
Frontend: HTML, CSS, Bootstrap
Database: SQLite (Development), PostgreSQL (Production)
Deployment: Railway

LOCAL SETUP
Clone repository:
git clone https://github.com/Pravalikachokkakula/team-task-manager.git
Navigate:
cd team-task-manager
Install dependencies:
pip install -r requirements.txt
Create .env file:
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URI=sqlite:///app.db
Run:
python app.py

Application runs at:
http://localhost:5000

API ENDPOINTS

POST /api/login - Get JWT token
GET /api/projects - Get projects
GET /api/tasks - Get tasks (supports search/filter)
POST /api/tasks - Create task (Admin only)
PUT /api/tasks/<id> - Update task
DELETE /api/tasks/<id> - Delete task (Admin only)

DEPLOYMENT (RAILWAY)
Connect GitHub repository to Railway
Add PostgreSQL database
Set environment variables:
DATABASE_URI = Railway Postgres URL
SECRET_KEY = your_secret
JWT_SECRET_KEY = your_jwt_secret
Start command:
gunicorn app:app

AUTHOR

CHOKKAKULA PADMA PRAVALIKA
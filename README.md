# 🚀 Team Task Manager

A production-ready, full-stack project management application built with Flask and Python. It enables teams to create projects, assign tasks, and track progress using role-based access control, Kanban boards, and REST APIs.

---

## 🌐 Live Demo

👉 https://web-production-b458f.up.railway.app/

---

## 🚀 Features

* **Role-Based Access Control (RBAC):**
  Admins can create/delete projects and tasks, while Members can view and update assigned tasks.

* **Secure Authentication:**
  Session-based login for UI and JWT-based authentication for APIs. Passwords hashed using Bcrypt.

* **Kanban Board:**
  Visual task tracking across `Pending`, `In Progress`, and `Completed`.

* **Dynamic Dashboard:**
  Real-time overview of total, pending, completed, and overdue tasks.

* **Asynchronous Email Notifications:**
  Background threading sends task assignment emails without blocking UI.

* **Advanced Data Handling:**
  Pagination, filtering, and search using SQLAlchemy.

* **Responsive UI:**
  Built with Bootstrap 5 and includes Dark/Light mode toggle.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Bcrypt, Flask-JWT-Extended
* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2
* **Database:** SQLite (Development) / PostgreSQL (Production)
* **Deployment:** Railway

---

## ⚙️ Local Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/team-task-manager.git
cd team-task-manager
```

### 2. Create virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file:

```env
SECRET_KEY=your_super_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URI=sqlite:///app.db

# Optional: Email
# MAIL_USERNAME=your_email@gmail.com
# MAIL_PASSWORD=your_app_password
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
```

---

### 4. Run the application

```bash
python app.py
```

👉 App runs at: http://localhost:5000

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api`
Use: `Authorization: Bearer <token>`

| Method | Endpoint          | Description                   | Auth |
| ------ | ----------------- | ----------------------------- | ---- |
| POST   | `/api/login`      | Get JWT token                 | ❌    |
| GET    | `/api/projects`   | Get projects                  | ✅    |
| GET    | `/api/tasks`      | Get tasks (filters supported) | ✅    |
| POST   | `/api/tasks`      | Create task (Admin)           | ✅    |
| PUT    | `/api/tasks/<id>` | Update task                   | ✅    |
| DELETE | `/api/tasks/<id>` | Delete task (Admin)           | ✅    |

---

## 🌐 Deployment (Railway)

1. Connect GitHub repo to Railway
2. Add **PostgreSQL database**
3. In **Web Service → Variables**, add:

```
DATABASE_URI = ${{Postgres.DATABASE_URL}}
SECRET_KEY = your_secret
JWT_SECRET_KEY = your_jwt_secret
```

4. Ensure start command:

```
gunicorn app:app
```

5. Deploy 🚀

👉 Database tables auto-create on first run.

---

## 📄 License

This project is open-source under the MIT License.

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import os

app = Flask(__name__)

# CONFIG
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.String(50))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Pending")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# HOME
@app.route('/')
def index():
    return render_template("index.html")


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("User already exists!")
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!")
        return redirect(url_for('login'))

    return render_template("register.html")


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for('dashboard'))

        flash("Invalid credentials!")
        return render_template("login.html")

    return render_template("login.html")


# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for('index'))


# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        total_tasks=len(tasks),
        completed_tasks=len([t for t in tasks if t.status == "Completed"]),
        pending_tasks=len([t for t in tasks if t.status == "Pending"])
    )


# ADD TASK
@app.route('/add-task', methods=['POST'])
@login_required
def add_task():
    due_date = request.form['due_date']
    due_date = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None

    task = Task(
        title=request.form['title'],
        description=request.form['description'],
        priority=request.form['priority'],
        due_date=due_date,
        user_id=current_user.id
    )

    db.session.add(task)
    db.session.commit()

    flash("Task added!")
    return redirect(url_for('dashboard'))


# COMPLETE TASK
@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id == current_user.id:
        task.status = "Completed"
        db.session.commit()

    return redirect(url_for('dashboard'))


# EDIT TASK
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.priority = request.form['priority']

        db.session.commit()
        flash("Task updated!")
        return redirect(url_for('dashboard'))

    return render_template("edit_task.html", task=task)


# DELETE TASK
@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()

    flash("Task deleted!")
    return redirect(url_for('dashboard'))


# RUN
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
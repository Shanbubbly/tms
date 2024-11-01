from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Connection Setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shanmathi123*",
        database="todo_db"
    )

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to require admin role
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Access Denied. Admins Only.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Admin Dashboard


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db_connection()
    cursor = db.cursor()

    # Fetch all tasks along with assigned user info
    cursor.execute("""
        SELECT tasks.id, users.username, tasks.task, tasks.priority, tasks.status 
        FROM tasks 
        JOIN users ON tasks.user_id = users.id
    """)
    tasks = cursor.fetchall()
    db.close()

    return render_template('admin_dashboard.html', tasks=tasks)


@app.route('/user/dashboard')
@login_required
def user_dashboard():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id=%s", (session['user_id'],))
    tasks = cursor.fetchall()
    db.close()
    return render_template('user_dashboard.html', tasks=tasks)


# Add Task (Admin only)
@app.route('/admin/add_task', methods=['GET', 'POST'])
@admin_required
def add_task():
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        task = request.form['task']
        priority = request.form['priority']
        user_id = request.form['user_id']
        
        cursor.execute("INSERT INTO tasks (user_id, task, priority, status) VALUES (%s, %s, %s, %s)", 
                       (user_id, task, priority, 'Incomplete'))
        db.commit()
        db.close()
        
        flash("Task added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    # Get list of users to assign tasks to
    cursor.execute("SELECT id, username FROM users WHERE role = 'user'")
    users = cursor.fetchall()
    db.close()

    return render_template('add_task.html', users=users)


# Edit Task (Admin only)
@app.route('/admin/edit_task/<int:task_id>', methods=['GET', 'POST'])
@admin_required
def edit_task(task_id):
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        task = request.form['task']
        priority = request.form['priority']
        status = request.form['status']
        
        cursor.execute("UPDATE tasks SET task=%s, priority=%s, status=%s WHERE id=%s", 
                       (task, priority, status, task_id))
        db.commit()
        db.close()
        
        flash("Task updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    # Fetch task details for the form
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
    task = cursor.fetchone()
    db.close()

    return render_template('edit_task.html', task=task)

@app.route('/admin/delete_task/<int:task_id>', methods=['POST'])
@admin_required
def delete_task(task_id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db.commit()
        flash("Task deleted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"An error occurred while deleting the task: {str(e)}", "error")
    finally:
        db.close()
    
    return redirect(url_for('admin_dashboard'))


@app.route('/update_progress/<int:task_id>', methods=['POST'])
@login_required
def update_progress(task_id):
    db = get_db_connection()
    cursor = db.cursor()
    status = request.form['status']
    print("Updating status to:", status)  # Debug print to confirm the status value
    
    cursor.execute("UPDATE tasks SET status=%s WHERE id=%s AND user_id=%s", 
                   (status, task_id, session['user_id']))
    db.commit()
    db.close()
    return redirect(url_for('index'))


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        db.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[1]
            
            # Redirect based on role
            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html')


# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                       (username, password, role))
        db.commit()
        db.close()
        flash("Account created successfully. Please log in.")
        return redirect(url_for('login'))
    return render_template('signup.html')

# Logout
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)












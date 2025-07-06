from flask import Flask, render_template, g, request, redirect, url_for 
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import sqlite3
import os

app = Flask(__name__)

app.secret_key = 'your-secret-key'  # Replace with something unique and secure

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect here if login is required

from datetime import datetime

db_initialised = False

@app.template_filter('datetimeformat')
def format_datetime(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return value

DATABASE = os.path.join(os.getcwd(), 'app.db')

# --- Database creation ---

@app.before_request
def init_db_once():
    global db_initialised
    if not db_initialised:
        db_path = os.path.join(os.getcwd(), 'app.db')
        if not os.path.exists(db_path):
            with app.app_context():
                db = get_db()
                with open('schema.sql', 'r') as f:
                    db.executescript(f.read())

                # Insert dummy data for assessment
                db.executescript("""
                INSERT INTO users (username, password, first_name, last_name, role) VALUES
                    ('admin', 'adminpass', 'Admin', 'User', 'admin'),
                    ('jdoe', 'pass1', 'John', 'Doe', 'user'),
                    ('asmith', 'pass2', 'Alice', 'Smith', 'user'),
                    ('bwhite', 'pass3', 'Bob', 'White', 'user'),
                    ('cgreen', 'pass4', 'Clara', 'Green', 'user'),
                    ('dthomas', 'pass5', 'Dan', 'Thomas', 'user'),
                    ('ekhan', 'pass6', 'Emma', 'Khan', 'user'),
                    ('flam', 'pass7', 'Freddie', 'Lam', 'user'),
                    ('gchen', 'pass8', 'Grace', 'Chen', 'user'),
                    ('hlee', 'pass9', 'Hannah', 'Lee', 'user');

                INSERT INTO faults (title, description, location, status, submitted_by) VALUES
                    ('Light flickering', 'Office light near window is flickering.', 'Room 1A', 'Open', 2),
                    ('Broken heater', 'No heat in meeting room.', 'Room 2B', 'Open', 3),
                    ('Leaking tap', 'Tap leaking in staff kitchen.', 'Kitchen', 'Closed', 4),
                    ('Loose tile', 'Floor tile is loose.', 'Reception', 'Open', 5),
                    ('Network drop', 'Frequent disconnections.', 'IT Room', 'Closed', 2),
                    ('Door stuck', 'Main entrance door not opening smoothly.', 'Entrance', 'Open', 6),
                    ('Printer jam', 'Printer constantly jamming.', 'Print Room', 'Open', 7),
                    ('Air conditioning', 'AC blowing hot air.', 'Room 3C', 'Closed', 8),
                    ('Broken desk', 'Leg snapped off desk in breakout space.', 'Breakout Area', 'Open', 9),
                    ('Toilet flush broken', 'Toilet does not flush.', 'Toilets', 'Closed', 10);
                """)
                db.commit()
            db_initialised = True

# --- Database connection ---

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # So we can use dict-like access
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Login ---

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(id=user['id'], username=user['username'], role=user['role'])
    return None

# --- Routes ---

@app.route('/')
@login_required
def index():
    db = get_db()
    faults = db.execute("""
    SELECT 
        faults.*, 
        submitter.first_name || ' ' || submitter.last_name AS submitted_by_name,
        closer.first_name || ' ' || closer.last_name AS closed_by_name
    FROM faults
    JOIN users AS submitter ON faults.submitted_by = submitter.id
    LEFT JOIN users AS closer ON faults.closed_by = closer.id
    ORDER BY faults.date_created DESC
""").fetchall()
    return render_template('index.html', faults=faults)

@app.route('/submit', methods=['POST'])
@login_required
def submit_fault():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        submitted_by = current_user.id
        db.execute(
            'INSERT INTO faults (title, description, location, status, submitted_by) VALUES (?, ?, ?, ?, ?)',
            (title, description, location, 'Open', submitted_by)
        )
        db.commit()
        return redirect(url_for('index'))

@app.route('/close/<int:fault_id>', methods=['POST'])
@login_required
def close_fault(fault_id):
    db = get_db()
    today = datetime.today().strftime('%Y-%m-%d')  # Save as string
    db.execute(
        'UPDATE faults SET status = ?, closed_by = ?, date_closed = ? WHERE id = ?',
        ('Closed', current_user.id, today, fault_id)
    )
    db.commit()
    return redirect(url_for('index'))
    
@app.route('/delete/<int:fault_id>', methods=['POST'])
@login_required
def delete_fault(fault_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403

    db = get_db()
    db.execute('DELETE FROM faults WHERE id = ?', (fault_id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    db = get_db()
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']

        try:
            db.execute(
                'INSERT INTO users (username, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)',
                (username, password, first_name, last_name, role)
            )
            db.commit()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            error = "Username already exists."
    return render_template('add_user.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and user['password'] == password:
            user_obj = User(id=user['id'], username=user['username'], role=user['role'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Entry Point ---
if __name__ == '__main__':
    app.run(debug=True)
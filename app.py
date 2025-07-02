from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = os.path.join(os.getcwd(), 'app.db')

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

# --- Routes ---
@app.route('/')
def index():
    db = get_db()
    faults = db.execute("""
    SELECT 
        faults.*, 
        submitter.first_name || ' ' || submitter.last_name AS submitted_by_name,
        resolver.first_name || ' ' || resolver.last_name AS resolved_by_name
    FROM faults
    JOIN users AS submitter ON faults.submitted_by = submitter.id
    LEFT JOIN users AS resolver ON faults.resolved_by = resolver.id
    ORDER BY faults.date_created DESC
""").fetchall()
    return render_template('index.html', faults=faults)

# --- Submission ---
@app.route('/submit', methods=['GET', 'POST'])
def submit_fault():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        submitted_by = 1  # Simulated user ID
        db.execute(
            'INSERT INTO faults (title, description, location, status, submitted_by) VALUES (?, ?, ?, ?, ?)',
            (title, description, location, 'Open', submitted_by)
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template('submit.html')

# --- Entry Point ---
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "3b3ba30acc37a5f26db7a380ec905d7711f524d6af2f38a1your_secret_key"  # For flash messages

# Connect to MySQL Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="project"  # Replace with your database name
)

# Sample in-memory storage for diary entries
# Each entry will be a dictionary with id, title, content, and date
diary_entries = []

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch user data from database
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        # Validate credentials
        if user and check_password_hash(user['password'], password):
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password. Please try again.")
            return redirect(url_for('login'))
    return render_template('login.html')

# Register route
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate password confirmation
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Insert user data into the database
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            db.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}")
            return redirect(url_for('register'))
        finally:
            cursor.close()
    return render_template('register.html')

# Home route - display all entries
@app.route('/index.html')
def index():
    return render_template('index.html', entries=diary_entries)

# Route to add a new entry
@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        diary_entries.append({
            "id": len(diary_entries) + 1,
            "title": title,
            "content": content,
        })
        return redirect(url_for('index'))
    return render_template('add.html')

# Route to view a single entry
@app.route('/view/<int:entry_id>')
def view_entry(entry_id):
    entry = next((e for e in diary_entries if e['id'] == entry_id), None)
    return render_template('view.html', entry=entry)

# Route to edit an entry
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = next((e for e in diary_entries if e['id'] == entry_id), None)
    if request.method == 'POST':
        entry['title'] = request.form.get('title')
        entry['content'] = request.form.get('content')
        return redirect(url_for('index'))
    return render_template('edit.html', entry=entry)

# Route to delete an entry
@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    global diary_entries
    diary_entries = [e for e in diary_entries if e['id'] != entry_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

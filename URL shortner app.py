from flask import Flask, render_template, request, redirect, g
import sqlite3
import shortuuid


app = Flask(__name__)

# Configuration
DATABASE = 'urls.db'

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Create a table to store URL mappings
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_url TEXT NOT NULL
            )
        ''')
        db.commit()

# Close the database connection at the end of each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database
init_db()

# Routes...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('original_url')

    # Generate a unique short URL
    short_url = shortuuid.uuid()[:8]

    # Store the mapping in the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
    db.commit()

    return render_template('result.html', original_url=original_url, short_url=short_url)

@app.route('/<short_url>')
def redirect_to_original(short_url):
    # Retrieve the original URL from the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
    result = cursor.fetchone()

    if result:
        original_url = result[0]
        return redirect(original_url)
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True)

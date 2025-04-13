from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home Route: Display Movies
@app.route('/')
def index():
    conn = get_db_connection()
    movies = conn.execute('SELECT * FROM movies ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', movies=movies)

# Upload Route: Upload Movie
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        poster = request.files['poster']
        movie_file = request.files['movie_file']

        # Secure file names
        poster_filename = secure_filename(poster.filename)
        movie_filename = secure_filename(movie_file.filename)

        poster_path = os.path.join(UPLOAD_FOLDER, poster_filename)
        movie_path = os.path.join(UPLOAD_FOLDER, movie_filename)

        # Save files
        poster.save(poster_path)
        movie_file.save(movie_path)

        # Save data in the database
        conn = get_db_connection()
        conn.execute('INSERT INTO movies (title, description, poster, filename) VALUES (?, ?, ?, ?)',
                     (title, description, poster_filename, movie_filename))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('upload.html')

# Edit Route: Edit Movie
@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        poster = request.files['poster']
        movie_file = request.files['movie_file']

        # Update movie details
        poster_filename = secure_filename(poster.filename) if poster else movie['poster']
        movie_filename = secure_filename(movie_file.filename) if movie_file else movie['filename']

        # Save files if they were uploaded
        if poster:
            poster_path = os.path.join(UPLOAD_FOLDER, poster_filename)
            poster.save(poster_path)
        if movie_file:
            movie_path = os.path.join(UPLOAD_FOLDER, movie_filename)
            movie_file.save(movie_path)

        # Update database with new details
        conn.execute('UPDATE movies SET title = ?, description = ?, poster = ?, filename = ? WHERE id = ?',
                     (title, description, poster_filename, movie_filename, movie_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)

# Route to Download Movie
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

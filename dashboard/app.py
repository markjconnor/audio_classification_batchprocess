from flask import Flask, jsonify, render_template, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Paths based on your cluster architecture
DB_PATH = '/beegfs/dataset/results.db'
AUDIO_DIR = '/beegfs/dataset/audio_files/'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This allows us to return dictionaries instead of tuples
    return conn

@app.route('/')
def index():
    # Serves the main HTML page
    return render_template('index.html')

@app.route('/api/genres')
def get_genres():
    # Query to count how many files are in each genre
    conn = get_db_connection()
    genres = conn.execute('''
        SELECT prediction, COUNT(*) as count 
        FROM audio_predictions 
        GROUP BY prediction 
        ORDER BY count DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in genres])

@app.route('/api/tracks/<genre>')
def get_tracks(genre):
    # Query to get all tracks for a genre, sorted by highest confidence score
    conn = get_db_connection()
    tracks = conn.execute('''
        SELECT filename, score 
        FROM audio_predictions 
        WHERE prediction = ? 
        ORDER BY score DESC
    ''', (genre,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in tracks])

@app.route('/audio/<filename>')
def serve_audio(filename):
    # Securely serves the .wav files from the BeeGFS drive to the browser
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    # Run on all network interfaces so you can access it externally
    app.run(host='0.0.0.0', port=5000)
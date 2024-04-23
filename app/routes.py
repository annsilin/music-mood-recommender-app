from flask import render_template, request, jsonify
from app import app, db
from app.models import Song, Genre
import random
import os
from process_songs import fetch_genres, make_predictions
from werkzeug.utils import secure_filename
import csv
import ast


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/get-songs', methods=['POST'])
def get_songs():

    data = request.get_json()
    genre_id = data['genre']
    x = float(data['x'])
    y = float(data['y'])

    happy_prob = x * y
    aggressive_prob = (1 - x) * y
    sad_prob = (1 - x) * (1 - y)
    calm_prob = x * (1 - y)
    threshold = 0.05

    songs = (Song.query
             .filter(Song.genre_id == genre_id)
             .filter(Song.happy.between(happy_prob - threshold, happy_prob + threshold))
             .filter(Song.aggressive.between(aggressive_prob - threshold, aggressive_prob + threshold))
             .filter(Song.sad.between(sad_prob - threshold, sad_prob + threshold))
             .filter(Song.calm.between(calm_prob - threshold, calm_prob + threshold))
             .all())

    while len(songs) < 20:
        threshold += 0.01
        songs = (Song.query
                 .filter(Song.genre_id == genre_id)
                 .filter(Song.happy.between(happy_prob - threshold, happy_prob + threshold))
                 .filter(Song.aggressive.between(aggressive_prob - threshold, aggressive_prob + threshold))
                 .filter(Song.sad.between(sad_prob - threshold, sad_prob + threshold))
                 .filter(Song.calm.between(calm_prob - threshold, calm_prob + threshold))
                 .all())

    selected_songs = random.sample(songs, min(len(songs), 20))

    serialized_songs = [{
        'artist_name': song.artist_name,
        'track_name': song.track_name
    } for song in selected_songs]

    return jsonify(serialized_songs)


@app.route('/process_csv', methods=['POST'])
def process_csv_and_push_to_database():

    file = request.files.get('file')

    if file is None or file.filename == '':
        return {'success': False, 'message': 'No file uploaded.'}
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return {'success': False, 'message': f'Invalid file type: {filename}'}

    try:
        temp_file_path = os.path.join(app.config['TEMP_FOLDER'],
                                      f'{os.urandom(16).hex()}.csv')
        file.save(temp_file_path)

        predictions_path = os.path.join(app.config['TEMP_FOLDER'], f'{os.urandom(16).hex()}.csv')
        genres_path = os.path.join(app.config['TEMP_FOLDER'], f'{os.urandom(16).hex()}.csv')
        make_predictions(temp_file_path, predictions_path)
        fetch_genres(predictions_path, genres_path)

        with open(genres_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                artists_list = ast.literal_eval(row['artists'])
                artists = ', '.join(artists_list)
                genre_name = row['genre']

                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.session.add(genre)
                    db.session.commit()

                song = Song(track_name=row['name'], album_name=row['album'], artist_name=artists,
                            aggressive=row['aggressive'], calm=row['calm'],
                            happy=row['happy'], sad=row['sad'], genre_id=genre.id)
                db.session.add(song)

        db.session.commit()
        os.remove(temp_file_path)
        os.remove(predictions_path)
        os.remove(genres_path)

        return {'success': True, 'message': 'Data uploaded and processed successfully.'}

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Error processing CSV: {e}")
        return {'success': False, 'message': 'An error occurred while processing the data.'}


def allowed_file(filename):
    """Checks if the filename extension is allowed."""
    ALLOWED_EXTENSIONS = {'csv'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/get-genres', methods=['GET'])
def get_genres():
    genres = Genre.query.all()
    serialized_genres = [{
        'id': genre.id,
        'name': genre.name
    } for genre in genres]

    return jsonify(serialized_genres)

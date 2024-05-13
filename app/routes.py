from flask import render_template, request, jsonify, Response
from app import app, db
from app.models import Song, Genre
import random
import os
from process_songs import fetch_genres, make_predictions
from werkzeug.utils import secure_filename
import csv
import ast
import logging


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/get-songs', methods=['GET'])
def get_songs():
    genre_id = request.args.get('genre')
    x = float(request.args.get('x'))
    y = float(request.args.get('y'))

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

    while len(songs) < 20 and threshold <= 1:
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
        'track_name': song.track_name,
        'happy_prob': song.happy,
        'aggressive_prob': song.aggressive,
        'sad_prob': song.sad,
        'calm_prob': song.calm,
    } for song in selected_songs]

    return jsonify(serialized_songs)


@app.route('/process_csv', methods=['POST'])
def process_csv_and_push_to_database():
    # logger = logging.getLogger(__name__)
    # logger.setLevel(logging.INFO)
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    file = request.files.get('file')

    # logger.info("File upload in progress...")
    # yield "data: File upload in progress...\n\n"

    if file is None or file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 500
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return jsonify({'error': f'Invalid file type: {filename}'}), 500

    try:

        temp_file_path = os.path.join(app.config['TEMP_FOLDER'],
                                      f'{os.urandom(16).hex()}.csv')
        file.save(temp_file_path)

        get_moods_flag = request.form['get-moods']
        get_genres_flag = request.form['get-genres']

        if get_moods_flag == 'true':
            make_predictions(temp_file_path, temp_file_path)

        if get_genres_flag == 'true':
            genres_path = os.path.join(app.config['TEMP_FOLDER'], f'{os.urandom(16).hex()}.csv')
            fetch_genres(temp_file_path, genres_path)
            temp_file_path = genres_path

        with open(temp_file_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)

            first_row = next(csvreader)

            if get_moods_flag == 'false' and any(
                    col not in first_row for col in ['happy', 'sad', 'calm', 'aggressive']):
                raise Exception('"Predict moods" flag is not set but mood columns are missing in the CSV file.')

            elif get_genres_flag == 'false' and any(col not in first_row for col in ['genre']):
                raise Exception('"Get genres" flag is not set but "genre" column is missing in the CSV file.')

            elif get_genres_flag == 'false' and any(col not in first_row for col in ['name', 'album', 'artists']):
                raise Exception('"name", "album", "artists" columns are missing in the CSV file.')

            csvfile.seek(0)
            next(csvreader)

            for row in csvreader:

                if any(value == '' for value in row.values()):
                    continue

                if get_moods_flag == 'false':
                    try:
                        happy = float(row['happy'])
                        sad = float(row['sad'])
                        calm = float(row['calm'])
                        aggressive = float(row['aggressive'])
                        if happy + sad + calm + aggressive != 1.0:
                            continue
                    except ValueError:
                        continue

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
                # yield f"Added song: {song.artist_name} - {song.track_name} to database. \n"
                # yield "Added song to database. \n"

        db.session.commit()
        remove_temp_files(app.config['TEMP_FOLDER'])
        return jsonify({'message': 'Data uploaded and processed successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Error processing CSV: {e}")
        remove_temp_files(app.config['TEMP_FOLDER'])
        return jsonify({'error': str(e)}), 500


def remove_temp_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        os.remove(file_path)


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

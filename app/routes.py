from flask import render_template, request, jsonify, make_response, redirect, url_for
from app import app, db
from app.models import Song, Genre, Admin
import random
import os
from process_songs import fetch_genres, make_predictions
from werkzeug.utils import secure_filename
import csv
import ast
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies
from datetime import datetime, timedelta


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
@jwt_required(optional=True)
def admin():
    current_user = get_jwt_identity()
    if current_user:
        return render_template('admin.html')
    else:
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            print('Username and password are required')
            return jsonify({'error': 'Username and password are required'}), 400

        admin = Admin.query.filter_by(username=username).first()
        if not admin or not admin.check_password(password):
            print('Invalid username or password')
            return jsonify({'error': 'Invalid username or password'}), 401

        access_token = create_access_token(identity=admin.id)
        response = make_response(jsonify({'message': 'Login successful'}), 200)
        set_access_cookies(response, encoded_access_token=access_token)
        return response
    else:
        if get_jwt_identity():
            return redirect(url_for('admin'))


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


@app.route('/process-csv', methods=['POST'])
@jwt_required()
def process_csv_and_push_to_database():
    file = request.files.get('file')

    if file is None or file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 500
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return jsonify({'error': f'Invalid file type: {filename}'}), 500

    current_user = get_jwt_identity()
    print(current_user)
    if current_user is None:
        print(current_user)
        return jsonify({'error': 'Authorization required.'}), 401
    else:
        try:

            temp_file_path = os.path.join(app.config['TEMP_FOLDER'],
                                          f'{os.urandom(16).hex()}.csv')
            file.save(temp_file_path)

            get_moods_flag = request.form['get-moods']
            get_genres_flag = request.form['get-genres']

            if get_moods_flag == 'true':
                make_predictions(temp_file_path, temp_file_path)

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

                    if get_genres_flag == 'true':
                        genre_name = fetch_genres(row['name'], artists_list[0], row['album'])

                    if not genre_name:
                        continue

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
            remove_temp_files(app.config['TEMP_FOLDER'])
            return jsonify({'message': 'Data uploaded and processed successfully.'}), 200

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f'Error processing CSV: {e}')
            remove_temp_files(app.config['TEMP_FOLDER'])
            return jsonify({'error': str(e)}), 500


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now()
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


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

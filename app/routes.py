from flask import render_template, request, jsonify, make_response, redirect, url_for
from jwt import ExpiredSignatureError
from rq.command import send_stop_job_command
from sqlalchemy import func
from app import app, redis_conn, queue, db
from app.models import Song, Genre, Admin
from app.bg_jobs import process_csv_and_push_to_database_bg
import random
import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, \
    verify_jwt_in_request
from datetime import datetime, timedelta
from rq.job import Job
from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(ExpiredSignatureError)
def handle_expired_error(e):
    return redirect(url_for('login'))


@app.route('/admin')
@jwt_required(optional=True)
def admin():
    current_user = get_jwt_identity()
    if current_user:
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))


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
        try:
            verify_jwt_in_request(optional=True)
            current_user = get_jwt_identity()
            if current_user:
                return redirect(url_for('admin'))
        except ExpiredSignatureError:
            pass
        return render_template('login.html')


@app.route('/get-songs', methods=['GET'])
def get_songs():
    genre_id = request.args.get('genre')
    happy_prob = float(request.args.get('happy_prob'))
    aggressive_prob = float(request.args.get('aggressive_prob'))
    sad_prob = float(request.args.get('sad_prob'))
    calm_prob = float(request.args.get('calm_prob'))

    if abs(happy_prob + sad_prob + calm_prob + aggressive_prob - 1.0) >= 0.01:
        return jsonify({'error': 'The sum of the probabilities is not equal to one'}), 406

    if not (0 <= happy_prob <= 1 and 0 <= sad_prob <= 1 and 0 <= calm_prob <= 1 and 0 <= aggressive_prob <= 1):
        return jsonify({'error': 'One or more probabilities are out of the range between 0 and 1'}), 406

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
        'album_cover': song.album_cover_url,
    } for song in selected_songs]

    return jsonify(serialized_songs)


@app.route('/process-csv', methods=['POST'])
@jwt_required()
def process_csv_and_push_to_database():
    file = request.files.get('file')
    get_moods_flag = request.form['get-moods']
    get_genres_flag = request.form['get-genres']
    get_album_covers_flag = request.form['get-album-covers']

    if file is None or file.filename == '':
        return jsonify({'error': 'No file uploaded.'}), 500
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return jsonify({'error': f'Invalid file type: {filename}'}), 500

    temp_file_path = os.path.join(app.config['TEMP_FOLDER'],
                                  f'{os.urandom(16).hex()}.csv')
    file.save(temp_file_path)

    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({'error': 'Authorization required.'}), 401

    if len(queue) >= app.config['MAX_QUEUE_BG_JOBS']:
        return jsonify({'error': 'Queue full. Please try again later.'}), 503

    job = queue.enqueue(process_csv_and_push_to_database_bg, temp_file_path, get_moods_flag, get_genres_flag,
                        get_album_covers_flag, result_ttl=86400)

    return jsonify({'message': 'Data processing job queued.', 'job_id': job.id}), 202


@app.route('/all-jobs', methods=['GET'])
@jwt_required()
def get_all_jobs():
    queued_job_ids = queue.job_ids
    started_job_registry = StartedJobRegistry(queue=queue)
    active_job_ids = started_job_registry.get_job_ids()
    finished_job_registry = FinishedJobRegistry(queue=queue)
    finished_job_ids = finished_job_registry.get_job_ids()
    failed_job_registry = FailedJobRegistry(queue=queue)
    failed_job_ids = failed_job_registry.get_job_ids()

    all_job_ids = [job_id for job_id in (queued_job_ids + active_job_ids + finished_job_ids + failed_job_ids) if
                   job_id is not None]

    if not all_job_ids:
        return jsonify({'message': 'No jobs found.'}), 200

    all_jobs_info = []
    for job_id in all_job_ids:
        job = Job.fetch(job_id, connection=redis_conn)
        if job_id in failed_job_ids:
            job_info = {
                'id': job.id,
                'status': job.get_status(),
                'created_at': job.created_at.isoformat(),
                'meta': job.meta,
            }
        else:
            job_info = {
                'id': job.id,
                'function': job.func_name,
                'args': job.args,
                'kwargs': job.kwargs,
                'status': job.get_status(),
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'ended_at': job.ended_at.isoformat() if job.ended_at else None,
                'meta': job.meta,
            }
        all_jobs_info.append(job_info)

    return jsonify(all_jobs_info)


@app.route('/delete-job', methods=['DELETE'])
@jwt_required()
def delete_job():
    job_id = request.args.get('job_id')
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        if job.get_status() == 'started':

            if job.func_name == 'app.bg_jobs.process_csv_and_push_to_database_bg':
                temp_file_path = job.args[0]
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            send_stop_job_command(redis_conn, job_id)
            job.delete()
        else:
            job.delete()
        return jsonify({'message': f'Job {job_id} deleted successfully.'}), 200

    except Exception as e:
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


@app.route('/get-all-songs-by-genre', methods=['GET'])
@jwt_required()
def get_songs_by_genre():
    # Fetch songs grouped by genre
    genre_counts = db.session.query(Genre.name, func.count(Song.id)). \
        join(Song, Genre.id == Song.genre_id). \
        group_by(Genre.name). \
        all()

    serialized_genre_counts = [{
        'genre': genre,
        'count': count
    } for genre, count in genre_counts]

    return jsonify(serialized_genre_counts)

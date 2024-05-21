import json
from sqlalchemy.exc import IntegrityError, DataError
from process_songs import fetch_genres, make_predictions, fetch_album_cover
import csv
from rq import get_current_job
import os
from app import app, db
from app.models import Song, Genre


def process_csv_and_push_to_database_bg(temp_file_path, get_moods_flag, get_genres_flag, get_album_covers_flag):
    with app.app_context():
        try:
            job = get_current_job()
            job.meta['progress'] = 0
            job.save_meta()

            # Uncomment if you're running Flask app locally on Windows
            # if os.name == 'posix':
            #    temp_file_path = '/mnt/c' + temp_file_path[2:]
            #    temp_file_path = temp_file_path.replace('\\', '/')

            if get_moods_flag == 'true':
                make_predictions(temp_file_path, temp_file_path)

            with open(temp_file_path, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)
                columns = csvreader.fieldnames

                if columns is None:
                    raise Exception("CSV file is empty or columns could not be determined.")

                if get_moods_flag == 'false' and any(
                        col not in columns for col in ['happy', 'sad', 'calm', 'aggressive']):
                    raise Exception('"Predict moods" flag is not set but mood columns are missing in the CSV file.')

                if get_moods_flag == 'true' and any(col not in columns for col in
                                                    ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                                                     'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                                                     'duration_ms', 'time_signature']):
                    raise Exception('"Predict moods" flag is set but feature columns are missing in the CSV file.')

                if get_genres_flag == 'false' and 'genre' not in columns:
                    raise Exception('"Get genres" flag is not set but "genre" column is missing in the CSV file.')

                if any(col not in columns for col in ['name', 'album', 'artists']):
                    raise Exception('"name", "album", "artists" columns are missing in the CSV file.')

                total_rows = len(list(csvreader))
                print(total_rows)
                processed_rows = 0
                csvfile.seek(0)
                next(csvreader)

                for row in csvreader:

                    processed_rows += 1
                    job.meta['progress'] = processed_rows / total_rows * 100
                    job.save_meta()

                    if any(value == '' and key != 'album_cover' for key, value in row.items()):
                        app.logger.warning(f"Skipping row with empty values (except album_cover): {row}")
                        continue

                    if get_moods_flag == 'false':
                        try:
                            happy = float(row['happy'])
                            sad = float(row['sad'])
                            calm = float(row['calm'])
                            aggressive = float(row['aggressive'])
                            if abs(happy + sad + calm + aggressive - 1.0) >= 0.01:
                                app.logger.warning(f"Skipping row with invalid mood sum: {row}")
                                continue
                        except ValueError:
                            app.logger.warning(f"Skipping row with invalid mood values: {row}")
                            continue

                    artists_list = json.loads(row['artists'])
                    artists = ', '.join(artists_list)

                    if get_genres_flag == 'true':
                        genre_name = fetch_genres(row['name'], artists_list[0], row['album'])
                        if not genre_name:
                            app.logger.warning(f"Skipping row due to genre fetch failure: {row}")
                            continue
                    else:
                        genre_name = row['genre']

                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        try:
                            db.session.add(genre)
                            db.session.commit()
                        except IntegrityError:
                            db.session.rollback()
                            app.logger.warning(f"Duplicate genre found, using existing genre: {genre_name}")
                            genre = Genre.query.filter_by(name=genre_name).first()

                    if get_album_covers_flag == 'true':
                        album_cover_url = fetch_album_cover(artists_list[0], row['album'])
                    elif 'album_cover' in columns:
                        album_cover_url = row['album_cover']
                    else:
                        album_cover_url = ''

                    song = Song(track_name=row['name'], album_name=row['album'], artist_name=artists,
                                aggressive=row['aggressive'], calm=row['calm'],
                                happy=row['happy'], sad=row['sad'], genre_id=genre.id, album_cover_url=album_cover_url)

                    try:
                        db.session.add(song)
                        db.session.commit()
                    except DataError as e:
                        db.session.rollback()
                        app.logger.warning(
                            f"Skipping row due to data error (possibly field too long): {row}. Error: {e}")
                        continue
                    except IntegrityError:
                        db.session.rollback()
                        app.logger.warning(f"Skipping insertion of duplicate song: {song}")
                        continue

            if temp_file_path:
                os.remove(temp_file_path)

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f'Error processing CSV: {e}')
            if temp_file_path:
                os.remove(temp_file_path)
            pass

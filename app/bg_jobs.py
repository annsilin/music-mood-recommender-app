from sqlalchemy.exc import IntegrityError

from process_songs import fetch_genres, make_predictions, fetch_album_cover
import csv
import ast
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

            if os.name == 'posix':
                temp_file_path = '/mnt/c' + temp_file_path[2:]
                temp_file_path = temp_file_path.replace('\\', '/')

            if get_moods_flag == 'true':
                make_predictions(temp_file_path, temp_file_path)

            with open(temp_file_path, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)

                total_rows = len(list(csvreader))
                processed_rows = 0

                csvfile.seek(0)
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
                            app.logger.warning(f"Skipping insertion of duplicate genre: {genre}")
                            continue

                    if get_album_covers_flag == 'true':
                        album_cover_url = fetch_album_cover(artists_list[0], row['album'])
                    else:
                        album_cover_url = row['album_cover']

                    song = Song(track_name=row['name'], album_name=row['album'], artist_name=artists,
                                aggressive=row['aggressive'], calm=row['calm'],
                                happy=row['happy'], sad=row['sad'], genre_id=genre.id, album_cover_url=album_cover_url)
                    try:
                        db.session.add(song)
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        app.logger.warning(f"Skipping insertion of duplicate song: {song}")
                        continue

                    processed_rows += 1
                    job.meta['progress'] = processed_rows / total_rows * 100
                    job.save_meta()

            if temp_file_path:
                os.remove(temp_file_path)

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f'Error processing CSV: {e}')
            if temp_file_path:
                os.remove(temp_file_path)
            pass

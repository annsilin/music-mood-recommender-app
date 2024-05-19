import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'you-will-never-guess'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_CSRF_HEADER_NAME = 'X-CSRF-TOKEN'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://username:password@localhost:5432/yourdatabase'
    FLASK_RUN_PORT = int(os.environ.get('FLASK_RUN_PORT', 5000))
    ALLOWED_EXTENSIONS = {'csv'}
    TEMP_FOLDER = os.path.join(basedir, 'process_songs/temp_files')
    MAX_QUEUE_BG_JOBS = 10

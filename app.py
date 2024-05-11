import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import Song, Genre


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'Song': Song, 'Genre': Genre}


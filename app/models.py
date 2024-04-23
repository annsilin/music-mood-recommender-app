import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Song(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    artist_name: so.Mapped[str] = so.mapped_column(sa.String(255))
    album_name: so.Mapped[str] = so.mapped_column(sa.String(255))
    track_name: so.Mapped[str] = so.mapped_column(sa.String(255))
    happy: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    aggressive: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    sad: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    calm: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    genre_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('genre.id'))

    def __repr__(self):
        return f"{self.artist_name} - {self.track_name}"


class Genre(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64))

    def __repr__(self):
        return f"{self.name}"

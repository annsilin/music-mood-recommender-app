import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional


class Song(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    artist_name: so.Mapped[str] = so.mapped_column(sa.String(512))
    album_name: so.Mapped[str] = so.mapped_column(sa.String(255))
    track_name: so.Mapped[str] = so.mapped_column(sa.String(512))
    happy: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    aggressive: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    sad: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    calm: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    genre_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('genre.id'))
    album_cover_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255), nullable=True)

    __table_args__ = (
        sa.UniqueConstraint('artist_name', 'album_name', 'track_name', name='uq_artist_album_track'),
    )

    def __repr__(self):
        return f"{self.artist_name} - {self.track_name}"


class Genre(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64))

    __table_args__ = (
        sa.UniqueConstraint('name', name='uq_genre'),
    )

    def __repr__(self):
        return f"{self.name}"


class Admin(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint('username', name='uq_username'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

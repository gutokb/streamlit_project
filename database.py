"""SQLite storage for movie ratings. One row per movie."""

import sqlite3
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "movies.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS ratings (
    movie_id    INTEGER PRIMARY KEY,
    title       TEXT    NOT NULL,
    year        TEXT,
    poster_path TEXT,
    overview    TEXT,
    genres      TEXT,
    rating      REAL    NOT NULL,
    review      TEXT,
    watched_on  TEXT,
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(SCHEMA)


def save_rating(
    movie_id: int,
    title: str,
    year: str,
    poster_path: str | None,
    overview: str,
    genres: str,
    rating: float,
    review: str,
    watched_on: date | None,
) -> None:
    """Insert a rating, or update it if the movie was already rated."""
    now = datetime.now().isoformat(timespec="seconds")
    watched = watched_on.isoformat() if watched_on else None
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO ratings (movie_id, title, year, poster_path, overview,
                                 genres, rating, review, watched_on,
                                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(movie_id) DO UPDATE SET
                title       = excluded.title,
                year        = excluded.year,
                poster_path = excluded.poster_path,
                overview    = excluded.overview,
                genres      = excluded.genres,
                rating      = excluded.rating,
                review      = excluded.review,
                watched_on  = excluded.watched_on,
                updated_at  = excluded.updated_at
            """,
            (
                movie_id, title, year, poster_path, overview, genres,
                rating, review, watched, now, now,
            ),
        )


def get_rating(movie_id: int) -> sqlite3.Row | None:
    with _connect() as conn:
        cursor = conn.execute("SELECT * FROM ratings WHERE movie_id = ?", (movie_id,))
        return cursor.fetchone()


def list_ratings(sort_by: str = "updated_at") -> list[sqlite3.Row]:
    """All rated movies. `sort_by` is validated against a fixed whitelist."""
    columns = {
        "updated_at": "updated_at DESC",
        "rating": "rating DESC, title ASC",
        "title": "title COLLATE NOCASE ASC",
        "year": "year DESC, title ASC",
        "watched_on": "watched_on DESC, updated_at DESC",
    }
    order = columns.get(sort_by, columns["updated_at"])
    with _connect() as conn:
        return conn.execute(f"SELECT * FROM ratings ORDER BY {order}").fetchall()


def delete_rating(movie_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM ratings WHERE movie_id = ?", (movie_id,))


def count_ratings() -> int:
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]


def average_rating() -> float | None:
    with _connect() as conn:
        return conn.execute("SELECT AVG(rating) FROM ratings").fetchone()[0]

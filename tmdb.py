"""Thin client for the TMDB (The Movie Database) REST API."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
TIMEOUT = 10


class TMDBError(RuntimeError):
    """Raised when TMDB is unreachable or rejects the request."""


def _api_key() -> str:
    key = os.getenv("TMDB_API_KEY", "").strip()
    if not key:
        raise TMDBError(
            "No TMDB API key found. Copy .env.example to .env and set "
            "TMDB_API_KEY=your_key (get one free at themoviedb.org)."
        )
    return key


def _get(path: str, **params) -> dict:
    params["api_key"] = _api_key()
    try:
        response = requests.get(f"{BASE_URL}{path}", params=params, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise TMDBError(f"Could not reach TMDB: {exc}") from exc

    if response.status_code == 401:
        raise TMDBError("TMDB rejected the API key (401). Check TMDB_API_KEY in .env.")
    if not response.ok:
        raise TMDBError(f"TMDB returned {response.status_code}: {response.text[:200]}")

    return response.json()


def search_movies(query: str, page: int = 1) -> list[dict]:
    """Search movies by title, most relevant first."""
    query = query.strip()
    if not query:
        return []
    data = _get("/search/movie", query=query, page=page, include_adult="false")
    return data.get("results", [])


def get_movie(movie_id: int) -> dict:
    """Full details for one movie, including genres and runtime."""
    return _get(f"/movie/{movie_id}")


def poster_url(poster_path: str | None, size: str = "w342") -> str | None:
    """Build a full poster URL, or None when the movie has no poster."""
    if not poster_path:
        return None
    return f"{IMAGE_BASE_URL}/{size}{poster_path}"


def release_year(movie: dict) -> str:
    """Four-digit release year as a string, or '' when unknown."""
    return (movie.get("release_date") or "")[:4]


def genre_names(movie: dict) -> str:
    """Comma-separated genre names from a movie *details* payload."""
    return ", ".join(genre["name"] for genre in movie.get("genres", []))

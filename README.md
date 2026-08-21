# 🎬 Movie Diary

A small Streamlit app to search movies on [TMDB](https://www.themoviedb.org/), rate the
ones you've seen, and keep your ratings in a local SQLite database.

- **Search & Rate** — search by title, see poster / synopsis / genres, give a 0.5–10
  score with notes and a watch date.
- **My Ratings** — your whole list, sortable, with edit and delete.

## Setup

### 1. Get a TMDB API key (free)

1. Create an account at [themoviedb.org](https://www.themoviedb.org/signup).
2. Go to **Settings → API** and request a key (choose *Developer*, personal use).
3. Copy the **API Key (v3 auth)** value.

### 2. Configure the key

```powershell
Copy-Item .env.example .env
```

Then open `.env` and replace `your_tmdb_api_key_here` with your key. `.env` is
gitignored, so the key never gets committed.

### 3. Virtual environment

The `.venv/` folder is already created with everything installed. If you ever need to
rebuild it:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell blocks the activate script, run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal first.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

The app opens at http://localhost:8501. Without activating the venv, this also works:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

## Files

| File | What it does |
| --- | --- |
| `app.py` | Streamlit UI — tabs, search results, rating form, list view |
| `tmdb.py` | TMDB API client (search, details, poster URLs) |
| `database.py` | SQLite schema and queries for `movies.db` |
| `.env` | Your TMDB API key (not committed) |
| `movies.db` | Your ratings — created on first run, not committed |

## Notes

- API responses are cached for an hour, so repeated searches don't burn requests.
- One row per movie: rating the same film twice updates the existing entry.
- To start over, just delete `movies.db`.

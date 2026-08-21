"""Movie Diary — search movies on TMDB, rate the ones you've seen, keep the list."""

from datetime import date

import streamlit as st

import database as db
import tmdb

st.set_page_config(page_title="Movie Diary", page_icon="🎬", layout="wide")

db.init_db()


# --- helpers ---------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def search_movies(query: str) -> list[dict]:
    return tmdb.search_movies(query)


@st.cache_data(ttl=3600, show_spinner=False)
def get_movie(movie_id: int) -> dict:
    return tmdb.get_movie(movie_id)


def stars(rating: float) -> str:
    """Render a 0-10 rating as five stars, e.g. 7.5 -> '★★★☆☆'."""
    filled = int(round(rating / 2))
    return "★" * filled + "☆" * (5 - filled)


def poster(poster_path: str | None, width: int) -> None:
    url = tmdb.poster_url(poster_path)
    if url:
        st.image(url, width=width)
    else:
        st.markdown(
            f"<div style='width:{width}px;height:{int(width * 1.5)}px;"
            "display:flex;align-items:center;justify-content:center;"
            "border:1px dashed rgba(128,128,128,.5);border-radius:8px;"
            "font-size:2rem;'>🎬</div>",
            unsafe_allow_html=True,
        )


def clear_state(*keys: str) -> None:
    for key in keys:
        st.session_state.pop(key, None)


# --- search & rate ---------------------------------------------------------

def rating_form(movie: dict) -> None:
    """Detail panel + save form for one movie (used for new and edited ratings)."""
    existing = db.get_rating(movie["id"])
    year = tmdb.release_year(movie)

    left, right = st.columns([1, 3])
    with left:
        poster(movie.get("poster_path"), width=200)
    with right:
        st.subheader(f"{movie['title']} {f'({year})' if year else ''}")
        meta = [tmdb.genre_names(movie)]
        if movie.get("runtime"):
            meta.append(f"{movie['runtime']} min")
        if movie.get("vote_average"):
            meta.append(f"TMDB {movie['vote_average']:.1f}/10")
        st.caption(" · ".join(part for part in meta if part))
        st.write(movie.get("overview") or "_No synopsis available._")

    with st.form(f"rate_{movie['id']}"):
        col1, col2 = st.columns([2, 1])
        with col1:
            rating = st.slider(
                "Your rating",
                min_value=0.5,
                max_value=10.0,
                step=0.5,
                value=float(existing["rating"]) if existing else 7.0,
            )
        with col2:
            watched_on = st.date_input(
                "Watched on",
                value=(
                    date.fromisoformat(existing["watched_on"])
                    if existing and existing["watched_on"]
                    else date.today()
                ),
                max_value=date.today(),
            )
        review = st.text_area(
            "Notes",
            value=existing["review"] if existing else "",
            placeholder="What did you think of it?",
        )

        if st.form_submit_button("💾 Save rating", type="primary"):
            db.save_rating(
                movie_id=movie["id"],
                title=movie["title"],
                year=year,
                poster_path=movie.get("poster_path"),
                overview=movie.get("overview") or "",
                genres=tmdb.genre_names(movie),
                rating=rating,
                review=review.strip(),
                watched_on=watched_on,
            )
            clear_state("selected_movie", "editing")
            st.success(f"Saved **{movie['title']}** — {rating}/10 {stars(rating)}")
            st.rerun()


def search_tab() -> None:
    query = st.text_input(
        "Search for a movie",
        placeholder="e.g. Blade Runner",
        label_visibility="collapsed",
    )

    if st.session_state.get("selected_movie"):
        if st.button("← Back to results"):
            clear_state("selected_movie")
            st.rerun()
        try:
            rating_form(get_movie(st.session_state["selected_movie"]))
        except tmdb.TMDBError as exc:
            st.error(str(exc))
        return

    if not query.strip():
        st.info("Search TMDB by title, then pick a movie to rate it.")
        return

    try:
        results = search_movies(query)
    except tmdb.TMDBError as exc:
        st.error(str(exc))
        return

    if not results:
        st.warning(f"No movies found for “{query}”.")
        return

    st.caption(f"{len(results)} result(s)")
    for movie in results:
        with st.container(border=True):
            left, right = st.columns([1, 5])
            with left:
                poster(movie.get("poster_path"), width=110)
            with right:
                year = tmdb.release_year(movie)
                st.markdown(f"**{movie['title']}** {f'({year})' if year else ''}")
                rated = db.get_rating(movie["id"])
                if rated:
                    st.caption(f"You rated this {rated['rating']}/10 {stars(rated['rating'])}")
                overview = movie.get("overview") or "No synopsis available."
                st.write(overview[:280] + ("…" if len(overview) > 280 else ""))
                if st.button(
                    "✏️ Update rating" if rated else "⭐ Rate this",
                    key=f"pick_{movie['id']}",
                ):
                    st.session_state["selected_movie"] = movie["id"]
                    st.rerun()


# --- my ratings ------------------------------------------------------------

def ratings_tab() -> None:
    total = db.count_ratings()
    if not total:
        st.info("You haven't rated anything yet. Head to **Search & Rate** to start.")
        return

    col1, col2, col3 = st.columns([1, 1, 2])
    col1.metric("Movies rated", total)
    col2.metric("Average score", f"{db.average_rating():.1f}")
    sort_by = col3.selectbox(
        "Sort by",
        options=["updated_at", "rating", "title", "year", "watched_on"],
        format_func={
            "updated_at": "Recently updated",
            "rating": "Highest rated",
            "title": "Title (A–Z)",
            "year": "Release year",
            "watched_on": "Recently watched",
        }.get,
    )

    for row in db.list_ratings(sort_by):
        movie_id = row["movie_id"]
        with st.container(border=True):
            left, right = st.columns([1, 5])
            with left:
                poster(row["poster_path"], width=110)
            with right:
                header = f"**{row['title']}**"
                if row["year"]:
                    header += f" ({row['year']})"
                st.markdown(f"{header} — {row['rating']}/10 {stars(row['rating'])}")
                caption = [row["genres"]]
                if row["watched_on"]:
                    caption.append(f"watched {row['watched_on']}")
                st.caption(" · ".join(part for part in caption if part))
                if row["review"]:
                    st.write(row["review"])

                edit_col, delete_col, _ = st.columns([1, 1, 3])
                if edit_col.button("✏️ Edit", key=f"edit_{movie_id}"):
                    st.session_state["editing"] = movie_id
                    st.rerun()
                if delete_col.button("🗑️ Delete", key=f"del_{movie_id}"):
                    st.session_state["pending_delete"] = movie_id
                    st.rerun()

            if st.session_state.get("pending_delete") == movie_id:
                st.warning(f"Remove **{row['title']}** from your list?")
                yes_col, no_col, _ = st.columns([1, 1, 4])
                if yes_col.button("Yes, delete", key=f"yes_{movie_id}", type="primary"):
                    db.delete_rating(movie_id)
                    clear_state("pending_delete", "editing")
                    st.rerun()
                if no_col.button("Cancel", key=f"no_{movie_id}"):
                    clear_state("pending_delete")
                    st.rerun()

            if st.session_state.get("editing") == movie_id:
                st.divider()
                try:
                    rating_form(get_movie(movie_id))
                except tmdb.TMDBError as exc:
                    st.error(str(exc))
                if st.button("Cancel edit", key=f"canceledit_{movie_id}"):
                    clear_state("editing")
                    st.rerun()


# --- layout ----------------------------------------------------------------

st.title("🎬 Movie Diary")
st.caption("Search TMDB, rate what you've seen, and keep your own little archive.")

search, ratings = st.tabs(["🔎 Search & Rate", "⭐ My Ratings"])
with search:
    search_tab()
with ratings:
    ratings_tab()

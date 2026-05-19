import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPE = "user-library-read"
LIMIT = 50

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))


def fetch_all_liked_songs() -> list[dict]:
    """Fetch all liked songs."""

    # 1. Paginate through all liked songs
    all_items = []
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=LIMIT, offset=offset)
        items = results["items"]
        if not items:
            break
        all_items.extend(items)
        offset += LIMIT
    print(f"Fetched {len(all_items)} liked songs")

    # 2. Build song objects
    songs = []
    for item in all_items:
        track = item["track"]
        songs.append({
            "id":           track["id"],
            "name":         track["name"],
            "artist":       ", ".join(a["name"] for a in track["artists"]),
            "artist_ids":   [a["id"] for a in track["artists"]],
            "album":        track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "duration_ms":  track["duration_ms"],
            "uri":          track["uri"],
            "added_at":     item["added_at"],
        })

    print(f"Built {len(songs)} songs")
    return songs


def save_to_json(songs: list[dict], filename: str = "liked_songs.json") -> None:
    """Save songs list to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(songs)} songs to {filename}")


if __name__ == "__main__":
    songs = fetch_all_liked_songs()
    save_to_json(songs)

    print("\nFirst 5 songs:")
    for s in songs[:5]:
        print(f"  {s['name']} — {s['artist']} ({s['release_date'][:4]})")
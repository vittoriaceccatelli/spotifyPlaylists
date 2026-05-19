import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

SCOPE = "user-library-read playlist-modify-public playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))


def load_songs(filename: str = "liked_songs.json") -> list[dict]:
    with open(filename, "r", encoding="utf-8") as f:
        songs = json.load(f)
    print(f"Loaded {len(songs)} songs")
    return songs


def group_by_decade(songs: list[dict]) -> dict[str, list[str]]:
    decades = defaultdict(list)

    for song in songs:
        release_date = song.get("release_date", "")
        if not release_date:
            decades["Unknown"].append(song["uri"])
            continue

        try:
            year = int(release_date[:4])
            decade = (year // 10) * 10
            decades[f"{decade}s"].append(song["uri"])
        except ValueError:
            decades["Unknown"].append(song["uri"])

    for decade, uris in sorted(decades.items()):
        print(f"  {decade}: {len(uris)} songs")

    return decades


def create_playlist(name: str, uris: list[str]) -> str:
    user_id = sp.current_user()["id"]
    user = sp.current_user()
    print(user["display_name"], user["id"])

    playlist = sp.current_user_playlist_create(
        name=name,
        public=False,
        description=f"Liked songs from the {name} — created by spotify-order"
    )    
    playlist_id = playlist["id"]

    # Add tracks in batches of 100 (Spotify limit)
    for i in range(0, len(uris), 100):
        batch = uris[i:i + 100]
        sp.playlist_add_items(playlist_id, batch)

    return playlist["external_urls"]["spotify"]


def create_decade_playlists(songs: list[dict]) -> None:
    print("\nGrouping songs by decade...")
    decades = group_by_decade(songs)

    print("\nCreating playlists...")
    for decade, uris in sorted(decades.items()):
        if decade == "Unknown":
            name = "Unknown Decade"
        else:
            name = f"{decade}"

        print(f"  Creating '{name}' ({len(uris)} songs)...", end=" ")
        url = create_playlist(name, uris)
        print(f"done → {url}")


if __name__ == "__main__":
    songs = load_songs("liked_songs.json")
    create_decade_playlists(songs)
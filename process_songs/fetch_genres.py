import ast
import pylast
import logging
import yaml
import csv
from collections import OrderedDict
import os


current_directory = os.path.dirname(os.path.abspath(__file__))
WHITELIST_FILE = os.path.join(current_directory, 'genres.txt')
GENRE_TREE_FILE = os.path.join(current_directory, 'genres-tree.yaml')


def load_whitelist():
    """Loads genres from a whitelist file."""
    whitelist = set()
    with open(WHITELIST_FILE, "r") as f:
        for line in f:
            line = line.strip().lower()
            if line and not line.startswith("#"):
                whitelist.add(line)
    return whitelist


def load_genre_tree():
    """Loads the genre tree from a YAML file."""
    with open(GENRE_TREE_FILE, "r", encoding="utf-8") as f:
        genres_tree = yaml.safe_load(f)
    branches = []
    flatten_tree(genres_tree, [], branches)
    return branches


def flatten_tree(elem, path, branches):
    """Flattens nested lists/dictionaries into lists of strings (branches)."""
    if not path:
        path = []
    if isinstance(elem, dict):
        for k, v in elem.items():
            flatten_tree(v, path + [k], branches)
    elif isinstance(elem, list):
        for sub in elem:
            flatten_tree(sub, path, branches)
    else:
        branches.append(path + [str(elem)])


def find_parents(candidate, branches):
    """Finds parent genres of a given genre, ordered from closest to furthest."""
    for branch in branches:
        try:
            idx = branch.index(candidate)
            return list(reversed(branch[:idx + 1]))
        except ValueError:
            continue
    return [candidate]


def is_allowed_genre(genre, whitelist):
    """Determines if a genre is allowed based on the whitelist."""
    return genre is not None and (not whitelist or genre in whitelist)


def resolve_genres(tags, whitelist=None, genre_tree=None, count=1, separator=", "):
    """
    Resolves genres from a list of tags considering whitelist and genre tree.

    Args:
        tags: List of genre tags.
        whitelist: Set of allowed genres (optional).
        genre_tree: List of branches representing genre hierarchy (optional).
        count: Maximum number of genres to return (default: 1).
        separator: String separator to join multiple genres (default: ", ").
    """
    genres = []
    for tag in tags:
        # Extend list to consider tag's parents in the genre tree
        all_tags = [tag]
        if whitelist:
            parents = [
                x for x in find_parents(tag, genre_tree) if is_allowed_genre(x, whitelist)
            ]
        else:
            parents = [find_parents(tag, genre_tree)[-1]]
        all_tags.extend(parents)

        # Stop if we have enough genres already
        if len(genres) >= count:
            break

        all_tags = list(OrderedDict.fromkeys(all_tags))

        # Filter and format allowed genres
        genres.extend(
            [t.lower() for t in all_tags if is_allowed_genre(t, whitelist) and t.lower() not in genres]
        )

    # Limit genres to count and join with separator
    return separator.join(genres[:count])


def fetch_genre_from_lastfm(network, artist_name, track_name, album_name, whitelist, genre_tree, min_weight=1):
    """Fetches the genre for a song from Last.fm track tags."""
    try:
        track = network.get_track(artist_name, track_name)
        tags = track.get_top_tags()
        tags = [tag for tag in tags if int(tag.weight) >= min_weight]
        tags.sort(key=lambda x: int(x.weight), reverse=True)
        tag_names = [tag.item.name.lower() for tag in tags]
        # Resolve Last.fm tags into genres based on whitelist and genre tree
        genres = resolve_genres(tag_names, whitelist, genre_tree)

        if len(genres) < 1:
            # Fetch tags from album
            album = network.get_album(artist_name, album_name)
            album_tags = album.get_top_tags()
            album_tags = [tag for tag in album_tags if int(tag.weight) >= min_weight]
            album_tags.sort(key=lambda x: int(x.weight), reverse=True)
            album_tag_names = [tag.item.name.lower() for tag in album_tags]
            genres = resolve_genres(album_tag_names, whitelist, genre_tree)

        if len(genres) < 1:
            # Fetch tags from artist
            artist = network.get_artist(artist_name)
            artist_tags = artist.get_top_tags()
            artist_tags = [tag for tag in artist_tags if int(tag.weight) >= min_weight]
            artist_tags.sort(key=lambda x: int(x.weight), reverse=True)
            artist_tag_names = [tag.item.name.lower() for tag in artist_tags]
            genres = resolve_genres(artist_tag_names, whitelist, genre_tree)

        return genres if len(genres) > 0 else None

    except pylast.PyLastError as e:
        logging.warning(f"Error fetching genres from Last.fm: {e}")
        return None


def fetch_genres_from_csv_helper(network, filename, output_filename, whitelist, genre_tree):
    """
    Fetches genres from Last.fm for songs in a CSV and writes to a new CSV.

    Args:
        filename: Path to the input CSV file.
        output_filename: Path to the output CSV file.
        whitelist: Set of allowed genres (optional).
        genre_tree: List of branches representing genre hierarchy.
    """
    with open(filename, 'r', encoding='utf-8') as csvfile, open(output_filename, 'w', newline='',
                                                                encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)

        first_row = next(reader)
        if any(col not in first_row for col in ['name', 'album', 'artists']):
            raise Exception('"name", "album", "artists" columns are missing in the CSV file.')

        csvfile.seek(0)
        next(reader)

        writer = csv.DictWriter(outfile, fieldnames=list(reader.fieldnames) + ['genre'])
        writer.writeheader()

        for row in reader:
            artists_list_str = row['artists']
            artists_list = ast.literal_eval(artists_list_str) if artists_list_str else []
            artist_name = artists_list[0] if artists_list else None

            track_name = row['name'] if row['name'] else None
            album_name = row['album'] if row['album'] else None
            print(artist_name, track_name)
            # Pass whitelist and genre_tree if provided for genre resolution
            genres = fetch_genre_from_lastfm(network, artist_name, track_name, album_name, whitelist=whitelist, genre_tree=genre_tree)
            if genres is not None:  # Only write the row if genres are not None
                row['genre'] = genres
                writer.writerow(row)


def initialize_lastfm_network():
    api_key = os.environ.get("LASTFM_API_KEY")
    api_secret = os.environ.get("LASTFM_API_SECRET")

    if api_key is None or api_secret is None:
        raise ValueError("LASTFM_API_KEY and LASTFM_API_SECRET must be provided as OS environment variables.")

    return pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)


def fetch_genres_from_csv(input_path, output_path):
    whitelist = load_whitelist()
    genre_tree = load_genre_tree()

    network = initialize_lastfm_network()

    fetch_genres_from_csv_helper(network, input_path, output_path, whitelist, genre_tree)


def fetch_genres(track_name, artist_name, album_name):
    whitelist = load_whitelist()
    genre_tree = load_genre_tree()

    network = initialize_lastfm_network()

    genres = fetch_genre_from_lastfm(network, artist_name, track_name, album_name, whitelist=whitelist,
                                     genre_tree=genre_tree)

    return genres

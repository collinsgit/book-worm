"""Helper functions to decorate book loading and save locally."""
import os
import pickle
import shutil
from functools import wraps
from typing import Callable, Optional

from book_worm.book import Book

CACHE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cache")


def cache_book(function_cache_name: str) -> Callable:
    def decorator(f: Callable[[str], Book]) -> Callable:
        @wraps(f)
        def wrapper(
            title: str, *args, override_cache_name: Optional[str] = None, **kwargs
        ):
            # allow cache name to be overwritten on load_book call, get title mapping
            cache_name = override_cache_name or function_cache_name
            title_map_path, title_map = _get_title_map(cache_name)

            # check if book is cached (title will be in map)
            if title in title_map:
                book_path = title_map[title]
                # the title mapping could be pointing to the true name on the book source
                if book_path in title_map:
                    book_path = title_map[book_path]

                return Book.parse_file(book_path, allow_pickle=True)

            # run actual function if not cached
            book = f(title, *args, **kwargs)
            book_path = os.path.join(
                CACHE_DIR, cache_name, f"{_title_to_filename(book.title)}.pkl"
            )

            # add title mapping
            if title != book.title:
                title_map[title] = book.title
            title_map[book.title] = book_path

            # make dirs if they don't exist
            os.makedirs(CACHE_DIR, exist_ok=True)
            os.makedirs(os.path.join(CACHE_DIR, cache_name), exist_ok=True)

            # write the updated title map and the book object
            pickle.dump(title_map, open(title_map_path, "wb"))
            pickle.dump(book.dict(), open(book_path, "wb"))

            return book

        return wrapper

    return decorator


def _title_to_filename(title: str) -> str:
    """Formats a title to be a safe filename.

    Strips down to alphanumeric chars and replaces spaces with underscores.
    """
    return "".join(c for c in title if c.isalnum() or c == " ").replace(" ", "_")


def _get_title_map(cache_name: str) -> tuple[str, dict[str, str]]:
    """Load the map from titles to book files.

    Creates a dict if the file doesn't exist.
    """
    title_map_path = os.path.join(CACHE_DIR, f"{cache_name}_map.pkl")

    # load or create a new dict
    if os.path.exists(title_map_path):
        title_map: dict[str, str] = pickle.load(open(title_map_path, "rb"))
    else:
        title_map = {}

    return title_map_path, title_map


def clear_cache(cache_name: str):
    """Clear the title map and all saved books for a named cache."""
    # delete the title map
    title_map_path = os.path.join(CACHE_DIR, f"{cache_name}_map.pkl")
    if os.path.exists(title_map_path):
        os.remove(title_map_path)

    # delete the directory of books
    named_cache_dir = os.path.join(CACHE_DIR, cache_name)
    if os.path.exists(named_cache_dir):
        shutil.rmtree(named_cache_dir)

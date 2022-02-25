"""Tests for the book loading and caching utils."""
import os

import pytest

from book_worm.book import Book
from book_worm.sources import book_caching, project_gutenburg

# any book should be far more than 1000 characters
MIN_TEXT_SIZE = 1000


def test_book_cache():
    temp_cache = "temp-cache"
    title = "Alice in Wonderland"
    # query for book
    project_gutenburg.find_book(title, override_cache_name=temp_cache)

    # confirm the mapping is made
    _, title_map = book_caching._get_title_map(temp_cache)
    assert title in title_map

    # confirm the book is cached
    path = title_map[title]
    if path in title_map:
        path = title_map[path]
    assert os.path.exists(path)

    # query again to make sure cache retrieval has no errors
    project_gutenburg.find_book(title, override_cache_name=temp_cache)

    book_caching.clear_cache(temp_cache)


class TestGutenburg:
    temp_cache = "gutenburg-temp"

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        # clean up cache created during testing
        yield
        book_caching.clear_cache(self.temp_cache)

    def test_frankenstein(self):
        # test that the book can be found, with the expected fields
        book: Book = project_gutenburg.find_book(
            "Frankenstein", override_cache_name=self.temp_cache
        )

        assert len(book.text) > MIN_TEXT_SIZE
        assert book.author == "Mary Wollstonecraft Shelley"
        assert book.title == "Frankenstein; Or, The Modern Prometheus"

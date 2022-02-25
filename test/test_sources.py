from book_worm.book import Book
from book_worm.sources import project_gutenburg

# any book should be far more than 1000 characters
MIN_TEXT_SIZE = 1000


class TestGutenburg:
    def test_frankenstein(self):
        book: Book = project_gutenburg.find_book("Frankenstein")

        assert len(book.text) > MIN_TEXT_SIZE
        assert book.author == "Mary Wollstonecraft Shelley"
        assert book.title == "Frankenstein; Or, The Modern Prometheus"

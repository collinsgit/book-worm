"""Top level file for running examples."""


if __name__ == "__main__":
    from book_worm.sources.book_caching import clear_cache
    from book_worm.sources.project_gutenburg import find_book

    book = find_book("Frankenstein")
    print(book.title)
    book2 = find_book("Frankenstein")
    print(book.author)
    clear_cache("gutenburg")

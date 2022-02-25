"""Utils to scrape book data (particularly a book's text) from Project Gutenburg.

Makes use of basic web scraping to attempt to infer the book from the given title.
"""
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from book_worm.book import Book

_GUTENBURG_URL = "https://www.gutenberg.org"
_BOOK_PAGE_PATTERN = r"/ebooks/(\d+)"


def find_book(title: str) -> Book:
    """Scrapes Project Gutenburg to get named book.

    Uses the website's query tool to guess the desired book from the given title and
    downloads the associated plain text copy of the book.
    """
    # load Project Gutenburg's query page for the given title
    search_url = f"{_GUTENBURG_URL}/ebooks/search/"
    params = {"query": title, "submit_search": "Search"}
    r = requests.get(search_url, params=params)
    html = BeautifulSoup(r.text, "html.parser")

    # isolate the list of book results and take the first
    results_list = html.find("ul", class_="results")
    first_result = results_list.find("li", class_="booklink")

    # grab the title and authoer info
    title = first_result.find("span", class_="title").text
    author = first_result.find("span", class_="subtitle").text

    # iterate through all links in the book result HTML
    # if one goes to a /ebooks/{id} page, grab that book ID
    links = first_result.find_all("a")
    book_id: Optional[str] = None
    for link in links:
        if "href" in link.attrs:
            m = re.match(_BOOK_PAGE_PATTERN, link["href"])
            if m:
                book_id = m.group(1)

    assert book_id is not None, f"Could not infer eBook ID for '{title}'"

    text = _find_book_text(book_id)

    return Book(title, text, author=author)


def _find_book_text(book_id: str) -> str:
    """Given a book's Project Gutenburg ID, finds and downloads the plain text file."""
    # load the html of the book's info page
    r = requests.get(f"{_GUTENBURG_URL}/ebooks/{book_id}")
    html = BeautifulSoup(r.text, "html.parser")

    # find the table of downloads and list all download links
    file_table = html.find("table", class_="files")
    files = file_table.find_all("a", class_="link")

    # take the first file that is plaintext
    file_path: Optional[str] = None
    for file in files:
        if "type" in file.attrs and file["type"].split(";")[0] == "text/plain":
            file_path = file["href"]
            break

    assert (
        file_path is not None
    ), f"Could not infer text file location for book with ID '{book_id}'"

    # download the text from the inferred path
    return requests.get(f"{_GUTENBURG_URL}/{file_path}").text

"""Representation of a book.

Currently just acts like a named tuple, but will be extended.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    title: str
    text: str
    author: Optional[str] = None

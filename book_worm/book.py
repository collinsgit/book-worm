"""Representation of a book.

Currently just acts like a named tuple, but will be extended.
"""
from typing import Optional

from pydantic import BaseModel


class Book(BaseModel):
    title: str
    text: str
    author: Optional[str] = None

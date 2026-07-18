"""
01_bookstore — CRUD API для книжного магазина 📚
"""

Татачка, [18 июля 2026 г., 22:49:59]:
...from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Category(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=50)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

    model_config = {"extra": "forbid"}


class Book(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2025)
    isbn: str
    price: float = Field(gt=0)
    category_id: Optional[int] = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, value: str) -> str:
        if not value.isdigit() or len(value) not in (10, 13):
            raise ValueError("ISBN must contain 10 or 13 digits")
        return value


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2025)
    isbn: str
    price: float = Field(gt=0)
    category_id: Optional[int] = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, value: str) -> str:
        if not value.isdigit() or len(value) not in (10, 13):
            raise ValueError("ISBN must contain 10 or 13 digits")
        return value

    model_config = {"extra": "forbid"}


class BookNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail="Book not found")


class DuplicateIsbnException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=409, detail="Book with this ISBN already exists")


app = FastAPI(title="Bookstore API")

BOOKS: list[dict] = []
CATEGORIES: list[dict] = []


@app.exception_handler(BookNotFoundException)
def book_not_found_handler(request, exc: BookNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Book not found", "code": "NOT_FOUND"},
    )


@app.exception_handler(DuplicateIsbnException)
def duplicate_isbn_handler(request, exc: DuplicateIsbnException):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.detail, "code": "DUPLICATE_ISBN"},
    )


def _next_book_id() -> int:
    if not BOOKS:
        return 1
    return max(book["id"] for book in BOOKS) + 1


def _next_category_id() -> int:
    if not CATEGORIES:
        return 1
    return max(category["id"] for category in CATEGORIES) + 1


def _find_book(book_id: int) -> dict:
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    raise BookNotFoundException()


def _isbn_exists(isbn: str, exclude_book_id: int | None = None) -> bool:
    return any(
        book["isbn"] == isbn and book["id"] != exclude_book_id
        for book in BOOKS
    )


@app.get("/categories")
def list_categories():
    return CATEGORIES


@app.post("/categories", status_code=201)
def create_category(category: CategoryCreate):
    new_category = {"id": _next_category_id(), "name": category.name}
    CATEGORIES.append(new_category)
    return new_category


@app.get("/books")
def list_books(category_id: Optional[int] = None, year: Optional[int] = None):
    result = BOOKS

    if category_id is not None:
        result = [book for book in result if book.get("category_id") == category_id]

    if year is not None:
        result = [book for book in result if book["year"] == year]

    return result


@app.get("/books/search")
def search_books(query: str):
    normalized_query = query.lower()
    return [
        book
        for book in BOOKS
        if normalized_query in book["title"].lower()
        or normalized_query in book["author"].lower()
    ]


@app.get("/books/{book_id}")
def get_book(book_id: int):
    return _find_book(book_id)

@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    if _isbn_exists(book.isbn):
        raise DuplicateIsbnException()

    new_book = {"id": _next_book_id(), **book.model_dump()}
    BOOKS.append(new_book)
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate):
    current_book = _find_book(book_id)

    if _isbn_exists(book.isbn, exclude_book_id=book_id):
        raise DuplicateIsbnException()

    current_book.clear()
    current_book.update({"id": book_id, **book.model_dump()})
    return current_book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    book = _find_book(book_id)
    BOOKS.remove(book)
    return Response(status_code=204)

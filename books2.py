import inspect
from enum import Enum
from random import randint
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, Form, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from google_books import get_google_books


# ENVIROMENT VARIABLES
class ENV(str, Enum):
    BOOKS = "BOOKS"
    SECURE_BOOKS = "SECURE_BOOKS"
    processing = "processing"
    description_max_size = "description_max_size"
    delta = "delta"


env = {
    ENV.BOOKS: [],
    ENV.SECURE_BOOKS: [],
    ENV.processing: False,
    ENV.description_max_size: 200,
    ENV.delta: 1
}

BOOKS = []
SECURE_BOOKS = []
processing = False
description_max_size = 200
delta = 1

# EXCEPTIONS CLASSES


class ModuleException(HTTPException):
    def __init__(self, function_name: str):
        self.function_name = function_name


class NegativeNumberException(ModuleException):
    def __init__(self, function_name, books_to_return):
        super().__init__(function_name)
        self.books_to_return = books_to_return
        self.status_code = 418
        self.detail = '{}: The number of books to return must be positive. You entered {}'.format(
            self.function_name, self.books_to_return)
        self.headers = self.detail


class ItemNotFoundException(ModuleException):
    def __init__(self, function_name, book_id: UUID):
        super().__init__(function_name)
        self.book_id = book_id
        self.status_code = 404
        self.detail = '{}: Book with ID: [{}] not found'.format(
            function_name, book_id),
        self.headers = '{}: Nothing to be seen at the UUID: [{}].'.format(
            function_name, book_id)


class ItemNameNotFoundException(ModuleException):
    def __init__(self, function_name, query):
        super().__init__(function_name)
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = '{}: Book with name [{}] not found.'.format(
            function_name, query)
        self.headers = self.detail


class AuthenticationException(ModuleException):
    def __init__(self, function_name, username):
        super().__init__(function_name)
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = '{}: Authentication failure for [{}].'.format(function_name, username)
        self.headers = self.detail


# FASTAPI APP CREATION
app = FastAPI()

# BOOK CLASSES


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        title="Description of the book",
        min_length=1,
        max_length=description_max_size
    )
    rating: int = Field(ge=0, le=100)

    class Config:
        schema_extra = {
            "example": {
                "id": uuid4(),
                "title": "The Zen of Python",
                "author": "Tim Peters",
                "description": "A collection of 19 aphorisms about Python",
                "rating": randint(60, 100)
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        title="Description of the book",
        min_length=1,
        max_length=description_max_size
    )

    class Config:
        schema_extra = {
            "example": {
                "id": uuid4(),
                "title": "The Zen of Python",
                "author": "Tim Peters",
                "description": "A collection of 19 aphorisms about Python",
            }
        }

# EXCEPTIONS


@app.exception_handler(ModuleException)
async def module_exception_handler(request: Request, exc: ModuleException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
        headers={"X-Header-Error": exc.headers}
    )

# CRUD OPERATIONS


@app.post("/books/login", status_code=status.HTTP_202_ACCEPTED)
async def book_login(username: str = Form(...), password: str = Form(...)):
    return {"message": "You are logged in",
            "username": username,
            "password": password
            }


def get_a_book(book_id: UUID):
    for book in BOOKS[delta:]:
        if book.id == book_id:
            return book
    return None


def get_a_book(book_title: str):
    for book in BOOKS[delta:]:
        if book.title == book_title:
            return book
    return None


def validated_user(username: str, password: str):
    target_user = "FastAPIUser"
    target_password = "test1234!"
    return username == target_user and password == target_password


@app.post("/books/assignment/", status_code=status.HTTP_200_OK)
async def book_login(username: str = Header(None),
                     password: Optional[str] = Header(None),
                     query: Optional[str] = Header(None)):
    if validated_user(username, password):
        book = get_a_book(query)
        if book is None:
            raise ItemNameNotFoundException(inspect.stack()[0][3], query)
        else:
            return {"message": "You are logged in",
                    "username": username,
                    "password": password,
                    "book_id": query,
                    "book": book
                    }
    else:
        raise AuthenticationException(inspect.stack()[0][3], username)


@app.get("/header", status_code=status.HTTP_200_OK)
async def read_header(random_header: Optional[str] = Header(None)):
    return {"Random-Header": random_header}


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all_books(books_to_return: Optional[int] = None):
    if processing:
        return {"wait": "No books found yet. Still processing"}
    else:
        if books_to_return and books_to_return < 0:
            raise NegativeNumberException(
                inspect.stack()[0][3], books_to_return)

        if len(BOOKS) == 0:
            create_book_no_api()
            global delta
            delta = 0

        if books_to_return and books_to_return < (len(BOOKS)+(1-delta)):
            return BOOKS[delta:books_to_return+delta]
        else:
            return BOOKS[delta:]


@app.get("/book/{book_id}")
async def read_book(book_id: UUID):
    if processing:
        return {"wait": "No books found yet. Still processing"}
    else:
        book = get_a_book(book_id)
        if book:
            return book
        else:
            raise ItemNotFoundException(inspect.stack()[0][3], book_id)


@app.get("/book/rating/{book_id}", response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    if processing:
        return {"wait": "No books found yet. Still processing"}
    else:
        book = get_a_book(book_id)
        if book:
            return book
        else:
            raise ItemNotFoundException(inspect.stack()[0][3], book_id)


@app.put("/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_book(book_id: UUID, book: Book):
    if processing:
        return {"wait": "No books found yet. Still processing"}
    else:
        counter = 0
        for onebook in BOOKS[delta:]:
            counter += 1
            if onebook.id == book_id:
                onebook.title = book.title
                onebook.author = book.author
                onebook.description = book.description
                onebook.rating = book.rating
                BOOKS[counter-(1-delta)] = onebook
                return onebook

        raise ItemNotFoundException(inspect.stack()[0][3], book_id)


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    if processing:
        return {"wait": "No books found yet. Still processing"}
    else:
        BOOKS.append(book)
        return book


@app.delete("/{book_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_book(book_id: UUID):
    if processing:
        return {"wait": "No books found yet. Still processing"}
    else:
        counter = 0
        for onebook in BOOKS[delta:]:
            counter += 1
            if onebook.id == book_id:
                del BOOKS[counter-(1-delta)]
                return {'success": "Book with ID: [{}] deleted'.format(book_id)}

        raise ItemNotFoundException(inspect.stack()[0][3], book_id)

# STARTUP AND SHUTDOWN EVENTS


@app.on_event("startup")
async def create_book_from_google():
    processing = True
    books = get_google_books()

    BOOKS.clear()
    BOOKS.append(
        {"processing": "Processing books from Google Books API. Size: " + str(len(books))})
    for book in books:
        book_description = book["volumeInfo"]["description"] if "description" in book["volumeInfo"] else "<No description found>"
        if len(book_description) > description_max_size:
            book_description = book_description[:
                                                description_max_size-3] + "..."

        authors = book["volumeInfo"]["authors"] if "authors" in book["volumeInfo"] else None
        if authors is not None:
            if len(authors) > 50:
                authors = ' | '.join(authors[:47] + "...")
            else:
                authors = ' | '.join(authors)
        else:
            authors = "<No authors found>"

        book = Book(
            id=uuid4(),
            title=book["volumeInfo"]["title"],
            author=authors,
            rating=randint(60, 100),
            description=book_description
        )
        BOOKS.append(book)
    processing = False
    return BOOKS


@app.on_event("shutdown")
async def shutdown_event():
    return "Shutting down"

# RESET BOOKS


@app.post("/reset/", status_code=status.HTTP_202_ACCEPTED)
async def reset():
    BOOKS.clear()
    processing = False
    return BOOKS

# EXTRAS


def create_book_no_api():
    for i in range(randint(0, 100)):
        book = Book(
            id=uuid4(),
            title="The Hitchhiker's Guide to the Galaxy " + str(i),
            author="Douglas Adams " + str(i),
            rating=randint(0, 100)
        )
        BOOKS.append(book)
    return BOOKS

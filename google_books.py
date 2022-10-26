# Python's built-in module for encoding and decoding JSON data
import json
# Python's built-in module for opening and reading URLs
from urllib.request import urlopen

# sample ISBN for testing: 1593276036


def get_google_books():
    # create getting started variables
    api = "https://www.googleapis.com/books/v1/volumes?q=*&maxResults=40"

    # send a request and get a JSON response
    resp = urlopen(api)

    # parse JSON into Python as a list
    book_data = json.load(resp)
    book_list = book_data["items"]

    return book_list


def get_google_book(isbn):
    # define return book list
    books = []

    # create getting started variables
    api = "https://www.googleapis.com/books/v1/volumes?q=*"
    # isbn = input("Enter 10 digit ISBN: ").strip()

    # send a request and get a JSON response
    resp = urlopen(api + isbn)

    # parse JSON into Python as a dictionary
    book_data = json.load(resp)

    # create additional variables for easy querying
    volume_info = book_data["items"][0]["volumeInfo"]
    author = volume_info["authors"]

    # practice with conditional expressions!
    prettify_author = author if len(author) > 1 else author[0]

    # display title, author, page count, publication date
    # fstrings require Python 3.6 or higher
    # \n adds a new line for easier reading
    print(f"\nTitle: {volume_info['title']}")
    print(f"Author: {prettify_author}")
    print(f"Page Count: {volume_info['pageCount']}")
    print(f"Publication Date: {volume_info['publishedDate']}")
    print("\n***\n")

    return book_data

    # # ask user if they would like to enter another isbn
    # user_update = input("Would you like to enter another ISBN? y or n ").lower().strip()

    # if user_update != "y":
    #     print("May the Zen of Python be with you. Have a nice day!")
    #     break # as the name suggests, the break statement breaks out of the while loop

### FURTHER READING ###

# Further reading on JSON:
# https://realpython.com/python-json/

# Futher reading on urllib:
# https://docs.python.org/3/library/urllib.html

# Requests is another highly recommended third-party HTTP package for Python:
# http://docs.python-requests.org/en/master/

# Looking for a free place to store your programs online?
# Try GitHub Gists: https://gist.github.com/

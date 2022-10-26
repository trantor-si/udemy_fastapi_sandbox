from fastapi import FastAPI

app = FastAPI()
local_var = "Trantor SI"
counter = 0

BOOKS = {
    'book_1': {'title': 'Title One', 'author': 'Author One'},
    'book_2': {'title': 'Title Two', 'author': 'Author Two'},
    'book_3': {'title': 'Title Three', 'author': 'Author Three'},
    'book_4': {'title': 'Title Four', 'author': 'Author Four'},
    'book_5': {'title': 'Title Five', 'author': 'Author Five'},
}

@app.get("/")
async def read_book():
    return {"saudation": "Hello World {}!".format(local_var)}

@app.get("/books/{book_id}")
async def read_book(book_id: int):
    return {"book_id": book_id}

@app.get("/books/{book_id}/authors/{author_id}")
async def read_book_author(book_id: int, author_id: str):
    return {"book_id": book_id, "author_id": author_id} 

@app.get("/books/{book_id}/authors/{author_id}/items/{item_id}")
async def read_book_author_item(book_id: int, author_id: str, item_id: str):
    return {"book_id": book_id, "author_id": author_id, "item_id": item_id}

# Store a value in a local_var variable
@app.post("/universe/ins/{universe_id}")
async def update_book(universe_id: str):
    global local_var
    global counter
    counter = 0
    local_var = universe_id
    return {"local_var": local_var}

# Update a value in a local_var variable
@app.put("/universe/upd/")
async def update_book():
    global local_var
    global counter
    counter += 1
    local_var = local_var + ": " + str(counter)
    return {"local_var": local_var}

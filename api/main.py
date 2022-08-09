from fastapi import FastAPI
from models.item import Item
from typing import Union


app = FastAPI()
# TODO: Setup an xbox client here
# TODO: Setup a psn client here
# TODO: Setup a steam client here

@app.get("/xbox/{xbox_gamertag}")
def get_xbox_account_id(xbox_gamertag: int):
    """
    This endpoint will receive an xbox gamertag and will return the
    corresponding xbox account id connected to that xbox gamertag.
    """
    # TODO: Call a function here, passing the xbox gamertag and being returned
    # the account id
    xbox_account_id = 
    return xbox_account_id

@app.get("/psn/{psn_online_id}")
def get_psn_account_id(psn_online_id: int):
    """
    This endpoint will receive an xbox gamertag and will return the
    corresponding xbox account id connected to that xbox gamertag.
    """
    # TODO: Call a function here so we can pass 
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


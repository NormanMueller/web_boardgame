from __future__ import annotations
from django.shortcuts import render
from django.urls import reverse
from dataclasses import dataclass, field
import json

@dataclass
class Bücherhallen:
    availability :str
    count: str
    current_item_state: str
    category:str



@dataclass
class Game:
    name: str 
    rank: int
    image: str
    ebay_kleinanzeigen: EbayKleinanzeigen  = None
    bücherhallen: Bücherhallen  = None

@dataclass
class EbayKleinanzeigen:
    link:str
    price:int
    description:str
    location:str
    date:str


def index(request):
    games_list: list[Game] = []

    with open("boardgame/bgg_top_100.json") as f:
        bgg_top_100 = json.load(f)

    with open("boardgame/ebay_kleinanzeigen_dict.json") as f:
        ebay_kleinanzeigen = json.load(f)
    
    with open("boardgame/bücherhallen.json") as f:
        bücherhallen = json.load(f)


    for game in bgg_top_100:
        game = Game(**game)
        ebay_entry = ebay_kleinanzeigen.get(game.name)
        if ebay_entry:
            game.ebay_kleinanzeigen = EbayKleinanzeigen(**ebay_entry)
        
        bücherhallen_entry = bücherhallen.get(game.name)
        if bücherhallen_entry:
            game.bücherhallen = Bücherhallen(**bücherhallen_entry)

        games_list.append(game)
    return render(request, "boardgame/index.html", {
            "entries": games_list
        })

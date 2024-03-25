from pathlib import Path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse

import json
from . import util
from django import forms



def index(request):
    games_list: list[util.Game] = util.get_top_100_games()
    with open("boardgame/ebay_kleinanzeigen_dict.json") as f:
        ebay_kleinanzeigen = json.load(f)
    
    for game in games_list:

        ebay_entry = ebay_kleinanzeigen.get(game.name)
        if ebay_entry:
            game.ebay_kleinanzeigen = util.EbayKleinanzeigen(link=ebay_entry["link"], 
                              price=ebay_entry["price"], 
                              description=ebay_entry["description"],
                              location=ebay_entry["location"],
                              date=ebay_entry["date"])


    return render(request, "boardgame/index.html", {
            "entries": games_list
        })

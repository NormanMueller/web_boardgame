from __future__ import annotations
from dataclasses import dataclass, field
import json
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import requests

# Ebay_Kleinanzeigen 
RADIUS_ALTONA_10_KM = "k0l9506r10" 
GAME_NAME = "Brass Birmingham"
EBAY_KLEINANZEIGEN_URL = "https://www.kleinanzeigen.de/s-spielzeug/" + GAME_NAME + "/" + RADIUS_ALTONA_10_KM 
MAX_RESLTS = 1
FILTER_CONDITION = ["spiel", "brettspiel", "gesellschaftsspiel", "sammlung","kickstarter", "edition" ]

#BoardgameGeek
TOP_99 =  range(0,99)
BASE_URL_BOARDGAME_GEEK = "https://boardgamegeek.com/browse/boardgame"


@dataclass
class Game:
    name: str 
    rank: int
    image: str
    ebay_kleinanzeigen: EbayKleinanzeigen  = None


@dataclass
class EbayKleinanzeigen:
    link:str
    price:int
    description:str
    location:str
    date:str


@dataclass
class WebDriver:
    url: str
    service:Service = Service(executable_path=r"C:\Users\norma\chromedriver.exe")
    driver:WebDriver = field(init=False)

    def __post_init__(self) -> None:
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get(self.url)
        
    
    def fill_form_by_id(self,find_element_str:str, send_keys:str) -> None:
        search_input = self.driver.find_element(By.ID, find_element_str)
        search_input.clear()       
        search_input.send_keys(send_keys)  
        search_input.send_keys(Keys.ENTER)

    def get_html_soup_object(self) -> BeautifulSoup:
        html = self.driver.page_source
        return BeautifulSoup(html, 'html.parser')    


class NoMatchException(Exception):
    def __init__(self, message = "No results found on EbayKleinanzeigen") -> None:
        self.message = message 
        super().__init__(self.message)


@dataclass
class EbayKleinanzeigenScraper:
    driver:WebDriver = WebDriver(EBAY_KLEINANZEIGEN_URL)

    def find_nr_of_matches(self) -> int:
        h1_tag = self.driver.get_html_soup_object().find('h1')   #1 - 2 von 2 Ergebnissen für Spirit Island 
        pattern = r'\d+\s*-\s*(\d+)'

        matches = re.findall(pattern, str(h1_tag))
        if not matches:
            raise NoMatchException
        
        return MAX_RESLTS if int(matches[0]) >MAX_RESLTS else int(matches[0])     

    @staticmethod
    def check_if_description_matches_condition(description) -> bool:
            check_result = [condition for condition in  FILTER_CONDITION if condition in description.lower() ]
            if check_result:
                return True
            return False


    def get_ebay_kleinanzeigen_listings(self,games:list[Game], plz:str,) -> dict:
        result_dict = {}

        for game in games:
            self.driver.fill_form_by_id(find_element_str='site-search-query', send_keys=game.name) 
            self.driver.fill_form_by_id(find_element_str='site-search-area', send_keys=plz)
            
            try:
                self.find_nr_of_matches()  
            
            except NoMatchException as e:
                result_dict.update({game.name:None})
                continue 

            description = self.driver.driver.find_element(By.CLASS_NAME, "aditem-main--middle--description").text
            date = self.driver.driver.find_element(By.CLASS_NAME, "aditem-main--top--right").text
            price = self.driver.driver.find_element(By.CLASS_NAME, "aditem-main--middle--price-shipping--price").text
            location = self.driver.driver.find_element(By.CLASS_NAME, "aditem-main--top--left").text
            link = self.driver.driver.find_element(By.CSS_SELECTOR, "h2.text-module-begin > a.ellipsis").get_attribute('href')

            if self.check_if_description_matches_condition(description):
                result_dict.update({game.name: EbayKleinanzeigen(description=description,date=date, price=price, location=location, link=link).__dict__})
      
        return result_dict


def get_top_100_games() -> list[Game]:
    base_urls: str = BASE_URL_BOARDGAME_GEEK
    req = requests.get(base_urls)
    soup = BeautifulSoup(req.text, 'html.parser')

    top_100: list[Game] = []

    for game_rank in TOP_99:
            name = soup.find('div', id=f"results_objectname{game_rank+1}").get_text(strip=True)
            cleaned_name = re.sub(r'\([^()]*\)', '', name).strip() #'Spirit Island(2017)' -> Spirit Island
            image = soup.find_all("td", class_="collection_thumbnail")[game_rank].find("img")['src']
            rank = game_rank +1
            top_100.append(Game(name=cleaned_name, image=image, rank=rank))
        
    return top_100



if __name__ == "__main__":

    games = get_top_100_games()
    path = Path(__file__).parent.absolute()

    with open (path / "bgg_top_100.json", "w") as outfile:
        json_serialize = [game.__dict__ for game in games]
        json.dump(json_serialize,outfile)

    ebay_scraper = EbayKleinanzeigenScraper()
    result_dict = ebay_scraper.get_ebay_kleinanzeigen_listings(games=games,
                                                               plz= "22767",
                                                               )
    print(result_dict)

    with open (path / "ebay_kleinanzeigen_dict.json", "w") as outfile:
        json.dump(result_dict,outfile)
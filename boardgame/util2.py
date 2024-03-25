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
import time
from selenium.common.exceptions import NoSuchElementException


# Ebay_Kleinanzeigen



@dataclass
class Bücherhallen:
    availability :str
    count: str
    current_item_state: str
    category:str

@dataclass
class WebDriver:
    url: str
    service:Service = Service(executable_path=r"C:\Users\norma\chromedriver.exe")
    driver:webdriver.Chrome = field(init=False)

    def __post_init__(self) -> None:
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get(self.url)

    def fill_form(self,find_element_str:str, send_keys:str) -> None:
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
class HtmlTag:
    search_dict:dict
    name: str

    
    def run_find_return_strip_text(self,tag_object:Tag| BeautifulSoup) -> dict:
        result = tag_object.find(**self.search_dict).get_text(strip=True)
        return {self.name:result}

    def run_find_return_tag(self,tag_object:Tag| BeautifulSoup) -> Tag| BeautifulSoup:
            return  tag_object.find(**self.search_dict)



EBAY_KLEINANZEIGEN_URL = "https://www.buecherhallen.de/katalog-suchergebnisse.html"
FILTER_CONDITION = "Gesellschaftsspiel"

@dataclass
class BücherhallenScraper:
    list_of_tags: list[HtmlTag]
    driver:WebDriver = WebDriver(EBAY_KLEINANZEIGEN_URL)

    def get_bücherhallen_listings(self, games) -> dict:
        result_dict = {}


        for game in games:
            self.driver.fill_form(find_element_str='ctrl_4', send_keys=game.get("name"))
            time.sleep(1)  
            try:
                self.driver.driver.find_element(By.CLASS_NAME,"search-results-image").click()
                time.sleep(1)  

                self.driver.driver.find_element(By.CLASS_NAME,"medium-availability-item-title-location").click()
                time.sleep(1)  
                
                current_item_state = self.driver.driver.find_element(By.CLASS_NAME, "item-data.item-data-current-item-state-message")
                category = self.driver.driver.find_element(By.CLASS_NAME, "item-data.item-data-shelfmark")
                availability = self.driver.driver.find_element(By.CLASS_NAME,'medium-availability-item-title-location')
                count =  self.driver.driver.find_element(By.CLASS_NAME,"medium-availability-item-title-count")

                if category != FILTER_CONDITION:
                    result_dict.update({game["name"]:None})
                
                result_dict.update({game["name"]:Bücherhallen(
                                   current_item_state=current_item_state.text,
                                   category=category.text,
                                   availability=availability.text,
                                   count=count.text
                                   ).__dict__})
                                   
            except NoSuchElementException as e:
                pass     
        
        return result_dict

            
        
       # return result_dict


if __name__ == "__main__":
    availability = HtmlTag(search_dict={'name':'span','class_':'medium-availability-item-title-location'}, name="availability")
    count =  HtmlTag(search_dict={'name':'span','class_':'medium-availability-item-title-count'}, name="count")
    description =  HtmlTag(search_dict={'name':'span','class_':'medium-detail-item-value'}, name="description")

    list_of_tags = [availability,count,description]
    path = Path(__file__).parent.absolute()
    
    with open(path / "bgg_top_100.json", 'r') as f:
        bgg_top_100 = json.load(f)

    bücherhallen_scraper = BücherhallenScraper( list_of_tags=list_of_tags)
    result_dict = bücherhallen_scraper.get_bücherhallen_listings(games = bgg_top_100) 
    
    with open (path / "bücherhallen.json", "w") as outfile:
        json.dump(result_dict,outfile)

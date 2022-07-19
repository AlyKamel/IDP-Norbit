import requests
import json
from fake_useragent import UserAgent
from pathlib import Path


def readJson(path):
    path += '.json'
    path = Path(__file__).parent / path
    with path.open() as json_file:
        data = json.load(json_file)
        return data

# Expects data to be populated by idfetcher.py
brands = readJson('data/brands')
sizes = readJson('data/sizes')
def getBrands():
    return brands

def getJSON(url):
    header = {
        'User-Agent': UserAgent().safari
    }
    res = requests.get(url, headers=header)
    return res.json()

def getBrandId(brand):
    for x in brands:
        if x["text"] == brand:
            return x["id"]

    raise ValueError('Invalid brand supplied')

def getSizeId(size):
    for x in sizes:
        if float(x["text"].split()[0].replace(",", ".")) == float(size):
            return x["id"]
    raise ValueError('Size not found')


def createSearchUrl(price_range, brand, size):
    url = "https://www.idealo.de/mvc/CategoryData/results/category/4012?pageIndex=0&sortKey=DEFAULT&onlyNew=false&onlyBargain=false&onlyAvailable=false"

    url += f"&p={price_range[0]}-{price_range[1]}" if price_range != None else ""
    url += f"&filters={getBrandId(brand)}" if brand != None else ""
    url += f"&filters={getSizeId(size)}" if size != None else ""
    return url


def findProducts(price_range, brand, size):
    url = createSearchUrl(price_range, brand, size)

    products = []
    while url != None and len(products) < 50:
        res = getJSON(url)
        products += res['categoryJsonResults']['entries']

        pagination = res['categoryPagination']
        url = pagination['nextPageAjaxLink'] if pagination != None else None
    return products


# For testing
# ps = findProducts((0,1000), "Samsung", 40)
# for p in ps:
#     print(p['link']['productLink']['href'])

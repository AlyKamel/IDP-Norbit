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

"https://www.idealo.de/mvc/CategoryAttributeFilters/category/4012/attribute/16"
"https://www.idealo.de/preisvergleich/Sitemap.html"
""""
def openDriver(url = None):
    options = Options()
    # options.add_argument('--headless')
    options.add_argument("--incognito")
    options.add_argument("--nogpu")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1280")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')

    # Safari
    # driver = webdriver.safari.webdriver.WebDriver(quiet=False)

    driver = webdriver.Chrome(options=options)
    if url != None:
        driver.get(url)
    return driver

def fetchDriverContent(driver):
    print("Spam:", "Sicherheitsprüfung (Spam-Schutz)" in driver.page_source)
    jsonstring = driver.find_element(By.TAG_NAME, "body").text
    return jsonstring

    driver = openDriver()
    products = []

    while url != None and len(products) < 100:
        driver.get(url)
        time.sleep(1)

        content = fetchDriverContent(driver)
        dict = json.loads(content)
        products += dict['categoryJsonResults']['entries']

        pagination = dict['categoryPagination']
        url = pagination['nextPageAjaxLink'] if pagination != None else None
    return products
"""

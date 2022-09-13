import json
from pathlib import Path
from scraping.util.util import fetchJSON


def readJson(path):
    path += '.json'
    path = Path(__file__).parent / path
    with path.open() as json_file:
        data = json_file.read()
        data = json.loads(data)
        return data

# Expects data to be populated by idfetcher.py
brands = readJson('data/brands')
sizes = readJson('data/sizes')
types = readJson('data/types')

def getBrands():
    return brands

def getTypes():
    return types

def getBrandId(brand):
    try:
        return brands[brand]
    except KeyError:
        raise ValueError('Invalid brand supplied')

def getSizeId(size):
    for s, id in sizes.items():
        if float(s.split()[0].replace(",", ".")) == float(size):
            return id
    raise ValueError('Size not found')

def getTypeId(type):
    return 1921183 # 4K
    # for t, id in types.items():
    #     if float(t.split()[0].replace(",", ".")) == float(size):
    #         return id
    # raise ValueError('Type not found')

def getValidSize(size):

    # valid_size = 0
    # size_string = str(size).replace('.', ',') + ' Zoll'
    # pos = bisect_left(list(sizes.keys()), size_string)
    # if pos == 0:
    #     valid_size = sizes[0]
    # elif pos == len(sizes):
    #     valid_size = sizes[-1]
    # else:
    #     sm_size = sizes[pos - 1]
    #     lg_size = sizes[pos + 1]
    #     if lg_size - size < size - sm_size:
    #         valid_size = lg_size
    #     else:
    #         valid_size = sm_size
    # return valid_size

    # get closest number
    diff = float('inf')
    valid_size = 0
    for s in sizes:
        # parse to float
        s = float(s.replace(',', '.').replace(' Zoll', ''))
        temp_diff = abs(s - size)
        if temp_diff < diff:
            diff = temp_diff
            valid_size = s
        else:
            break
    return valid_size

def createSearchUrl(price_range, brand, size, type):
    url = "https://www.idealo.de/mvc/CategoryData/results/category/4012?pageIndex=0&sortKey=DEFAULT&onlyNew=false&onlyBargain=false&onlyAvailable=false"

    url += f"&p={price_range[0]}-{price_range[1]}" if price_range != None else ""
    url += f"&filters={getBrandId(brand)}" if brand != None else ""
    url += f"&filters={getSizeId(size)}" if size != None else ""
    url += f"&filters={getTypeId(type)}" if type != None else ""
    return url


def findProducts(price_range, brand, size, type):
    url = createSearchUrl(price_range, brand, size, type)

    products = []
    while url != None and len(products) < 50:
        res = fetchJSON(url)
        products += res['categoryJsonResults']['entries']

        pagination = res['categoryPagination']
        url = pagination['nextPageAjaxLink'] if pagination != None else None
    return products

# For testing
# ps = findProducts((0, 550), "Samsung", 65, "4K")
# for p in ps:
#     print(p['link']['productLink']['href'])
# correct_results = ['/preisvergleich/OffersOfProduct/201240173_-gu65au7179u-samsung.html',
#       'https://www.idealo.de/preisvergleich/OffersOfProduct/201452975_-ue65tu7095uxxc-samsung.html']
# if ps != correct_results:
#     raise ValueError("invalid result")

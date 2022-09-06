import requests
from fake_useragent import UserAgent
from pathlib import Path
import json

def getJSON(url):
    header = {
        'User-Agent': UserAgent().safari
    }
    res = requests.get(url, headers=header)
    return res.json()

def getFilter(filters, name):
    att = next(x for x in filters if x["title"] == name)['remainingItems']
    name_id_dic = {}
    for i in att:
        name_id_dic[i['text']] = i['id']
    return name_id_dic

def storeProductIds():
    """Stores the feature ids that are needed for creating search filters. Should be used run in a while, to account for any changes on the server side."""

    url = 'https://www.idealo.de/mvc/CategoryData/results/category/4012?pageIndex=0&sortKey=DEFAULT&onlyNew=false&onlyBargain=false&onlyAvailable=false'
    res = getJSON(url)
    filters = res['productJsonFilterRows']['popularFilterAttributes']

    brands = getFilter(filters, "Hersteller")
    sizes = getFilter(filters, "Bildschirmgröße")
    types = getFilter(filters, "Produkttyp")
    types = {k.replace("-", " ").replace("Fernseher", "").strip(): v for k, v in types.items()}

    output_file = Path(__file__).parent / 'data'
    output_file.mkdir(exist_ok=True, parents=True)
    with open(output_file / 'brands.json', 'w') as f:
        json.dump(brands, f, indent=4)
    with open(output_file / 'sizes.json', 'w') as f:
        json.dump(sizes, f, indent=4)
    with open(output_file / 'types.json', 'w') as f:
        json.dump(types, f, indent=4)

    # add lookup tables
    output_file = Path('data/lookup')

    # Generate txt file for tv_brand lookup
    output_file.mkdir(exist_ok=True, parents=True)
    with open(output_file / 'tv_brand.txt', 'w') as f:
        for key in brands:
            f.write(f"{key}\n")

    # Generate yml file for tv_type lookup
    with open(output_file / 'tv_type.yml', 'w') as f:
        f.write(f"version: \"3.1\"\nnlu:\n  - lookup: tv_type  \n    examples: |\n")
        for key in types:
            f.write(f"      - {key}\n")

if __name__ == "__main__":
    storeProductIds()
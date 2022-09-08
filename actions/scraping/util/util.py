import requests
from fake_useragent import UserAgent

def fetchJSON(url):
    # url = "http://httpbin.org/headers"
    # geht mit vpn ohne proxy
    # proxies = {
    #     'http': "e3w4Lh9DDxcCV53kEdVBDFDn:axapSk9DknEsHemT23EcNR3T@de-fra.prod.surfshark.com",
    #     'https': "e3w4Lh9DDxcCV53kEdVBDFDn:axapSk9DknEsHemT23EcNR3T@de-fra.prod.surfshark.com",
    # }
    # cookies = {'ipcuid': '01waaonh00l7rp7qpa'}

    headers = {
        'User-Agent': UserAgent().safari,
        "Accept-Language": "en-US,en;q=0.9",
    }
    res = requests.get(url, headers=headers)

    if res.status_code == 429:
        raise ConnectionError("Blocked by spam protection")
    return res.json()
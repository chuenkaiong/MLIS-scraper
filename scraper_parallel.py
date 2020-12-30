import requests
from helper import get_legis_body, save_file    # helper functions for getting and saving legislation
from bs4 import BeautifulSoup

# disable warnings for HTTPS certificate verification
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.mlis.gov.mm"
s = requests.Session()
s.verify = False        # disable HTTPS certificate verification (not ideal)

# Get set of all laws with parallel translations
list_url = url + '/mLsScList.do'

payload = {"pageSize":150,"upperLawordKndCode":"0100","queryType":"07","ordrType":"01","query":"","selFont":"PYI"}
lawordSn_set = set()

pageNo = 1
not_empty = True
while not_empty:
  payload["pageIndex"] = pageNo
  r = s.post(list_url, json=payload)
  if len(r.json()['list']) == 0:
    not_empty = False
  else:
    for item in r.json()['list']:
      lawordSn_set.add(item["lawordSn"])
  pageNo += 1

# generate final list of legislation objects, each with a pointer to EN and MY versions 
legis_list = []
for item in lawordSn_set:
  legis_list.append({"EN": item})

# Obtain Burmese translations for each piece of legislation 
view_legis_url = "https://www.mlis.gov.mm/mLsView.do"

for legis in legis_list:
  payload = {"lawordSn": legis["EN"]}
  r = s.get(view_legis_url, params = payload)
  soup = BeautifulSoup(r.text, "lxml")
  
  try:
    translation_link = soup.find('a', class_='btn-convert').get('href')
    translation_lawordSn = translation_link.split("lawordSn=")[1]
    legis["MY"] = translation_lawordSn
  except:
    print(f"translation link unavailable for {legis['EN']}")
    legis["MY"] = None

# Obtain English and Burmese versions of the law in parallel and save to similarly named files (legislation title followed by _MY or _EN)
for legis in legis_list:
  en = legis["EN"]
  my = legis["MY"]

  title_en, paras_en = get_legis_body(en, s)
  # save_file(title_en + "_EN", paras_en)

  if my != None:
    title_my, paras_my = get_legis_body(my, s)
    # save_file(title_en + "_MY", paras_my)
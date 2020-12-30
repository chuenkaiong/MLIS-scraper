import requests
from helper import get_legis_body, save_file_subordinate    # helper functions for getting and saving legislation
from bs4 import BeautifulSoup

# disable warnings for HTTPS certificate verification
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.mlis.gov.mm"
s = requests.Session()
s.verify = False        # disable HTTPS certificate verification (not ideal)

# Get set of all laws with parallel translations
list_url = url + '/lsScListJsp.do'

payload = {"pageSize":150,"upperLawordKndCode":"0200","queryType":"07","ordrType":"01","query":"","selFont":"PYI"}

lawordSn_set = set()

list_url = url + '/lsScListJsp.do'
payload = {"pageSize":150,"upperLawordKndCode":"0200","queryType":"07","ordrType":"01","query":"","selFont":"PYI"}

pageNo = 1
not_empty = True
while not_empty:
  payload["pageIndex"] = pageNo
  r = s.post(list_url, json=payload)
  soup = BeautifulSoup(r.text, "lxml")
  lawordSn_list = [link['lawordsn'] for link in soup.find_all("a", "link_wide")]
  if len(lawordSn_list) == 0:
    not_empty = False
  else:
    for lawordSn in lawordSn_list:
      lawordSn_set.add(lawordSn)
  pageNo += 1

# generate final list of legislation objects, each with a pointer to EN and MY versions 
legis_list = []
for item in lawordSn_set:
  legis_list.append({"EN": item})

# Obtain Burmese translations for each piece of legislation 
view_legis_url = "https://www.mlis.gov.mm/mLsView.do"

unavailable = []
for legis in legis_list:
  payload = {"lawordSn": legis["EN"]}
  r = s.get(view_legis_url, params = payload)
  soup = BeautifulSoup(r.text, "lxml")
  
  translation_link = soup.find('a', class_='btn-convert')
  if translation_link:
    translation_lawordSn = translation_link.get('href').split("lawordSn=")[1]
    legis["MY"] = translation_lawordSn
  else:
    unavailable.append(legis["EN"])
    legis["MY"] = None

# output log of serial numbers scraped 
with open("data/subordinate/log.txt", "w") as f:
  for item in legis_list:
    f.write(str(item) + "\n")

# Obtain English and Burmese versions of the law in parallel and save to similarly named files (legislation title followed by _MY or _EN)
for legis in legis_list:
  en = legis["EN"]
  my = legis["MY"]

  title_en, paras_en = get_legis_body(en, s)
  save_file_subordinate(title_en + "_EN", paras_en)

  if my != None:
    title_my, paras_my = get_legis_body(my, s)
    save_file_subordinate(title_en + "_MY", paras_my)
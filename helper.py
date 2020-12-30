from bs4 import BeautifulSoup
def get_legis_body(lawordSn, s):
  payload = {"lawordSn": lawordSn}
  r = s.post("https://www.mlis.gov.mm/mLsViewDetail.do", json=payload)
  soup = BeautifulSoup(r.text, features="html.parser")
  title = soup.find("p", "H3").text

  sections = soup.find_all("p", ["SEC1", "SEC2", "SEC3"])
  paras = []
  for section in sections:
    if "SEC1" in section["class"]:
      paras.append(section.text)
    elif len(paras) > 0:
      paras[-1] += section.text
  
  title = title.replace("/", ",")

  return title, paras

def save_file(filename, paras):
  with open(f"data/{filename}.txt", "wb") as f:
    for para in paras:
      para = para + "\n"
      para_encoded = para.encode("utf8")
      f.write(para_encoded)

def save_file_subordinate(filename, paras):
  with open(f"data/subordinate/{filename}.txt", "wb") as f:
    for para in paras:
      para = para + "\n"
      para_encoded = para.encode("utf8")
      f.write(para_encoded)
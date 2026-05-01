import requests, random, os, sys
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from polen_lib import EMOJIS, LEVELS, create_client, is_dupe, save_data, post_thread

load_dotenv()

POLEN_URL = os.getenv("POLEN_URL_LASROZAS")

try:
    page = requests.get(POLEN_URL, timeout=10)
    page.raise_for_status()
except requests.exceptions.HTTPError as err:
    raise SystemExit(err)

soup = BeautifulSoup(page.content, "html.parser")

data = soup.find_all("label", {"class": "valor"})
dataDict = {
    "ciudad": data[0].get_text(strip=True),
    "fecha":  data[1].get_text(strip=True),
    "datos":  [],
}

raw = [t.get_text(strip=True) for t in soup.find_all("label", {"class": "texto"})[5:]]
for i in range(0, len(raw), 3):
    dataDict["datos"].append({"tipo": raw[i], "medicion": raw[i+1], "nivel": raw[i+2]})
dataDict["datos"].sort(key=lambda k: k["tipo"])

if is_dupe(dataDict["ciudad"], dataDict):
    print("Dupe")
    sys.exit(0)

tweet = random.choice(EMOJIS) + " " + dataDict["fecha"] + "\n"
for d in dataDict["datos"]:
    nivel = d["nivel"]
    if nivel.startswith("Bajo"):       icon = LEVELS["bajo"]
    elif nivel.startswith("Medio"):    icon = LEVELS["medio"]
    elif nivel.startswith("Alto"):     icon = LEVELS["alto"]
    elif nivel.startswith("Muy alto"): icon = LEVELS["muyalto"]
    else:                              icon = ""
    tweet += f"{d['tipo']}: {d['medicion']} {icon}\n"

if tweet.count("\n") < 2:
    tweet += "Sin datos\n"
tweet += "#LasRozas"

print(tweet)
post_thread(create_client("LASROZAS"), tweet)
save_data(dataDict["ciudad"], dataDict)

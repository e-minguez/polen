import requests, random, os, sys, xmltodict, datetime
from dotenv import load_dotenv
from polen_lib import EMOJIS, LEVELS, create_client, is_dupe, save_data, post_thread

load_dotenv()

POLEN_URL = os.getenv("POLEN_URL_AVILA")

try:
    page = requests.get(POLEN_URL, timeout=10)
    page.raise_for_status()
except requests.exceptions.HTTPError as err:
    raise SystemExit(err)

doc = xmltodict.parse(page.content)
element = doc["document"]["list"]["element"]

fecha_inicio = element["@fecha"]
fecha_fin = (datetime.datetime.strptime(fecha_inicio, "%d/%m/%Y") + datetime.timedelta(days=7)).strftime("%d/%m/%Y")

dataDict = {"ciudad": "Ávila", "fecha-inicio": fecha_inicio, "fecha-fin": fecha_fin, "datos": []}
for estacion in element["estacion"]:
    if estacion["@nombre"] == "ÁVILA":
        dataDict["datos"].append({
            "tipo":     estacion["tipo_polinico"]["@nombre"].capitalize(),
            "real":     estacion["tipo_polinico"]["valor_real"].lower(),
            "prevision":estacion["tipo_polinico"]["valor_previsto"].lower(),
        })
dataDict["datos"].sort(key=lambda k: k["tipo"])

if is_dupe(dataDict["ciudad"], dataDict):
    print("Dupe")
    sys.exit(0)

def level_icon(val):
    if val.startswith("bajo"):     return LEVELS["bajo"]
    if val.startswith("moderado"): return LEVELS["medio"]
    if val.startswith("alto"):     return LEVELS["muyalto"]
    return ""

tweet = random.choice(EMOJIS) + " " + fecha_inicio + "-" + fecha_fin + "\n"
for d in dataDict["datos"]:
    tweet += f"{d['tipo']}: {level_icon(d['real'])} [{level_icon(d['prevision'])}]\n"
tweet += "#Ávila"

print(tweet)
post_thread(create_client("AVILA"), tweet)
save_data(dataDict["ciudad"], dataDict)

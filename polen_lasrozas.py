import requests, random, os, sys, json, datetime
from dotenv import load_dotenv
from polen_lib import EMOJIS, LEVELS, classify_level, create_client, is_dupe, save_data, post_thread

load_dotenv()

RESOURCE_ID = "1f2c4851-b69b-4daa-85ae-89f56cabc67d"
CAPTADOR    = os.getenv("CAPTADOR_LASROZAS", "ROZA")
API         = "https://datos.comunidad.madrid/api/3/action/datastore_search"


def ckan_search(**params):
    r = requests.get(API, params=params, timeout=10)
    r.raise_for_status()
    result = r.json()
    if not result.get("success"):
        raise SystemExit(f"CKAN error: {result.get('error')}")
    return result["result"]["records"]


# Fetch recent rows for this captador, filter latest date client-side.
# The provider reloads its datastore non-atomically each day, so a run that lands
# mid-reload can see this captador with no rows yet. Skip gracefully instead of
# crashing and let the next scheduled run pick it up.
all_rows = ckan_search(resource_id=RESOURCE_ID, filters=json.dumps({"captador": CAPTADOR}), sort="fecha_lectura desc", limit=50)
if not all_rows:
    print(f"No data for captador {CAPTADOR} (datastore may be mid-reload); skipping")
    sys.exit(0)
latest_date = all_rows[0]["fecha_lectura"]

if is_dupe("Las Rozas", {"fecha": latest_date}):
    print("Dupe")
    sys.exit(0)

records = sorted([r for r in all_rows if r["fecha_lectura"] == latest_date], key=lambda r: r["tipo_polinico"])

dataDict = {
    "ciudad":   "Las Rozas",
    "captador": CAPTADOR,
    "fecha":    latest_date,
    "datos":    [{"tipo": r["tipo_polinico"], "granos": r["granos_de_polen_x_metro_cubico"]} for r in records],
}

_MONTHS_ES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
def _fmt_date(iso):
    dt = datetime.datetime.fromisoformat(iso)
    return f"{dt.day:02d}-{_MONTHS_ES[dt.month-1]}-{dt.year}"

tweet = random.choice(EMOJIS) + " " + _fmt_date(latest_date) + "\n"
for d in dataDict["datos"]:
    granos = int(d["granos"] or 0)
    if granos == 0:
        continue
    tweet += f"{d['tipo']}: {granos} {LEVELS[classify_level(granos, d['tipo'])]}\n"

if tweet.count("\n") < 2:
    tweet += "Sin datos\n"
tweet += "#LasRozas"

print(tweet)
post_thread(create_client("LASROZAS"), tweet)
save_data("Las Rozas", {"fecha": latest_date})

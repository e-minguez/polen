import requests, json, tweepy, os, random, datetime, locale
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY_LASROZAS")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET_LASROZAS")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_LASROZAS")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET_LASROZAS")

POLEN_URL = os.getenv("POLEN_URL_LASROZAS")

emojis = [
  "\U0001f927", # sneeze
  "\U0001F33E", # wheat
  "\U0001F33A", # flower
  "\U0001f4e2", # loud speaker
  "\U0001F514", # bell
  "\U0001F509", # speaker
  "\U0001F4D6", # open book
  "\U0001F5DE", # newspaper
  "\U0001F4EC"  # mailbox
]

levels = {
  "bajo": "\U0001F7E2", # green
  "medio": "\U0001F7E1", # yellow
  "alto": "\U0001F7E0", # orange
  "muyalto": "\U0001F534" # red
}

hashtag = "#LasRozas"

try:
  page = requests.get(POLEN_URL)
  page.raise_for_status()
except requests.exceptions.HTTPError as err:
  raise SystemExit(err)

soup = BeautifulSoup(page.content, 'html.parser')

tables = soup.findAll("table")

dataDict = {}
dataDict['ciudad'] = "Las Rozas"
dataDict['datos'] = []

for table in tables:
  tmpdict = {}
  for table_row in table.findAll('tr'):
    k=table_row.find("label", {"class": "nombre"}).getText(strip=True)
    v=table_row.find("label", {"class": "valor"}).getText(strip=True)
    if ((k == "FC_FECHA_MEDICION") and ('fecha' not in dataDict)):
      fecha_orig = datetime.datetime.strptime(v,"%d/%m/%y %H:%M")
      locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')
      dataDict['fecha'] = datetime.datetime.strftime(fecha_orig,'%d-%b-%Y')
    if k == "DS_MATERIAS":
      tmpdict['tipo']=v
    if k == "NM_VALOR":
      tmpdict['medicion']=v
      tmpdict['nivel']="bajo"
    if ((k == "NM_MEDIO") and ((int(tmpdict['medicion'])>(int(v))))):
      tmpdict['nivel']="medio"
    if ((k == "NM_ALTO") and ((int(tmpdict['medicion'])>(int(v))))):
      tmpdict['nivel']="alto"
    if ((k == "NM_MUYALTO") and ((int(tmpdict['medicion'])>(int(v))))):
      tmpdict['nivel']="muyalto"
  dataDict['datos'].append(tmpdict)

dataDict['datos'] = sorted(dataDict['datos'], key=lambda k: k['tipo']) 

# Open the previous json data
try:
  with open(dataDict['ciudad']+'.json') as json_file:
    previous = json.load(json_file)
except:
  previous = {}

# If the results are the same, do nothing
if previous == dataDict:
  print("Dupe")
  exit()
# Otherwise, save the file for next execution and continue
else:
  with open(dataDict['ciudad']+'.json','w') as json_file:
    json_file.write(json.dumps(dataDict))

#print(json.dumps(dataDict,indent=4))
tweet = random.choice(emojis) + " " + dataDict['fecha'] + "\n"

for dic in dataDict['datos']:
  tweet += dic["tipo"] + ": " + dic["medicion"] + " " + levels[dic["nivel"]]+ "\n"

tweet += hashtag

print(tweet)

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create API object
api = tweepy.API(auth)

# Create a tweet
api.update_status(tweet)

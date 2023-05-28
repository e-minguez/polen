import requests, json, tweepy, os, random, locale
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY_LASROZAS")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET_LASROZAS")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_LASROZAS")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET_LASROZAS")
BEARER_TOKEN = os.getenv("BEARER_TOKEN_LASROZAS")

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

arrows = {
  "up": "\U00002b06",
  "down": "\U00002b07",
  "equal": "\U00002194"
}

hashtag = "#LasRozas"

try:
  page = requests.get(POLEN_URL)
  page.raise_for_status()
except requests.exceptions.HTTPError as err:
  raise SystemExit(err)

soup = BeautifulSoup(page.content, 'html.parser')

dataDict = {}

data = soup.findAll("label", {"class": "valor"})
dataDict['ciudad'] = data[0].getText(strip=True)
dataDict['fecha'] = data[1].getText(strip=True)
dataDict['datos'] = []

# Tipo, Medicion, Nivel
data = [ tmpdata.getText(strip=True) for tmpdata in soup.findAll("label", {"class": "texto"})[4:] ]

for i in range(0,len(data),2):
  tmpdict = {}
  tmpdict['tipo'] = data[i]
  tmpdict['nivel'] = data[i+1]
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

#locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
#fecha = datetime.strptime(dataDict['fecha'], '%d-%b-%Y')

#if fecha > datetime.today():
#  print("Future")
#  exit()

#print(json.dumps(dataDict,indent=4))
tweet = random.choice(emojis) + " " + dataDict['fecha'] + "\n"

for dic in dataDict['datos']:
  tipo=dic['tipo']
  for k in dic:
    if k == "tipo":
      tweet += dic[k] + ": "
    elif k == "nivel":
      if dic[k].startswith("Bajo"):
        tweet += levels["bajo"]
      elif dic[k].startswith("Medio"):
        tweet += levels["medio"]
      elif dic[k].startswith("Alto"):
        tweet += levels["alto"]
      elif dic[k].startswith("Muy alto"):
        tweet += levels["muyalto"]
  tweet += "\n"

if tweet.count('\n') < 2:
  tweet += "Sin datos\n"
tweet += hashtag

print(tweet)

# Authenticate to Twitter
api = tweepy.Client(bearer_token=BEARER_TOKEN)

api = tweepy.Client(
    consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET
)

TWEET_LIMIT = 280
if len(tweet.encode('utf-8')) > TWEET_LIMIT:
  lines = tweet.splitlines()
  to_tweet = ""
  posted = ""
  for i in range(len(lines)):
    if len(to_tweet.encode('utf-8')) > TWEET_LIMIT:
      # Remove the last 5 characters to fit (...)
      to_tweet = to_tweet[:-5]
      # Find the latest '\n', remove the leftovers and add (...)
      to_tweet = to_tweet[:to_tweet.rfind('\n')] + "(...)" 
      if posted:
        posted = api.create_tweet(text=to_tweet,in_reply_to_tweet_id=posted.data.get('id'))
      else:
        posted = api.create_tweet(text=to_tweet)
      to_tweet = (lines[i-1] + '\n' + lines[i] + '\n')
    else:
      to_tweet += (lines[i] + '\n')
  api.create_tweet(text=to_tweet,in_reply_to_tweet_id=posted.data.get('id'))
else:
  api.create_tweet(text=tweet)

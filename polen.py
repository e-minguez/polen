import requests, json, tweepy, os, random
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

POLEN_URL = os.getenv("POLEN_URL")

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

page = requests.get(POLEN_URL)
soup = BeautifulSoup(page.content, 'html.parser')

dataDict = {}

data = soup.findAll("label", {"class": "valor"})
dataDict['ciudad'] = data[0].getText(strip=True)
dataDict['fecha'] = data[1].getText(strip=True)
dataDict['datos'] = []

# Tipo, Medicion, Nivel
data = [ tmpdata.getText(strip=True) for tmpdata in soup.findAll("label", {"class": "texto"})[5:] ]

for i in range(0,len(data),3):
  tmpdict = {}
  tmpdict['tipo'] = data[i]
  tmpdict['medicion'] = data[i+1]
  tmpdict['nivel'] = data[i+2]
  dataDict['datos'].append(tmpdict)

# Open the previous json data
try:
  with open('previous.json') as json_file:
    previous = json.load(json_file)
except:
  previous = {}

# If the results are the same, do nothing
if previous == dataDict:
  print("Dupe")
  exit()
# Otherwise, save the file for next execution and continue
else:
  with open('previous.json','w') as json_file:
    json_file.write(json.dumps(dataDict))

#print(json.dumps(dataDict,indent=4))
tweet = random.choice(emojis) + " " + dataDict['ciudad'] + ": " + dataDict['fecha'] + "\n"

for dic in dataDict['datos']:
    for k in dic:
      if k == "tipo":
        tweet += dic[k] + ": "
      elif k == "medicion":
        tweet += dic[k] + " "
      elif k == "nivel":
        if dic[k].startswith("Bajo"):
          tweet += levels["bajo"] + "\n"
        elif dic[k].startswith("Medio"):
          tweet += levels["medio"] + "\n"
        elif dic[k].startswith("Alto"):
          tweet += levels["alto"] + "\n"
        elif dic[k].startswith("Muy alto"):
          tweet += levels["muyalto"] + "\n"

tweet += hashtag

print(tweet)

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create API object
api = tweepy.API(auth)

# Create a tweet
api.update_status(tweet)
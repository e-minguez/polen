import requests, json, tweepy, os, random, xmltodict, time
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY_AVILA")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET_AVILA")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_AVILA")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET_AVILA")

POLEN_URL = os.getenv("POLEN_URL_AVILA")

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

hashtag = "#Ávila"

page = requests.get(POLEN_URL)
doc = xmltodict.parse(page.content)

dataDict = {}

#dataDict['ciudad'] = "Ávila"
dataDict['fecha'] = doc["document"]["list"]["element"]["@fecha"]
dataDict['datos'] = []

for estacion in doc["document"]["list"]["element"]["estacion"]:
  if estacion["@nombre"] == "\u00c1VILA":
    tmpdict = {}
    tmpdict['tipo'] = estacion["tipo_polinico"]["@nombre"].capitalize()
    tmpdict['real'] = estacion["tipo_polinico"]["valor_real"].lower()
    tmpdict['prevision'] = estacion["tipo_polinico"]["valor_previsto"].lower()
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
    for k in dic:
      if k == "tipo":
        tweet += dic[k] + ": "
      elif k == "real":
        if dic[k].startswith("bajo"):
          tweet += levels["bajo"] + "\n"
        elif dic[k].startswith("moderado"):
          tweet += levels["medio"] + "\n"
        elif dic[k].startswith("alto"):
          tweet += levels["muyalto"] + "\n"

tweet += hashtag

print(tweet)

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create API object
api = tweepy.API(auth)

# https://stackoverflow.com/questions/53798094/tweet-strings-via-tweepy
TWEET_LIMIT = 200
print(len(tweet))
if len(tweet) > TWEET_LIMIT:
  to_tweet = []
  while len(tweet) > TWEET_LIMIT:
    cut = tweet[:TWEET_LIMIT]
    to_tweet.append(cut)
    tweet = tweet[TWEET_LIMIT:]
  to_tweet.append(tweet)
  for index, tw in enumerate(to_tweet):
    if index == 0:
      posted = api.update_status(tw)
    else:
      posted = api.update_status(tw,in_reply_to_status_id=posted.id,auto_populate_reply_metadata=True)
else:
  # Create a tweet
  api.update_status(tweet)
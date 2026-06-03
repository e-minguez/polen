import json, os, random, tweepy

EMOJIS = [
    "\U0001f927",  # sneeze
    "\U0001F33E",  # wheat
    "\U0001F33A",  # flower
    "\U0001f4e2",  # loud speaker
    "\U0001F514",  # bell
    "\U0001F509",  # speaker
    "\U0001F4D6",  # open book
    "\U0001F5DE",  # newspaper
    "\U0001F4EC",  # mailbox
]

LEVELS = {
    "bajo":     "\U0001F7E2",  # 🟢
    "moderado": "\U0001F7E1",  # 🟡
    "alto":     "\U0001F534",  # 🔴
}


def create_client(suffix):
    return tweepy.Client(
        consumer_key=os.getenv(f"CONSUMER_KEY_{suffix}"),
        consumer_secret=os.getenv(f"CONSUMER_SECRET_{suffix}"),
        access_token=os.getenv(f"ACCESS_TOKEN_{suffix}"),
        access_token_secret=os.getenv(f"ACCESS_TOKEN_SECRET_{suffix}"),
    )


def is_dupe(city, data):
    try:
        with open(city + ".json") as f:
            previous = json.load(f)
    except Exception:
        previous = {}
    return previous == data


def save_data(city, data):
    with open(city + ".json", "w") as f:
        json.dump(data, f)


_THRESHOLDS = {
    # Source: REA/UCO https://www.uco.es/investiga/grupos/rea/?page_id=262
    "Gramíneas":                   (10, 50),   # Poaceae
    "Olivo":                       (50, 200),  # Olea
    "Plantago":                    (10, 50),
    "Cupresáceas/Taxáceas":        (50, 200),  # Cupressus
    "Plátano de paseo":            (50, 200),  # Platanus
    "Urticaceae (Ortigas)":        (10, 20),   # Urticaceae
    "Quenopodiáceas/Amarantáceas": (10, 20),   # Amaranthaceae
    "Aliso":                       (30, 50),   # Alnus
    "Abedul":                      (30, 50),   # Betula
    "Corylus":                     (30, 50),
    "Fresno":                      (30, 50),   # Fraxinus
    "Pinos":                       (50, 200),  # Pinus
    "Quercus":                     (50, 200),
}
_DEFAULT_THRESHOLDS = (30, 100)


def classify_level(granos, tipo=None):
    g = int(granos or 0)
    low, mid = _THRESHOLDS.get(tipo, _DEFAULT_THRESHOLDS)
    if g < low: return "bajo"
    if g < mid: return "moderado"
    return "alto"


def _twitter_len(text):
    # BMP chars = 1, supplementary (emoji) = 2
    return sum(2 if ord(c) > 0xFFFF else 1 for c in text)


def _split_tweet(text, limit=280):
    chunks, current = [], ""
    for line in text.splitlines():
        candidate = (current + "\n" + line) if current else line
        if _twitter_len(candidate) > limit and current:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def post_thread(client, text):
    reply_to = None
    for chunk in _split_tweet(text):
        kwargs = {"text": chunk}
        if reply_to:
            kwargs["in_reply_to_tweet_id"] = reply_to
        reply_to = client.create_tweet(**kwargs).data["id"]

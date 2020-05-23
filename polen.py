import requests
import json
from bs4 import BeautifulSoup

POLEN_URL = 'http://gestiona.madrid.org/geoserver/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&LAYERS=SPOL_V_CAPTADORES_GIS&QUERY_LAYERS=SPOL_V_CAPTADORES_GIS&STYLES=&BBOX=365560.97254%2C4415910.465472%2C495339.02746%2C4558089.534528&FEATURE_COUNT=50&HEIGHT=493&WIDTH=450&FORMAT=image%2Fpng&INFO_FORMAT=text%2Fhtml&SRS=EPSG%3A23030&X=202&Y=251'
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

print(json.dumps(dataDict,indent=4))

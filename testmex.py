import time
import hashlib
import hmac
from future.builtins import bytes
import urllib.request
import json

import utils.loadconfig as config 



symbol='XBTUSD'

verb    = "POST"
nonce   = str(int(time.time()))
path    = "/api/v1/position/leverage"
data    = '{"symbol":"XBTUSD","leverage":5}'

print(data)

message =  verb + path + nonce + data

#gen sig
signature = hmac.new(bytes(config.SHITMEX_API_SECRET, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()

#build GET req headers
req = urllib.request.Request('https://www.bitmex.com'+path)
req.add_header('api-nonce', nonce)
req.add_header('api-key', config.SHITMEX_API_KEY)
req.add_header('api-signature', signature)
req.add_header('Content-Type', 'application/json')
datab=str.encode(data) #Bytes needed for POST data
resp = urllib.request.urlopen(req, datab)

content     = resp.read()
decodeddata =json.loads(content.decode())

print(decodeddata)

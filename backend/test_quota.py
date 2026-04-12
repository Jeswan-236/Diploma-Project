import urllib.request, json, os
from dotenv import load_dotenv
load_dotenv()

key = os.environ.get('YOUTUBE_API_KEY')
url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id=PkZNo7MFNFg&key={key}'
req = urllib.request.Request(url)

try:
  res = urllib.request.urlopen(req)
  data = json.loads(res.read())
  print('SUCCESS! Quota is available. Result items:', len(data.get('items', [])))
except Exception as e:
  import traceback; traceback.print_exc()

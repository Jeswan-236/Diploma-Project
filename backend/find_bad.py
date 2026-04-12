import os, urllib.request
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])
data = sb.table('videos').select('id, thumbnail_url, title').execute()

for v in data.data:
  if v['thumbnail_url'] and 'http' in v['thumbnail_url']:
    try:
      req = urllib.request.Request(v['thumbnail_url'], headers={'User-Agent': 'Mozilla/5.0'})
      urllib.request.urlopen(req)
    except Exception as e:
      print('BAD THUMBNAIL:', v['title'], e, v['thumbnail_url'])

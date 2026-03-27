import signal
from scholarly import scholarly
import jsonpickle
import json
from datetime import datetime
import os

# 超时 60 秒自动终止
def timeout_handler(signum, frame):
    raise TimeoutError("爬虫超时，结束运行")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

try:
    author: dict = scholarly.search_author_id(os.environ['GOOGLE_SCHOLAR_ID'])
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    
    author['updated'] = str(datetime.now())
    author['publications'] = {v['author_pub_id']:v for v in author['publications']}
    
    os.makedirs('../google-scholar-stats', exist_ok=True)
    
    with open('../google-scholar-stats/gs_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(author, outfile, ensure_ascii=False, indent=2)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": f"{author.get('citedby', 0)}"
    }
    
    with open('../google-scholar-stats/gs_data_shieldsio.json', 'w', encoding='utf-8') as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)

except TimeoutError:
    print("ERROR: 爬虫请求超时")
except Exception as e:
    print(f"ERROR: {str(e)}")

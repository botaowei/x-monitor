import requests
import re
import json
import time
import os

# 配置
TWEET_URL = "https://nitter.net/Pxstar_/status/2014525129548825049"
DATA_FILE = "data.json"

def get_retweet_count():
    # 尝试多个镜像，防止单个失效
   mirrors = [
    "https://nitter.net", 
    "https://nitter.cz", 
    "https://nitter.privacydev.net", 
    "https://nitter.no-logs.com",
    "https://nitter.projectsegfau.lt"
]
    for mirror in mirrors:
        try:
            url = TWEET_URL.replace("https://nitter.net", mirror)
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            match = re.search(r'icon-retweet"></span>\s*([\d,]+)', res.text)
            if match:
                return int(match.group(1).replace(',', ''))
        except:
            continue
    return None

# 读取现有数据
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
else:
    data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}

current_count = get_retweet_count()
now = int(time.time())

if current_count is not None:
    # 逻辑判断
    if current_count != data["lastCount"]:
        # 转发数变化，重置计时
        data["lastChangeTimestamp"] = now
        data["lastCount"] = current_count
    else:
        # 转发数没变，检查是否超过24小时
        elapsed = now - data["lastChangeTimestamp"]
        if elapsed >= 24 * 3600:
            # 归零重置
            data["lastChangeTimestamp"] = now
    
    data["currentCount"] = current_count
    data["lastUpdate"] = now

    # 保存
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

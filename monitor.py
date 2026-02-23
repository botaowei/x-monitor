import requests
import re
import json
import time
import os

# 配置
TWEET_URL = "https://nitter.net/Pxstar_/status/2014525129548825049"
DATA_FILE = "data.json"

def get_retweet_count():
    # 扩大镜像列表，增加成功率
    mirrors = [
        "https://nitter.privacydev.net",
        "https://nitter.cz",
        "https://nitter.perennialte.ch",
        "https://nitter.no-logs.com",
        "https://nitter.net"
    ]
    for mirror in mirrors:
        try:
            url = TWEET_URL.replace("https://nitter.net", mirror)
            print(f"正在尝试镜像: {mirror}")
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            # 兼容不同镜像可能的 HTML 结构
            match = re.search(r'icon-retweet"></span>\s*([\d,.]+)', res.text)
            if match:
                count_str = match.group(1).replace(',', '').replace('.', '')
                return int(count_str)
        except Exception as e:
            print(f"镜像 {mirror} 失败")
            continue
    return None

# 1. 始终先读取或初始化 data 结构
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
        except:
            data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}
else:
    data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}

# 2. 执行抓取
current_count = get_retweet_count()
now = int(time.time())

# 3. 只有抓取成功才更新逻辑
if current_count is not None:
    if current_count != data.get("lastCount", 0):
        print(f"数据变化: {data.get('lastCount')} -> {current_count}")
        data["lastChangeTimestamp"] = now
        data["lastCount"] = current_count
    else:
        elapsed = now - data.get("lastChangeTimestamp", now)
        if elapsed >= 24 * 3600:
            print("24小时无变化，归零重置计时")
            data["lastChangeTimestamp"] = now
    
    data["currentCount"] = current_count
    data["lastUpdate"] = now
    print("抓取成功，准备写入文件")
else:
    # 如果抓取失败，我们也更新一下最后检查时间，确保 data.json 始终被“触碰”过
    data["lastUpdate"] = now
    print("所有镜像抓取失败，保持原有数据")

# 4. 无论成功失败，都写入文件（确保 Git add 能找到文件）
with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=4)

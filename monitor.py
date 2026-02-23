import requests
import re
import json
import time
import os

# 配置
TWEET_URL = "https://nitter.net/Pxstar_/status/2014525129548825049"
DATA_FILE = "data.json"

def get_retweet_count():
    # 备用镜像列表
    mirrors = [
        "https://nitter.net", 
        "https://nitter.cz", 
        "https://nitter.privacydev.net",
        "https://nitter.no-logs.com"
    ]
    for mirror in mirrors:
        try:
            url = TWEET_URL.replace("https://nitter.net", mirror)
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            # 匹配转发数
            match = re.search(r'icon-retweet"></span>\s*([\d,]+)', res.text)
            if match:
                count_str = match.group(1).replace(',', '')
                return int(count_str)
        except Exception as e:
            print(f"镜像 {mirror} 尝试失败: {e}")
            continue
    return None

# 1. 读取或初始化数据
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}
else:
    data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}

# 2. 执行抓取
current_count = get_retweet_count()
now = int(time.time())

# 3. 逻辑判断
if current_count is not None:
    # 如果转发数和上次记录的不一样（增减都算）
    if current_count != data.get("lastCount", 0):
        print(f"检测到变化: {data.get('lastCount')} -> {current_count}，重置计时器")
        data["lastChangeTimestamp"] = now
        data["lastCount"] = current_count
    else:
        # 如果转发数没变，检查是否已经过了 24 小时
        elapsed = now - data.get("lastChangeTimestamp", now)
        if elapsed >= 24 * 3600:
            print("24小时无变化，计时归零，重新开始计时")
            data["lastChangeTimestamp"] = now
            # 这里保持 lastCount 不变，只重置时间起点
    
    data["currentCount"] = current_count
    data["lastUpdate"] = now

    # 4. 保存数据
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print("数据更新成功")
else:
    print("未能获取到数据，跳过本次更新")

import requests
import re
import json
import time
import os

# 配置：这里填入你文章的直接链接
ARTICLE_URL = "https://x.com/i/article/2014421355379486720" 
# 以及分享这篇文章的推文链接（作为备选抓取路径）
TWEET_URL = "https://x.com/Pxstar_/status/2014525129548825049"
DATA_FILE = "data.json"

def get_count_from_nitter(target_path):
    # 扩大镜像列表
    mirrors = [
        "https://nitter.privacydev.net",
        "https://nitter.cz",
        "https://nitter.no-logs.com",
        "https://nitter.perennialte.ch"
    ]
    for mirror in mirrors:
        try:
            # 将 x.com 替换为镜像域名
            url = f"{mirror}{target_path}"
            print(f"正在尝试镜像: {url}")
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            
            # 尝试匹配转发数 (针对推文页面的通用结构)
            match = re.search(r'icon-retweet"></span>\s*([\d,.]+)', res.text)
            if match:
                count_str = match.group(1).replace(',', '').replace('.', '')
                return int(count_str)
            
            # 针对文章页面，如果 Nitter 渲染方式不同，尝试另一种匹配
            # 注：如果 Nitter 不支持文章页，这里可能返回 None
        except Exception as e:
            continue
    return None

# 1. 初始化数据
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
        except:
            data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}
else:
    data = {"lastCount": 0, "lastChangeTimestamp": int(time.time()), "currentCount": 0}

# 2. 执行抓取
# 我们首先尝试抓取分享该文章的推文转发数（这是最稳妥的免费抓取路径）
path = "/Pxstar_/status/2014525129548825049"
current_count = get_count_from_nitter(path)
now = int(time.time())

# 3. 核心倒计时逻辑
if current_count is not None:
    # 逻辑：只要当前的转发总数和上次记录的不一样（不论增减）
    if current_count != data.get("lastCount", 0):
        print(f"转发数发生变动: {data.get('lastCount')} -> {current_count}，重置24小时倒计时。")
        data["lastChangeTimestamp"] = now
        data["lastCount"] = current_count
    else:
        # 如果转发数没变，检查是否超过 24 小时
        elapsed = now - data.get("lastChangeTimestamp", now)
        if elapsed >= 24 * 3600:
            print("24小时内转发数无任何增减，倒计时归零，重新开始计时。")
            data["lastChangeTimestamp"] = now # 重新开始计时
            # 这里可以根据需求决定是否要把 lastCount 同步到当前，
            # 保持 data["lastCount"] = current_count 即可
    
    data["currentCount"] = current_count
    data["lastUpdate"] = now
else:
    print("本次抓取未获取到数据，保持原有倒计时状态。")
    data["lastUpdate"] = now

# 4. 写入文件
with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=4)

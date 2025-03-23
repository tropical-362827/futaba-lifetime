import json
import os
import time
import logging
from pathlib import Path
from datetime import datetime

import requests

# Loggerを作成
logger = logging.getLogger('futaba-crawler')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('output.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("Started!")

# ディレクトリ指定
base_path = Path("./log")
current_time = datetime.now().strftime('%Y-%m-%d-%H%M')

# スレッドリスト読み込み
with open("threads.json", "r") as f:
    threads = json.load(f)
logger.info(f"スレッドリストの長さ: {len(threads)}")

# カタログ取得
catalog_url = "https://may.2chan.net/b/futaba.php?mode=json"
catalog = requests.get(catalog_url).json()
logger.info(f"カタログのスレッド数: {len(catalog["res"])}")

# カタログ保存
with open(base_path / "catalog" / f"{current_time}.json", "w") as f:
    json.dump(catalog, f)

# 新しく監視対象にするスレッド
new_threads = sorted(list(catalog["res"].keys()))[-5:]
threads = list(dict.fromkeys(threads + new_threads))
logger.info(f"新たな監視対象: {new_threads}")

# 巡回
died_threads = []
logger.info(f"巡回({len(threads)}): {threads}")
for thread_num in threads:
    logger.info(f"スレッド巡回: {thread_num}")

    # ログディレクトリの用意
    log_path = base_path / "threads" / thread_num
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    
    # スレッド取得
    thread_url = f"https://may.2chan.net/b/futaba.php?mode=json&res={thread_num}"
    thread = requests.get(thread_url).json()

    # 死亡判定が立っていれば、リストに格納
    if thread["old"] == 1:
        died_threads.append(thread_num)
        logger.info(f"スレッド落ち判定")
    
    # スレッドを保存
    with open(base_path / "threads" / thread_num / f"{current_time}.json", "w") as f:
        json.dump(thread, f)
    
    time.sleep(2)

# スレッド保存
threads = [item for item in threads if item not in died_threads]
with open("threads.json", "w") as f:
    json.dump(threads, f)

logger.info("Finished!")
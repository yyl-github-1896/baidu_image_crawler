#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author: @__walnut__
@Date: 2025/10/07
@Acknowledgement: This code is inspired by https://github.com/wy315700/baidu_image_crawler
"""

import os
import json
import requests
from urllib.parse import quote


def search_img(keyword: str, k: int = 30):
    """
    从百度图片搜索中爬取指定关键词的图片链接，并下载到本地文件夹。

    Args:
        keyword (str): 搜索关键词
        k (int): 最大下载数量（默认 30）
    """
    encoded_kw = quote(keyword)
    search_url = (
        f"https://image.baidu.com/search/acjson"
        f"?tn=resultjson_com&logid=123456&ipn=rj&ct=201326592"
        f"&is=&fp=result&queryWord={encoded_kw}&cl=2&lm=-1&ie=utf-8&oe=utf-8"
        f"&adpicid=&st=-1&z=&ic=0&word={encoded_kw}&s=&se=&tab=&width=&height=&face=0"
        f"&istype=2&qc=&nc=1&fr=&pn=0&rn={k}"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": "https://image.baidu.com/",
    }

    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        resp_js = resp.json()
    except Exception as e:
        print(f"[Error] 请求或解析失败: {e}")
        return

    data_list = resp_js.get("data", [])
    if not data_list:
        print("[Info] 未找到任何图片数据。")
        return

    print(f"[Info] 找到 {len(data_list)} 条数据，准备下载最多 {k} 张图片...")

    count = 0
    for x in data_list:
        url = x.get("thumbURL")
        if not url:
            continue
        try:
            print(f"Downloading ({count+1}/{k}): {url}")
            save_to_disk(url, keyword)
            count += 1
            if count >= k:
                break
        except Exception as e:
            print(f"[Warn] 下载失败: {e}")
            continue

    print(f"[Done] 已完成 {count} 张图片的下载。")


def save_to_disk(url: str, folder: str):
    """
    下载图片到指定文件夹
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)

    filename = url.split("/")[-1].split("?")[0]
    if not filename:
        filename = f"img_{abs(hash(url))}.jpg"

    fpath = os.path.join(folder_path, filename)

    if os.path.exists(fpath):
        print(f"[Skip] 已存在: {fpath}")
        return

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(fpath, "wb") as f:
            f.write(resp.content)
        print(f"[OK] 已保存: {fpath}")
    except Exception as e:
        print(f"[Error] 下载失败: {e}")


if __name__ == "__main__":
    keyword = input("请输入关键词：").strip()
    if keyword:
        try:
            k = int(input("请输入最大下载数量 (默认 30)：") or 30)
        except ValueError:
            k = 30
        search_img(keyword, k)
    else:
        print("关键词不能为空。")

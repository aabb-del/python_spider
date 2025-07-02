

import re ,requests,time# 导入所需要的库
import random
from bs4 import BeautifulSoup
import cloudscraper
import os
import queue


# 直接使用requests获取不到，被反爬了

headers = {
    "cookie" : "_ga=GA1.1.1557907581.1751287763; cf_clearance=Eq2q3d6fH2RT5uxcoLY3qAd8nX7QG5iHwvnHy5sk3jY-1751454976-1.2.1.1-JRUYDkrDK0luR___pMTVE4avgV5dacZxZaTq_HpkFNSypPL5NriLLtq7fwc7FlNYYGWEpDdfdhWhNQsloZ9HvWwJ12_1yY6vs_tdcneLmdUlj84wP1JZtHjrG0SB1Wa9RKwhaKTeC8ZfTCSLkqvVXGt6uY2Kh274IYGeDN5vHHdtZ1jUwUIK6p0hHrceqmyUK3rgxDLqnjauxuqqXYndNquqhEy7X2fQzyMpOQ6IGJB8.TVMvXs7qmoUJjGVkroRF3UrzrGRZ_IMJu8T8I0XvJ39_z906n_dZ8yLtt6a.rA1eYVy1BcUiebaeSpZhzFaatsB81G0sreFhIr.YMR4wOwzYdrX87edkMhzIfzgB1w; session=.eJwNy0EOwiAQBdC7zLopsZaW4TINTP60RAUzsDPeXd_-fchwlj4sjdLqYVAYjCJdY7x7dE7qnEs9Z2kvRxMdaugXRU3Pjomkmx6jPVD_JXggLbxvWxDWfPfiGet-E_igPgmHlUPmhb4_jaYmYQ.aGUVCw.c6HT0v-EA4CtLg-5QYiRnzgxlUE; _ga_2Q92H6XBBP=GS2.1.s1751454981$o2$g1$t1751455628$j60$l0$h",
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding" : "gzip, deflate, br, zstd",
    "accept-language" : "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority":"u=0, i",
    "sec-ch-ua":'"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site":"same-origin",
    "sec-fetch-user":"?1",
    "upgrade-insecure-requests":"1",
    "User-Agent" :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",

}


# target_url="https://www.koipb.com/" # get失败
target_url="https://girl-atlas.com/"  # 成功获取
next_urls = []
detail_urls = []  # 存储图片地址
save_path = r"D:\data\python\koipb_save"
download_number = 0

origion_url_queue = queue.Queue()
detail_url_queue = queue.Queue()


# 获取网页
def get_and_deal_origion(url):
    print(url)
    # 创建实例
    scraper = cloudscraper.create_scraper()
    # 请求url
    response = scraper.get(url)

    bs = BeautifulSoup(response.content, "html.parser")

    # 获取子页面链接
    next_href = bs.select(".page-item .page-link")[-1]['href']
    next_url = target_url + next_href
    origion_url_queue.put(next_url)


    # 获取图像页面链接
    album_href_list = bs.select("div.card")
    for item in album_href_list:

        if(item.select("h4 a") == []):
            continue

        title = item.select("h4 a")[0].text.replace(" ","")
        print(title)

        directory = save_path + "\\" + title
        if (os.path.exists(directory)):
            # 有的话说明已经存在，不再进行后续操作,不需要保存
            print(title+"已存在，跳过")
            continue

        album = item.select("a")[0]['href']
        if "album" in album:
            url = target_url + item.select("a")[0]['href']
            # print(url)
            detail_url_queue.put(url)


# 处理图像页面
def get_and_deal_image(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    bs = BeautifulSoup(response.content, "html.parser")
    title = bs.select(".header-title")[0].text.replace(" ","")
    # print(title)

    directory = save_path+"\\"+title
    if(not os.path.exists(directory)):
        os.makedirs(save_path+"\\"+title)
    else:
        # 有的话说明已经存在，不再进行后续操作
        return

    # 获取图片地址
    images_href = bs.select(".gallery a")
    # print(images_href)
    for item in images_href:
        data_src = item["data-src"]
        name = directory+ "\\" + data_src.split("/")[-1].split("!")[0]
        # print(data_src)
        # print(name)
        if(not os.path.exists(name)):
            get_and_save_image(data_src, name)



def get_and_save_image(url, name):
    print(url)
    global download_number
    download_number = download_number + 1
    print("保存"+ str(download_number) + " " +name+"...")
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        with open(name, 'wb') as f:
            f.write(response.content)
    except:
        print("<UNK>")


def deal_origion_url():
    # @note 这里先一次处理一个页面
    if(not origion_url_queue.empty()):
        url = origion_url_queue.get()
        get_and_deal_origion(url)


def deal_detail_url():
    while(not detail_url_queue.empty()):
        url = detail_url_queue.get()
        get_and_deal_image(url)
        time.sleep(0.1)


def get_loop():
    # 初始页面
    origion_url_queue.put(target_url)
    while(True):
        deal_origion_url()
        deal_detail_url()




if __name__ == '__main__':

    get_loop()
    print("已完成")
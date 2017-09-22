#!/usr/bin/env python
#encoding:utf-8

import requests
import json
import xlwt
import os
import threading
from bs4 import BeautifulSoup
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

TOP_COUNT = 100

class ImageThread(threading.Thread):
    def __init__(self, url, file_name, type_name):
        threading.Thread.__init__(self)
        self.url = url
        self.file_name = file_name
        self.type_name = type_name

    def run(self):
        save_moive_image(self.url, self.file_name, self.type_name)

class FileThread(threading.Thread):
    def __init__(self, sheet, content, row):
        threading.Thread.__init__(self)
        self.sheet = sheet
        self.content = content
        self.row = row

    def run(self):
        write_to_excel(self.sheet, self.content, self.row)


def get_http_data(url):
    r = myRequest.get(url=url)
    r.encoding = 'utf-8'
    return r.text

def get_total_count(type_id):
    url = 'https://movie.douban.com/j/chart/top_list_count?type={}&interval_id=100%3A90'.format(type_id)
    count_data = json.loads(get_http_data(url))
    #{"playable_count":221,"total":407,"unwatched_count":407}
    return count_data['total']

def save_moive_image(url, file_name, type_name):
    image_path = os.path.join(os.getcwd(), 'images/' + type_name + '/' + file_name.replace('/','-') +'.jpg')
    r = myRequest.get(url=url)
    image_content = r.content
    image_file = open(image_path, 'wb')
    image_file.write(image_content)
    image_file.close()

def write_to_excel(sheet, content, row):
    for x in range(0, len(content)):
        # print('row:'+str(row)+' content:'+content[x])
        sheet.write(row, x, content[x])

def get_moive_data(sheet, type_id, sheet_name, count = 0):
    global wbk
    total = get_total_count(type_id)
    if count > 0 and count < total:
        total = count
    image_index = 1
    row0 = [u'名称', u'评分', u'国家', u'类型', u'上映时间', u'相关地址']
    write_to_excel(sheet, row0, 0)
    threads = []
    for i in range(0, total, 20):
        url = 'https://movie.douban.com/j/chart/top_list?type={}&interval_id=100%3A90&action=&start={}&limit={}'.format(type_id, i, 20)
        moive_datas = json.loads(get_http_data(url))
        for item in moive_datas:
            file_path = (os.getcwd() + '/images/' + sheet_name).encode('gb2312')
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            image_thread = ImageThread(item['cover_url'], item['title'], sheet_name)
            image_thread.start()
            threads.append(image_thread)
            # save_moive_image(item['cover_url'], image_index)
            address = ','.join(item['regions'])
            types = ','.join(item['types'])
            excel_content = [item['title'], item['score'], address, types, item['release_date'], item['url']]
            file_thread = FileThread(sheet, excel_content, image_index)
            file_thread.start()
            threads.append(file_thread)
            image_index += 1
    for t in threads:
        t.join()
    print(sheet_name+'下载完成')

def get_all_types():
    url = 'https://movie.douban.com/typerank?type_name=%E5%89%A7%E6%83%85&type=11&interval_id=100:90&action='
    html = get_http_data(url)
    soup = BeautifulSoup(html, 'lxml')
    datas = soup.find_all(href=re.compile('typerank'))
    all_types = []
    for item in datas:
        temp = str(item)
        start_pos = temp.index('?')+1
        end_pos = temp.index('>')-1
        lst = re.split('&amp;|=', temp[start_pos:end_pos])
        dic = {}
        for i in range(0, len(lst), 2):
            dic[lst[i]] = lst[i+1]
        all_types.append(dic)
    return all_types

def main():
    global wbk
    moive_types = get_all_types()
    wbk = xlwt.Workbook(encoding='utf-8')
    if sys.platform.find('win32') >= 0:
        for item in moive_types:
            sheet = wbk.add_sheet(item['type_name'])
            get_moive_data(sheet, item['type'], item['type_name'], TOP_COUNT)
    else:
        from multiprocessing import Pool
        p = Pool()
        for item in moive_types:
            sheet = wbk.add_sheet(item['type_name'])
            p.apply_async(get_moive_data, args=(sheet, item['type'], item['type_name'], TOP_COUNT, ))
        p.close()
        p.join()    
    print('全部下载完成')
    wbk.save('moives.xls')

if __name__ == "__main__":
    global myRequest

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    myRequest = requests.session()
    myRequest.headers.update(headers)

    main()

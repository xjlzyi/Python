#!/usr/bin/env pyhton
#encoding: utf-8

import os
import requests
import json
import urllib, urllib2
import re
import sys
import math
import threading
import ssl
import time
import subprocess
import xml.dom.minidom
import xlwt
from PIL import Image
from matplotlib import pyplot as plt

DEBUG = True
imagePath = os.path.join(os.getcwd(), 'qrcode.jpg')

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''
push_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'

BaseRequest = {}

ContactList = []
My = []
SyncKey = []

def getUUID():
    global uuid

    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()),
    }

    r = myRequests.get(url=url, params=params)
    r.encoding = 'utf-8'
    data = r.text

    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, data)

    code = pm.group(1)
    uuid = pm.group(2)

    if code == '200':
        return True
    return False

def showQRImage():
    global tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    r = myRequests.get(url=url, params=params)

    tip = 1

    f = open(imagePath, 'wb')
    f.write(r.content)
    f.close()
    time.sleep(1)

    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', imagePath])
    elif sys.platform.find('win32') >= 0:
        img = Image.open(imagePath)
        # img.show()
        fig = plt.figure()
        ax = fig.add_subplot(121)
        ax.imshow(img)
        plt.show(block=False)
    else:
        subprocess.call(['xdg-open', imagePath])

    print('请使用微信扫描二维码登录')

def waitForLogin():
    global tip, base_uri, redirect_uri, push_uri

    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (tip, uuid, int(time.time()))
    r = myRequests.get(url=url)
    r.encoding = 'utf-8'
    data = r.text

    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)

    code = pm.group(1)

    if code == '201':
        print('扫描成功，请在手机上点击确认登录')
        tip = 0
    elif code == '200':
        print('正在登录...')
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, data)
        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]

        services = [
            ('wx2.qq.com', 'webpush2.weixin.qq.com'),
            ('qq.com', 'webpush.weixin.qq.com'),
            ('web1.wechat.com', 'webpush1.wechat.com'),
            ('web2.wechat.com', 'webpush2.wechat.com'),
            ('wechat.com', 'webpush.wechat.com'),
            ('web1.wechatapp.com', 'webpush1.wechatapp.com'),
        ]
        push_uri = base_uri
        for (searchUrl, pushUrl) in services:
            if base_uri.find(searchUrl) >= 0:
                push_uri = 'https://%s/cgi-bin/mmwebwx-bin' % pushUrl
                break

        if sys.platform.find('darwin') >= 0:
            os.system("osascript -e 'quit app \"Preview\"'")
    elif code == '408':
        pass

    return code

def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest

    r = myRequests.get(url=redirect_uri)
    r.encoding = 'utf-8'
    data = r.text

    doc = xml.dom.minidom.parseString(data)
    root = doc.documentElement

    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data

    if not all((skey, wxsid, wxuin, pass_ticket)):
        return False

    BaseRequest = {
        'Uin': int(wxuin),
        'Sid': wxsid,
        'Skey': skey,
        'DeviceID': deviceId,
    }
    return True

def responseState(func, BaseResponse):
    ErrMsg = BaseResponse['ErrMsg']
    Ret = BaseResponse['Ret']
    if DEBUG or Ret != 0:
        print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False
    return True

def webwxinit():
    url = (base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time())) )
    params  = {'BaseRequest': BaseRequest }
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, data=json.dumps(params), headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
        f.write(r.content)
        f.close()

    global ContactList, My, SyncKey
    dic = data
    ContactList = dic['ContactList']
    My = dic['User']
    SyncKey = dic['SyncKey']

    state = responseState('webwxinit', dic['BaseResponse'])
    return state

def webwxgetcontact():
    url = (base_uri + 
        '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            pass_ticket, skey, int(time.time())) )
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url,headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
        f.write(r.content)
        f.close()

    dic = data
    MemberList = dic['MemberList']

    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ["newsapp", "fmessage", "filehelper", "weibo", "qqmail", "tmessage", "qmessage", "qqsync", "floatbottle", "lbsapp", "shakeapp", "medianote", "qqfriend", "readerapp", "blogapp", "facebookapp", "masssendapp",
                    "meishiapp", "feedsapp", "voip", "blogappweixin", "weixin", "brandsessionholder", "weixinreminder", "wxid_novlwrv3lqwv11", "gh_22b87fa7cb3c", "officialaccounts", "notification_messages", "wxitil", "userexperience_alarm"]
    for i in range(len(MemberList) - 1, -1, -1):
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
            MemberList.remove(Member)
        elif Member['UserName'] in SpecialUsers:  # 特殊账号
            MemberList.remove(Member)
        elif Member['UserName'].find('@@') != -1:  # 群聊
            MemberList.remove(Member)
        elif Member['UserName'] == My['UserName']:  # 自己
            MemberList.remove(Member)

    return MemberList

def syncKey():
    SyncKeyItems = ['%s_%s' % (item['Key'], item['Val'])
                    for item in SyncKey['List']]
    SyncKeyStr = '|'.join(SyncKeyItems)
    return SyncKeyStr

def syncCheck():
    url = push_uri + '/sysnccheck?'
    params = {
        'skey': BaseRequest['Skey'],
        'sid': BaseRequest['Sid'],
        'uin': BaseRequest['Uin'],
        'deviceId': BaseRequest['DeviceID'],
        'synckey': syncKey(),
        'r': int(time.time()),
    }

    r = myRequests.get(url=url, params = params)
    r.encoding = 'utf-8'
    data = r.text

    # window.synccheck={retcode:"0",selector:"2"}
    regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
    pm = re.search(regx, data)

    retcode = pm.group(1)
    selector = pm.group(1)

    return selector

def webwxsync():
    global SyncKey

    url = base_uri + '/webwxsync?lang=zh_CN&skey=%s&sid=%s&pass_ticket=%s' % (
        BaseRequest['Skey'], BaseRequest['Sid'], urllib.quote_plus(pass_ticket))
    params = {
        'BaseRequest': BaseRequest,
        'SyncKey': SyncKey,
        'rr': ~int(time.time()),
    }
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, data=json.dumps(params))
    r.encoding = 'utf-8'
    data = r.json()

    dic = data
    SyncKey = dic['SyncKey']

    state = responseState('webwxsync', dic['BaseResponse'])
    return state

def heartBeatLoop():
    while True:
        selector = syncCheck()
        if selector != '0':
            webwxsync()
        time.sleep(1)

# def writeToExcel():
#     wbk = xlwt.Workbook()
#     sheet = wbk.add_sheet('sheet 1')
#     sheet.write()
#     wbk.save()

def main():
    global myRequests
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    headers = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    myRequests = requests.Session()
    myRequests.headers.update(headers)

    if not getUUID():
        print('获取uuid失败')
        return

    print('正在获取二维码图片...')
    showQRImage()

    while waitForLogin() != '200':
        pass

    os.remove(imagePath)
    if not login():
        print('登录失败')
        return

    if not webwxinit():
        print('初始化失败')
        return

    MemberList = webwxgetcontact()

    threading.Thread(target=heartBeatLoop)

    MemberCount = len(MemberList)
    print('通讯录共%s位好友' % MemberCount)

    d = {}
    imageIndex = 0
    wbk = xlwt.Workbook(encoding='utf-8')
    sheet = wbk.add_sheet('sheet1')
    if not os.path.exists(os.getcwd() + '\\image'):
        os.makedirs(os.getcwd() + '\\image')
    for Member in MemberList:
        imageIndex = imageIndex + 1
        name = os.path.join(os.getcwd(), 'image\\'+str(imageIndex)+'.jpg')
        # name = '/home/test/Desktop/friendImage/image'+str(imageIndex)+'.jpg'
        imageUrl = 'https://wx.qq.com'+Member['HeadImgUrl']
        r = myRequests.get(url=imageUrl,headers=headers)
        imageContent = (r.content)
        fileImage = open(name,'wb')
        fileImage.write(imageContent)
        fileImage.close()
        print('正在下载第：'+str(imageIndex)+'位好友头像')
        d[Member['UserName']] = (Member['NickName'], Member['RemarkName'])
        city = (Member['Province'],Member['City'])
        city = 'nocity' if city == '' else  city
        name = Member['NickName']
        name = 'noname' if name == '' else  name
        sex = '男' if Member['Sex'] == 1 else '女'
        sign = Member['Signature']
        # sign = 'nosign' if sign == '' else  sign
        remark = Member['RemarkName']
        # remark = 'noremark' if remark == '' else remark
        alias = Member['Alias']
        alias = 'noalias' if alias == '' else alias
        nick = Member['NickName']
        nick = 'nonick' if nick == '' else nick
        # print(name,'  ^+*+^  ',city,'  ^+*+^  ',Member['Sex'],' ^+*+^ ',Member['StarFriend'],' ^+*+^ ',sign,' ^+*+^ ',remark,' ^+*+^ ',alias,' ^+*+^ ',nick )
        l = [name, city, sex, sign, remark]
        for i in range(0, len(l)):
            sheet.write(imageIndex - 1, i, l[i])
        # sheet.write(0, name) #city, Member['Sex'], Member['StarFriend'], sign, remark, alias, nick)
    wbk.save('wx.xls')

if __name__ == "__main__":
    main()

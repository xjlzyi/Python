# -*- coding:utf-8 -*-
import urllib
import urllib2
import re
import thread

#糗事百科爬虫类
class QSBK:
	def __init__(self):
		self.pageIndex = 1
		self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		#init headers
		self.headers = { 'User-Agent' : self.user_agent }
		#save per page content
		self.stories = []
		self.enable = False

	#传入某一页的索引获得页面代码
	def getPage(self, pageIndex):
		try:
			url = 'http://www.qiushibaike.com/hot/page/'+str(pageIndex)
			#build request
			request = urllib2.Request(url, headers = self.headers)
			response = urllib2.urlopen(request)
			#The page is converted to UTF-8 encoding
			pageCode = response.read().decode('utf-8')
			return pageCode
		except urllib2.URLError, e:
			if hasattr(e, "reason"):
				print u"连接糗事百科失败,错误原因", e.reason
				return None

	#传入某一页代码，返回本页不带图片的段子列表
	def getPageItems(self, pageIndex):
		pageCode = self.getPage(pageIndex)		
		if not pageCode:
			print u"页面加载失败...."
			return None

		pattern = re.compile('<div class="author clearfix">.*?href.*?<img src.*?title=.*?<h2>(.*?)</h2>.*?' +
			'<div class="content">(.*?)</div>.*?' + 
			'<div class="stats">.*?<i class="number">(.*?)</i>.*?<i class="number">(.*?)</i>',re.S)
		items = re.findall(pattern, pageCode)
		#用来存储每页的段子们
		pageStories = []
		for item in items:
			replaceBR = re.compile('<br/>')
			text = re.sub(replaceBR, "\n", item[1])
			#item[0]是一个段子的发布者，item[1]是内容,item[2]是点赞数,item[3]是评论
			pageStories.append([item[0].strip(), text.strip(), item[2].strip(), item[3].strip()])
		return pageStories
	
	#加载并提取页面的内容，加入到列表中
	def loadPage(self):
		if self.enable == True:
			if len(self.stories) < 2:
				pageStories = self.getPageItems(self.pageIndex)
				if pageStories:
					self.stories.append(pageStories)
					self.pageIndex += 1

	#调用该方法，每次敲回车打印输出一个段子
	def getOneStory(self, pageStories, page):
		#遍历一页的段子
		for story in pageStories:
			input = raw_input()
			#每当输入回车一次，判断一下是否要加载新页面
			self.loadPage()
			#如果输入Q则程序结束
			if input == "Q" or input == "q":
				self.enable = False
				return

			print u"第%d页\t发布人:%s\t赞:%s\t评论:%s\n%s" %(page,story[0],story[2],story[3],story[1])

	#开始方法
	def start(self):
		print u"正在读取糗事百科,按回车查看新段子，Q退出"
		self.enable = True
		self.loadPage()
		#局部变量，控制当前读到了第几页
		nowPage = 0
		while self.enable:
			print len(self.stories)
			if len(self.stories) > 0:
				#从全局list中获取一页的段子
				pageStories = self.stories[0]
				nowPage += 1
				#将全局list中第一个元素删除，因为已经取出
				del self.stories[0]
				self.getOneStory(pageStories, nowPage)

spider = QSBK()
spider.start()
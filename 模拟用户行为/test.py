# -*- coding: utf-8 -*-
import time,random,requests,json
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

class View_Bot:
	"""一个用于测试站点的bot"""
	#初始化参数 只需给出测试站点即可
	def __init__(self,url,name):
		# super(View_Bot,self).__init__()
		self.name = name
		self.count = 0
		self.url = url
		self.profile = webdriver.FirefoxProfile()
		self.profile.set_preference("network.proxy.type",1)
		self.profile.set_preference("general.useragent.site_specific_overrides",True)
		self.profile.set_preference("general.useragent.updates.enabled",True)
		self.options = webdriver.FirefoxOptions()
		self.options.add_argument('-headless')
		self.options.add_argument('--disable-gpu')
		self.driver = webdriver.Firefox(executable_path='geckodriver',firefox_options=self.options,firefox_profile=self.profile)
		
	#退出时关闭浏览器
	def __del__(self):
		self.driver.quit()
	#拖动滚动条 模仿浏览
	def fake_view(self,step):
		links=self.driver.find_elements_by_xpath("//a")
		if step==0:
			for x in range(1):
				self.driver.execute_script("arguments[0].scrollIntoView(false);",random.choice(links))
				# time.sleep(5)
				rand=random.randint(3,7)
				time.sleep(rand)
		elif step==1:
			for x in range(1):
				self.driver.execute_script("arguments[0].scrollIntoView(false);",random.choice(links))
				# time.sleep(10)
				rand=random.randint(7,14)
				time.sleep(rand)
		elif step==2:
			for x in range(1):
				self.driver.execute_script("arguments[0].scrollIntoView(false);",random.choice(links))
				# time.sleep(14)
				rand=random.randint(10,17)
				time.sleep(rand)

	#切换代理
	def switch_proxy(self):
		try:
			url_proxy='http://alwb.cqhxcm.com/getgateway_zm?type=socks5'
			r=requests.sesion()
			r.keep_alive = False
			r.get(url_proxy)
			res=json.loads(r.text)
			ip=res['data']['ip']
			port=res['data']['port']
			self.driver.get('about:config')
			script = '''
			var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
			prefs.setCharPref("network.proxy.socks","{ip}");
			prefs.setIntPref("network.proxy.socks_port",{port});'''.format(ip=ip , port=port)
			self.driver.execute_script(script)
			time.sleep(0.2)
		except:
			time.sleep(2)
	#随机读取一个UA
	def generate_user_agent(self,file):
		f=open(file,'r').read().split('\n')
		useragent=random.choice(f)
		return useragent
	#切换UA
	def switch_user_agent(self,useragent):
		self.driver.get('about:config')
		script = '''
		var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
		prefs.setCharPref("general.useragent.override","{useragent}");'''.format(useragent=useragent)
		self.driver.execute_script(script)
		time.sleep(0.2)
	#浏览内容页
	def view(self):
		try:
			self.driver.get(self.url)
			# print "[+] "+'Step 1'
			self.fake_view(0)
			self.AD_view()
			self.count += 1
			main_windows=self.driver.current_window_handle
			all_windows=self.driver.window_handles
			# self.driver.close()
			for handle in all_windows:
				if handle != main_windows:
					self.driver.switch_to.window(handle)
			for i in range(1,3):
				self.fake_view(i)
				self.click_link()
			time.sleep(5)
			print '[+]{name} finished {round}'.format(name=self.name , round=str(count))
		except Exception as e:
			print e
	#浏览广告位
	def AD_view(self):
		try:
			ad = self.driver.find_elements_by_xpath('//iframe[@allowtransparency="true"]')
			frame = random.choice(ad)
			self.driver.switch_to.frame(frame)
			self.click_link()
			time.sleep(5)
		except Exception as e:
			pass
	#点击链接
	def click_link(self):
		try:
			# print 'Curr_url: '+self.driver.current_url
			links=self.driver.find_elements_by_xpath("//a")

			if not links:
				pass
			for x in links:
				if 'none' in x.get_attribute('style'):
					links.remove(x)
					
			link=random.choice(links)
			# print 'Next_url: '+link.get_attribute('href')
			self.driver.execute_script("arguments[0].scrollIntoView(false);",link)
			# WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(link))
			time.sleep(2)
			actions = ActionChains(self.driver)
			actions.move_to_element(link)
			actions.click(link)
			actions.perform()
			# print '*'*10+'Next turn'+'*'*10
		except Exception as e:
			print e
	#调用函数
	def run(self):
		for x in range(1000):
			self.switch_user_agent(self.generate_user_agent('./ua_lib'))
			# print "ua ok"
			self.switch_proxy()
			# print "proxy ok"
			self.view()
#入口函数	
def start1(url,name):
	bot=View_Bot(url,name)
	bot.run()

if __name__ == '__main__':
	url='http://www.e4718h.cn/archives/1075'
	for y in range(1):
		Process(target=start1,args=(url,'Process{}'.format(y))).start()
		print 'Process{} Start'.format(y)
	# bot=View_Bot(url)
	# bot.run()
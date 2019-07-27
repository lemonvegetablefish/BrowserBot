# -*- coding: utf-8 -*-
from multiprocessing import Process,JoinableQueue,Event
from selenium import webdriver
import random
import time
import re
import requests
import json

def Producer(event,q):
	profile = webdriver.FirefoxProfile()
	profile.set_preference('network.proxy.type',1)
	profile.set_preference('browser.cache.disk.enable',False)
	profile.set_preference('dom.ipc.plugins.enabled', False)
	profile.set_preference("general.useragent.site_specific_overrides",True)
	profile.set_preference("general.useragent.updates.enabled",True)
	profile.set_preference("general.useragent.override","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0")
	profile.update_preferences()
	options = webdriver.FirefoxOptions()
	options.add_argument('-headless')
	options.add_argument('--disable-gpu')
	driver = webdriver.Firefox(executable_path='geckodriver' , firefox_options=options, firefox_profile=profile)
	driver.set_page_load_timeout(20)
	print '[+] Producer waiting'
	event.wait()
	event.clear()
	while True:
		
		if q.qsize()<200:
			proxy_list=get_proxy()
			for proxy in proxy_list:
				if test_proxy(driver,proxy)==1:
					q.put_nowait(proxy)
					print '[+] Proxy num ',q.qsize()
			# s='127.0.0.1:1080'
			# q.put(s)
			event.set()
		else:
			event.set()
	

def Consumer(event,q,phone_list):
	event.set()
	phone_group = list_divide(phone_list,5)
	phone_error = list()
	print '[+] Setting config'
	profile = webdriver.FirefoxProfile()
	profile.set_preference('network.proxy.type',1)
	profile.set_preference("general.useragent.site_specific_overrides",True)
	profile.set_preference("general.useragent.updates.enabled",True)
	profile.set_preference("general.useragent.override","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0")
	profile.update_preferences()
	options = webdriver.FirefoxOptions()
	options.add_argument('-headless')
	options.add_argument('--disable-gpu')
	driver = webdriver.Firefox(executable_path='geckodriver' , firefox_options=options , firefox_profile=profile)
	driver.set_page_load_timeout(20)
	while True:
		if event.is_set():
			for phone in phone_group: 
				proxy = q.get()
				for x in verify_act(driver,phone,proxy):
					phone_error.append(x)
			phone_tmp=list_divide(phone_error,5)
			for phone in phone_tmp:
				proxy = q.get()
				verify_act(driver,phone,proxy)
				break
		else: 
			time.sleep(1)
	driver.quit()

def verify_act(driver,phone_group,proxy):

	phone_error = list()

	ip = proxy.split(':')[0]
	port = proxy.split(':')[1]
	driver.get('about:config')
	script = '''
	var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
	prefs.setCharPref("network.proxy.socks",{ip});
	prefs.setIntPref("network.proxy.socks_port",{port});'''.format(ip='"'+ip+'"' , port=port)
	driver.execute_script(script)
	print '[+] Switching proxy '+proxy
	time.sleep(1)

	try:
		for i in phone_group:
			driver.delete_all_cookies()
			driver.get('https://passport.meituan.com/account/unitivesignup')
			# print '[+] Verifying '+i
			mobile=driver.find_element_by_name('mobile')
			mobile.clear()
			mobile.send_keys(i)
			time.sleep(0.1)
			button = driver.find_element_by_css_selector("[class='btn-normal btn-mini verify-btn J-verify-btn']")
			button.click()
			time.sleep(0.2)
			button.click()
			time.sleep(1)

			pattern='<span class="f1 verify-tip.*>(.*?)</span>'
			res=re.findall(pattern,driver.page_source)
			if res[0]==u'请输入验证码':
				data=i+'#'
				write(data)
				print data
			elif res[0]==u'该手机号已经注册，请直接登录或找回密码':
				print 'reg'
				# write(data)
				# print data
			else:
				print res[0]
				phone_error.append(i)
				print len(phone_error)

			driver.delete_all_cookies()
			time.sleep(5)
			
		
	except Exception as e:
		print e
		for x in phone_group:
			phone_error.append(x)

	return phone_error

def test_proxy(driver,proxy):
	# print '[+] Testing '+ proxy
	ip = proxy.split(':')[0]
	port = proxy.split(':')[1]
	driver.get('about:config')
	script = '''
	var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
	prefs.setCharPref("network.proxy.socks",{ip});
	prefs.setIntPref("network.proxy.socks_port",{port});'''.format(ip='"'+ip+'"' , port=port)
	driver.execute_script(script)
	time.sleep(1)
	try:
		driver.delete_all_cookies()
		driver.get('https://passport.meituan.com/account/unitivesignup')
		if '403 Forbidden' not in driver.page_source:
			driver.delete_all_cookies()
			return 1
		else:
			driver.delete_all_cookies()
			return -1
	except:
		driver.delete_all_cookies()
		return -2

def list_divide(listTemp, n):
	for i in range(0, len(listTemp), n):
		yield listTemp[i:i + n]

def get_proxy():
	url='http://webapi.http.zhimacangku.com/getip?num=200&type=1&pro=0&city=0&yys=0&port=2&pack=54494&ts=0&ys=0&cs=0&lb=3&sb=0&pb=45&mr=2&regions='
	req=requests.get(url)
	proxy_list1=req.content.split()
	if  len(proxy_list1) < 150:
		print '[+] Adding white list'
		add_white_list()
		req=requests.get(url)
		proxy_list1=req.content.split()
	return proxy_list1

def add_white_list():
	try:
		get_ip_url='http://webapi.http.zhimacangku.com/getip?num=200&type=1&pro=0&city=0&yys=0&port=2&pack=54494&ts=0&ys=0&cs=0&lb=3&sb=0&pb=45&mr=2&regions='
		res=requests.get(get_ip_url)
		s=json.loads(res.content)
		ip_pattern='[0-9].*[0-9]'
		my_ip=re.findall(ip_pattern, s['msg'])[0]
		set_white_list_url='web.http.cnapi.cc/index/index/save_white?neek=72453&appkey=ecbc77520ee96d626ad4d42c05f60328&white='+my_ip
		r=requests.get(set_white_list_url)
		print '[+] Add white list success!'
	except:
		pass

def write(data):
	# with open('result.json','a+') as f:
	# 	json.dump(data,f)
	with open('result','a+') as f:
		f.write(data)

def get_phone(file):
	f=open(file,'r')
	phone_list=f.readlines()
	f.close()
	x=list()
	for i in phone_list:
		x.append(i.replace('\n','').replace('\r',''))
	return x

def main():
	file = './mt.txt'#sys.argv[1]
	thread_num = 40

	phone_list = get_phone(file)
	random.shuffle(phone_list)
	num = len(phone_list)/thread_num
	phone_divide = list_divide(phone_list,num)
	print '[+] Read Phone OK!'

	event = Event() 
	q = JoinableQueue()
	for phone_tmp in phone_divide:
		Process(target=Consumer,args=(event,q,phone_tmp)).start()

	# Producer(event,q)
	for i in range(10):
		Process(target=Producer,args=(event,q)).start()

if __name__ == '__main__':
	main()
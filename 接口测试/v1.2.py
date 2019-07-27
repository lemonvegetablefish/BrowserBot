# -*- coding: utf-8 -*-
from multiprocessing import Process,JoinableQueue,Event
from selenium import webdriver
import random,time,re,requests,json,io


def Writer(q_write):
	with io.open('./result'+time.strftime("%m-%d_%H:%M:%S"), 'wb') as fp:
		while True:
			blk_data = q_write.get()
			if not isinstance(blk_data, bytearray):
				break
			fp.write(blk_data)


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
			for proxy in get_proxy():
				if test_proxy(driver,proxy)==1:
					q.put_nowait(proxy)
					print '[+] Proxy num ',q.qsize()
				event.set()
		else:
			event.set()
	

def Consumer(event,q,phone_list,q_write):
	event.set()
	phone_group = list_divide(phone_list,5)
	phone_error = list()
	print '[+] Starting Firefox'
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
				for x in verify_act(driver,phone,proxy,q_write):
					phone_error.append(x)
			phone_tmp=list_divide(phone_error,5)
			for phone in phone_tmp:
				proxy = q.get()
				verify_act(driver,phone,proxy)
				break
		else: 
			time.sleep(1)
	driver.quit()

def verify_act(driver,phone_group,proxy,q_write):

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
				data=bytearray(i+'#')
				print data
				q_write.put(data)
			elif res[0]==u'该手机号已经注册，请直接登录或找回密码':
				pass
			elif res[0]==u'已发送，1分钟后可重新获取。':
				data=bytearray(i+'#')
				print data
				q_write.put(data)
			else:
				print res[0]
				phone_error.append(i)
				# print len(phone_error)

			driver.delete_all_cookies()
			time.sleep(5)
			
		
	except Exception as e:
		print e
		for x in phone_group:
			phone_error.append(x)

	return phone_error

def test_proxy(driver,proxy):
	# print '[+] Testing '+ proxy
	try:
		ip = proxy.split(':')[0]
		port = proxy.split(':')[1]
	except:
		return -3
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
	
	url='http://alwb.cqhxcm.com/getgateway_zm?type=socks5&qcnt=10'
	req=requests.get(url)
	res=json.loads(req.text)
	proxy_list=list()
	try:
		for i in res['data']:
			proxy_list.append(str(i['ip']+':'+i['port']))
		return proxy_list
	except :
		time.sleep(0.5)
	

def get_phone(file):
	f=open(file,'r')
	phone_list=f.readlines()
	f.close()
	x=list()
	for i in phone_list:
		x.append(i.replace('\n','').replace('\r',''))
	return x

def main():
	file = './phone2.txt'#sys.argv[1]
	thread_num = 20

	phone_list = get_phone(file)
	random.shuffle(phone_list)
	num = len(phone_list)/thread_num
	phone_divide = list_divide(phone_list,num)
	print '[+] Read Phone OK!'

	event = Event() 
	q = JoinableQueue()
	q_write = JoinableQueue()
	for phone_tmp in phone_divide:
		Process(target=Consumer,args=(event,q,phone_tmp,q_write)).start()

	for i in range(5):
		Process(target=Producer,args=(event,q)).start()

	Process(target=Writer,args=(q_write,)).start()

if __name__ == '__main__':
	main()
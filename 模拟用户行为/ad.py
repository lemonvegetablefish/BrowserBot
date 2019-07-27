from selenium import webdriver
import time,random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

url='http://www.e4718h.cn/archives/1075'
profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.site_specific_overrides",True)
profile.set_preference("general.useragent.updates.enabled",True)
profile.set_preference("general.useragent.override","Mozilla/5.0 (Linux; Android 8.1; PAR-AL00 Build/HUAWEIPAR-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044304 Mobile Safari/537.36 MicroMessenger/6.7.3.1360(0x26070333) NetType/WIFI Language/zh_CN Process/tools")

options = webdriver.FirefoxOptions()
options.add_argument('-headless')
options.add_argument('--disable-gpu')
driver = webdriver.Firefox(executable_path='geckodriver',firefox_options=options,firefox_profile=profile)
driver.get(url)
xf = driver.find_elements_by_xpath('//iframe[@allowtransparency="true"]')
frame=random.choice(xf)
print len(xf)
# print frame.get_attribute("src")
driver.switch_to.frame(frame)
print driver.current_url
links= driver.find_elements_by_xpath('//a')
# for i in links:
# 	print i.get_attribute("href")
driver.quit()
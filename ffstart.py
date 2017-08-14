
"""
Данный файл будет реализовывать запуск браузера (мозилы) 
переход на сдо , сохранения кукисов , и сборки полной ссылки до страницы 
авторизации 
"""

#!/usr/bin/env python3
import sys
import requests
from selenium.webdriver.common.proxy import * # эта бибилиотека нужна ждя пуска мозилы через порт 8080
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from browsermobproxy  import Server, Client # попробую реализовать схему скрипт firefox->browsermobproxy->burpsuite


#====================================================================================
class Config_firefox_start():
    """
    Без этих настроек proxy firefox не запускался 
    через Burpsuite т.к настройки в запускаемой копии 
    firefox настраивались по умолчанию на работу без прокси .
    Заебался расшифровывать модули библиотеки selenium
    """
    
    def __init__(self,link_url): # link_url при создании обЪекта передаю нужный адрес сайта
        self.url      = link_url # link_url хранит адрес сайта который нужен для перехода

        """ настройка вкладки "Сеть" запускаемого браузера"""
        self.myProxy  = "localhost:8081"
        self.proxy_my = Proxy({
        'proxyType'   : ProxyType.MANUAL,
        'httpProxy'   : self.myProxy,
        'ftpProxy'    : self.myProxy,
        'sslProxy'    : self.myProxy,
        'socksProxy'  : self.myProxy,   
        'noProxy'     : '' # set this value as desired
        })
    
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("network.proxy.type", 1)
        self.profile.set_preference("network.proxy.http", "localhost")
        self.profile.set_preference("network.proxy.http_port", 8081)
        self.profile.set_proxy(self.proxy_my)

        """Запуск браузера с настроенными настройками(prifile)и переход на сайт"""
        self.driver = webdriver.Firefox(self.profile)
        self.driver.get(self.url)

#==================================================================================

class BMP_FF():
    """
    Класс для работы браузера Firefox через прокси browsermobproxy
    для перехвата и анализа Get запросов.
    Разобраться как удалять har
    разобраться как удалять экземпляр класса с помощью del
    """
 
    def __init__(self):
        """инициализация настроек браузера Firefox для работы через прокси"""
        #путь прописывать полностью от home до бинарника который скачивается отдельно не через pip install
        self.bmpproxy = Server(r'//home//sirius//project//python_sir//SBBs_sdo//lib//python3.5//site-packages//browsermob-proxy//bin//browsermob-proxy',{'port':8082}) # указываю  путь к  бинарнику и на каком порту слушать трафик
        self.bmpproxy.start() # start browsermobproxy
        self.bmp_port = self.bmpproxy.create_proxy() # назначение порта неизвестно
        self.resp = requests.post('http://localhost:8082/proxy',{}) # отправляю запрос для получения №порта на котором поднял проксик browsermobproxy
        self.browser_port = self.resp.json()['port'] # через этот порт работает браузер
        self.port_ff_net = 'localhost:' + str(self.browser_port) # получаю строку типа "localhost : 8082"

        self.proxy_my_ff = Proxy({
            'proxyType' : ProxyType.MANUAL,
            'httpProxy' : self.port_ff_net,
            'ftpProxy'  : self.port_ff_net,
            'sslProxy'  : self.port_ff_net,
            'socksProxy': self.port_ff_net,
            'noProxy'   : ''
        })
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("network.proxy.type" , 1)
        self.profile.set_preference("network.proxy.http" , "localhost")
        self.profile.set_preference("network.proxy.http_port" , self.browser_port) 
        self.profile.set_proxy(self.proxy_my_ff)



    def start_firefox_url(self,site_url): #site_url адрес нужного сайта
        """метод вызова браузера с заданными  настройками прокси в
        методе  __init__ и переход на заданный адрес сайта"""
        try:
            self.url = 'http://www.' +  site_url
            self.driver = webdriver.Firefox(self.profile)
            self.resp= requests.put('http://localhost:8082/proxy/' + str(self.browser_port) + '/har', {"initialPageRef": ""})# начинаю сессию мониторинга
            self.driver.get(self.url)
            self.resp = requests.get('http://localhost:8082/proxy/' + str(self.browser_port) + '/har') #read data in har
            sys.stdout.write('порт прокси браузера = ' + str(self.browser_port) + '\n' + 'порт для har = ' + str(self.browser_port) + '\n' )

        except WebDriverException as err:
            print('отработало исключение в методе start_firefox_url')
            self.bmp_stop()
            print('объект уничтожен')

    def start_data_proxy(self):
        """метод выводит какие данные прошли через прокси bmpproxy"""
        self.resp_har = requests.put('http://localhost:8082/proxy/' + str(self.bmp_port.port) + '/har', {"initialPageRef": ""})# начинаю сессию мониторинга
    def read_data_proxy(self):
        self.resp = requests.get('http://localhost:8082/proxy/' + str(self.bmp_port.port) + '/har')
        self.resp.content
        self.resp.json()
        
    def bmp_stop(self):
        """метод отстановки browsermobproxy но порты почему то заняты остаются ((("""
        self.bmpproxy.stop()
        sys.stdout.write('brouwsermobproxy остановлен, объект уничтожен' + '\n')
#======================================================================================
class BMP_FF_getRequests(BMP_FF):
    """
    данный  класс будет уметь обрабатывать Get request
    """
    pass
    




#=====================================================================================
class Working_coockies(Config_firefox_start):
    """
    Этот класс является потомком класса Config_firefox_start()
    класс работает с куками, но проблема в перехвате GET запросов
    для перехвата страницы, которая нужна для парсинга ссылки на 
    страницу авторизации. Для перехвата GET запросов нужно попробовать 
    использовать библиотеку BrowserMob Proxy и тогда схема коннекта 
    скрипта ffstart.py будет выглядеть следующим образом - класс Config_firefox_start()
    будет конектится к прокси BrowserMob Proxy а BrowserMob Prox к Burpsuite для визуального
    отображения процесса. При установке Browsermobproxy импортировать сертификаты ssl в браузер который будет использоваться классом Working_coockies()
    """
    def site_cookie(self):
        try:
            self.cookie = {"name": "key","value":"value" , "path" : "/"}
            self.driver.add_cookie(self.cookie)
            self.all_cookies = self.driver.get_cookies()
            print(self.all_cookies)
        except:
            print('что пошло не так в классе Working_cookies')


#===================================================================================


class BMP_FF_Working_coockies(BMP_FF):
    """
    Этот класс является потомком класса BMP_FF()
    класс работает с куками, но проблема в перехвате GET запросов
    для перехвата страницы, которая нужна для парсинга ссылки на 
    страницу авторизации. Для перехвата GET запросов нужно попробовать 
    использовать библиотеку BrowserMob Proxy и тогда схема коннекта 
    скрипта ffstart.py будет выглядеть следующим образом - класс Config_firefox_start()
    будет конектится к прокси BrowserMob Proxy а BrowserMob Prox к Burpsuite для визуального
    отображения процесса. При установке Browsermobproxy импортировать сертификаты ssl в браузер который будет использоваться классом Working_coockies()
    """
    def site_cookie(self):
        try:
            self.cookie = {"name": "key","value":"value" , "path" : "/"}
            self.driver.add_cookie(self.cookie)
            self.all_cookies = self.driver.get_cookies()
            print(self.all_cookies)
        except:
            print('что пошло не так в классе BMP_FF_Working_cookies')

#==================================================================================

if __name__ == '__main__':
    A = BMP_FF()
    A.start_firefox_url('google.ru')
    A.bmp_stop()

    B = BMP_FF()
    B.start_firefox_url('vk.com')
    B.bmp_stop()
#    pdb.set_trace()
#    A =  Working_coockies('http://www.sdo.rzd.ru/lms')
#    A.site_cookie()

#=================================================================================

    """
    План:
    
    1) настроить схему выхода в сеть : firefox ->(port) -> browsermob-proxy -> (port) -> Burpsuite -> net

    """    
"""    
    proxy.new_har("google")
    print(proxy.har)
#    print(resp.content) # информация о приложении слушающее порт 
#    client = Client(r'//home//sirius//project//python_sir//SBBs_sdo//lib//python3.5//site-packages//browsermob-proxy//bin//browsermob-proxy',{'port':8082})
#    client.Har()
#    client.port
#    client.new_har('google')
#    client.har

"""

#!/usr/bin/env python3
import sys
import requests
from selenium.webdriver.common.proxy import * # эта бибилиотека нужна ждя пуска мозилы через порт 8080
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from browsermobproxy  import Server # реализована схема скрипт firefox->browsermobproxy
#=====================================================================================

class BMP_FF():
    """
    Класс для работы браузера Firefox через прокси browsermobproxy
    для перехвата и анализа Get запросов.
    """
    def __init__(self,firefox_port = 8080):
        """По умолчанию класс работает с localhost на 8080-ом порту, но если этот порт занят или нужен под что то можно задать другой порт при создании экземпляра класса """
        """инициализация настроек браузера Firefox для работы через прокси"""
        self.port_firefox = firefox_port # 
        #путь прописывать полностью от home до бинарника который скачивается отдельно не через pip install
        self.bmpproxy = Server(r'//home//sirius//project//python_sir//SBBs_sdo//lib//python3.5//site-packages//browsermob-proxy//bin//browsermob-proxy',{'port':firefox_port}) # указываю  путь к  бинарнику и на каком порту слушать трафик
        self.bmpproxy.start() # start browsermobproxy
        self.bmp_port = self.bmpproxy.create_proxy() # назначение порта неизвестно
        self.resp = requests.post('http://localhost:%s/proxy' % (firefox_port),{}) # отправляю запрос для получения №порта на котором поднялся проксик browsermobproxy
        self.browser_port = self.resp.json()['port'] # через этот порт работает браузер
        self.port_ff_net = 'localhost:%s' % (self.browser_port) # получаю строку типа "localhost : 8082"

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
        методе  __init__ и переход на заданный адрес сайта в переменной site_url"""
        try:
            self.url = 'http://www.%s' % (site_url)
            self.driver = webdriver.Firefox(self.profile)
            self.driver.get(self.url)
            sys.stdout.write("порт прокси браузера = %s \nпорт для har = %s \n" % (self.browser_port,self.browser_port))

        except WebDriverException as err:
            print('отработало исключение в методе start_firefox_url')
            self.bmp_stop()
            print('объект уничтожен')

    def start_data_proxy(self):
        """метод выводит какие данные прошли через прокси bmpproxy"""
        """Если нужно получить данные то сначала вызывать этот  метод а потом уже start_firefox_url(site_url) """
        self.resp= requests.put('http://localhost:%s/proxy/%s/har' % (self.port_firefox,self.browser_port), {"initialPageRef": ""})# начинаю сессию мониторингаy
        sys.stdout.write(self.resp.url)# Выводит строку, которую нужно ввести в запущеном браузере (экземпляре object(BMP_FF()).driver) для просмотра har

    def read_data_proxy(self):
        """сохраняю запросы/ответы в object.rest.content"""
        self.resp = requests.get('http://localhost:%s/proxy/%s/har' % (self.port_firefox,self.browser_port)) #read data in har
        self.resp.content
        self.resp.json()
        
    def bmp_stop(self):
        """метод отстановки browsermobproxy и закрывает браузер firefox """
        self.driver.close() #закрываю браузер firefox
        self.bmpproxy.stop()
        sys.stdout.write('brouwsermobproxy остановлен, объект уничтожен' + '\n')
#======================================================================================

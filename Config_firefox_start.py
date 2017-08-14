#!/usr/bin/env python3

from selenium.webdriver.common.proxy import * # эта бибилиотека нужна для пуска Firefox через "определенный"/"нужный"  порт
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException


#====================================================================================
class Config_firefox_start():# параметр в __init__ передавать в виде 'google.ru' без 'http://www.'
    """
    Настройка параметров запускаемого  экземпляра Firefox
    """
    
    def __init__(self,link_url): # link_url при создании обЪекта передаю нужный адрес сайта
        self.url      = 'http://%s' % (link_url) # link_url хранит адрес сайта который нужен для перехода

        """ настройка вкладки "Сеть" запускаемого браузера"""
        self.myProxy  = "localhost:8081" # Экземпляр объекта Config_firefox_start() запустится на указанном прокси , в данном случае на 8081-м порту 
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
        self.profile.set_preference("network.proxy.http_port", 8081) # Firefox пойдет в сеть через 8081-й порт 
        self.profile.set_proxy(self.proxy_my)

        """Запуск браузера с настроенными настройками(prifile)и переход на сайт"""
        self.driver = webdriver.Firefox(self.profile)
        self.driver.get(self.url)

#==================================================================================

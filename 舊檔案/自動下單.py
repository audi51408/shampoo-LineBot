from selenium import webdriver
import pyautogui
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import requests
import re
import warnings
import random
import string
timer = 1

while True:
    driver = webdriver.Chrome(r'webcrawling/chromedriver.exe')
    driver.get('https://ctpsxifajing.webnode.tw/p/%E6%9C%A8%E8%B3%AA%E8%A4%90-%E5%BC%B1%E9%B9%BC%E6%80%A7%E6%9F%93%E8%86%8F-low-lift/')
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/main/div/div/section[2]/div/div/div[2]/div[1]/form/div[4]/div[2]/div/div/div/select')
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/main/div/div/section[2]/div/div/div[2]/div[1]/form/div[4]/div[2]/div/div/div/select/option[2]').click()  
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/main/div/div/section[2]/div/div/div[2]/div[1]/form/div[4]/div[4]/div/button').click()    
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/header/div/div/section/div/div/div[2]/div/div/div[2]/div[1]/div/a/div').click()    
    time.sleep(timer) 
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/main/div/div/section[2]/div/div/div[2]/div/div/div[2]/div/div[5]/a').click()
    time.sleep(timer) 
    random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[1]/div[1]/input').send_keys('莊詠鈞')
    time.sleep(timer) 
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[2]/div[1]/input').send_keys(random_str)    
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[3]/div[1]/input').send_keys(random_str)    
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[4]/div[1]/input').send_keys(random_str)    
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[5]/div[1]/select')
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[5]/div[1]/select/option[32]').click()
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[8]/div[1]/input').clear()
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[8]/div[1]/input').send_keys('audi51408@gmail.com')
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[9]/div[1]/input').clear()
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[1]/fieldset/div/div[9]/div[1]/input').send_keys('+8860966791066') 
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[1]/form/div[2]/button').click()    
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[2]/form/div[2]/button').click()
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[3]/form/div[2]/button').click()
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[4]/form/div[1]/div/div[6]/div[2]/input').click()
    time.sleep(timer)
    driver.find_element_by_xpath('/html/body/div/div[2]/main/section/div/div[4]/form/div[2]/button').click()
    time.sleep(5)
    driver.close()
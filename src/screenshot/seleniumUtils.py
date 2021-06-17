
import pprint
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv(dotenv_path='properties.env')
import os
import traceback

TIME_OUT = 30
chrome_path = './libs/chromedriver'
driver = None
wait = None
actions = None

def withChrome(headless):
    global driver
    global wait
    global actions
    chrome_options = Options()  
    if(headless):
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--proxy-server='direct://'")
        chrome_options.add_argument("--proxy-bypass-list=*")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--headless")
    else:
        chrome_options.add_argument("--start-maximized")
    
    chrome_path = './libs/chromedriver'

    driver = webdriver.Chrome(executable_path=chrome_path,   chrome_options=chrome_options)
    wait = WebDriverWait(driver,TIME_OUT)
    actions = ActionChains(driver)
	
def gotoURL(url, cookies = None):
    global driver
    driver.get(url)
    if cookies:
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get(url)
    
    
def myGetAttrFromXPath(xPath, attributeName):
    value = waitVisible(xPath).get_attribute(attributeName)
    if(value == ""):
        value = waitForClick(xPath).get_attribute(attributeName)
    return value

def myGetAttrFromElement(element, attributeName):
    return element.get_attribute(attributeName)
	
def myGetText(xPath):
    value = waitVisible(xPath).text
    if(value):
        return value.strip()
    else:
        return ""

def waitVisible(xPath):
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, xPath)))
    except:
        print("")
        # print("xPath", xPath)
        # traceback.print_exc()

def waitForClick(xPath):
    try:
        return wait.until(EC.element_to_be_clickable((By.XPATH, xPath)))
    except:
        print("")
        # print("xPath", xPath)
        # traceback.print_exc()

def mySendKey(xPath, keys):
    element=waitVisible(xPath)
    element.send_keys(Keys.COMMAND + "a")
    element.send_keys(keys)

def press(key, time=1):
    if(time <= 0):
        return
    ActionChains(driver).send_keys(key).perform()
    time-=1
    press(key,time)

def myClick(xPath):
    try:
        waitForClick(xPath).click()
    except:
        try:
            waitVisible(xPath).click()
        except:
            print("[ERROR] Cannot click to xPath", xPath)
            traceback.print_exc()
    finally:
        return

def myClick(xPath, times=1):
    if(times <= 0):
        return
    try:
        waitForClick(xPath).click()
        times+=-1
    except:
        try:
            waitVisible(xPath).click()
            times+=-1
        except:
            print("[ERROR] Cannot click to xPath", xPath)
            traceback.print_exc()
            return
    return myClick(xPath, times)

def myScrollToElement(xPath):
    driver.execute_script("arguments[0].scrollIntoView();", waitVisible(xPath))

def pause(seconds):
    time.sleep(seconds)


def switchToIframe(xPath):
    driver.switch_to.frame(waitVisible(xPath))

def mySlider(xPathSliderBar, xPathSlider, percent):
    global actions
    slidebar = waitVisible(xPathSliderBar)
    height = 38
    width = 298
    slider = waitVisible(xPathSlider)
    if width > height:
        #highly likely a horizontal slider
        actions.click_and_hold(slider).move_by_offset(percent * width / 100, 0).release().perform()
    else:
        #highly likely a vertical slider
       actions.click_and_hold(slider).move_by_offset(percent * height / 100, 0).release().perform()

def isExist(xPath):
    try:
        driver.find_element_by_xpath(xPath)
    except NoSuchElementException:
        return False
    return True

def getElements(xPath):
    try:
        datas = driver.find_elements_by_xpath(xPath)
    except NoSuchElementException:
        print("[ERROR]: not found elements with xPath: " + xPath)
        return []
    return datas

def screenShot(outputPath):
    driver.save_screenshot(outputPath)

def waitUntilExist(xPath):
    exist = isExist(xPath)
    if not exist:
        return waitUntilExist(xPath)
    
    return

def myHoverAndClick(xPath):
    element = waitVisible(xPath)
    hov = ActionChains(driver).move_to_element(element)
    hov.click().perform()

def quit():
    if (driver != None):
        driver.quit()

def changeStyle(xPath, styleName, newValue):
    item = waitVisible(xPath)
    item.click()
    driver.execute_script("arguments[0].style." + str(styleName) + " = '" + str(newValue) +"%'", item)
    item.click()

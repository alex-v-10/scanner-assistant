from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import pickle
    
chrome_profile_dir = os.path.abspath('browser/chrome_profile')

if not os.path.exists(chrome_profile_dir):
    os.makedirs(chrome_profile_dir)

def save_cookies(driver, filepath):
    with open(filepath, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, filepath):
    with open(filepath, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def manual_login_and_save_cookies():
    options = Options()
    options.add_argument(f"user-data-dir={chrome_profile_dir}")
    driver = webdriver.Chrome(options=options)
    driver.get('https://groq.com')
    print("Please log in manually and then press Enter here...")
    input()
    save_cookies(driver, 'browser/cookies.pkl')
    driver.quit()

def automated_interaction():
    options = Options()
    options.add_argument(f"user-data-dir={chrome_profile_dir}")
    driver = webdriver.Chrome(options=options)
    driver.get('https://groq.com')
    try:
        load_cookies(driver, 'browser/cookies.pkl')
        driver.refresh()
    except FileNotFoundError:
        print("No cookies found, please run manual_login_and_save_cookies() first.")
        driver.quit()
        return
    time.sleep(5)
    driver.quit()

def browse():
    manual_login_and_save_cookies()
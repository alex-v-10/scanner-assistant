from selenium import webdriver
import time


def browse():
    try:
        driver = webdriver.Chrome()
        driver.get('https://www.google.com')
        time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")    
    finally:
        driver.quit()
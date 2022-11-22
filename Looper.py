from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service
from selenium.webdriver.safari.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from signal import signal, alarm, SIGALRM
from time import sleep
import os
import pwd
import subprocess
import linecache
import re

s = Service('/usr/bin/safaridriver')
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--profile')
options.add_argument(os.path.join(os.environ['PWD'], 'profile'))
options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15')
driver = webdriver.Safari(service=s, options=options)
wait = WebDriverWait(driver, 30)
clickable = ec.element_to_be_clickable
Login_URL = 'https://gsx2.apple.com'


def login():  # Logs into GSX automatically.
    print("Attempting to login to GSX")
    driver.get(Login_URL)
    username = linecache.getline('/Users/'+pwd.getpwuid(os.getuid())[0]+'/Desktop/Login-Info.txt', 1)  # Gets AppleID and Password from a separate local file
    password = linecache.getline('/Users/'+pwd.getpwuid(os.getuid())[0]+'/Desktop/Login-Info.txt', 2)
    sleep(2)
    wait.until(
        ec.frame_to_be_available_and_switch_to_it((By.ID, "aid-auth-widget-iFrame")))  # wait for animations in iframe
    sleep(1)
    wait.until(clickable((By.ID, "account_name_text_field"))).send_keys(username, Keys.RETURN)
    sleep(1)
    wait.until(clickable((By.ID, "password_text_field"))).send_keys(password, Keys.RETURN)
    sleep(2)
    two_factor_auto()


def two_factor_auto():  # 2FA defeating method for Trusted Device
    if len(driver.find_elements(By.ID, 'char0')) > 0:
        print("Found Trusted Device Code input box! Automated 2FA process started!")
        as_script = '''tell application "System Events" to tell the process "FollowUpUI"
                                     click button "Allow" of window 1
                                     delay 1
                                     set Code to (get value of static text 1 of group 1 of window 1)
                                     delay 1
                                     click button "Done" of window 1
                                     Code
                                 end tell'''
        try:
            twofa = subprocess.check_output(['osascript', '-e', as_script]).decode("utf-8").replace(" ", "").replace(
                "\n", "")
            #
            sleep(1)
            try:
                for index, number in enumerate(twofa):
                    driver.find_element(By.CSS_SELECTOR, "input[data-index='{}']".format(index)).send_keys(number)
                    alarm(0)
            except:
                pass
        except subprocess.CalledProcessError:
            two_factor_manual()
        except AttributeError:
            two_factor_manual()
        sleep(2)
        if len(driver.find_elements(By.XPATH, '//*[starts-with(@id, "trust-browser-")]')) > 0:
            driver.find_element(By.XPATH, '//*[starts-with(@id, "trust-browser-")]').send_keys(Keys.SPACE)
    else:
        print("Skipping 2FA, not needed this time")


def two_factor_manual():  # 2FA Defeating for when Auto method fails for some reason
    signal(SIGALRM, lambda a, b: 1 / 0)
    try:
        alarm(300)
        print("Automated Trusted Device Code failed. Sending SMS instead. 5 minute timer started!")
        wait.until(clickable((By.ID, 'no-trstd-device-pop'))).send_keys(Keys.RETURN)
        sleep(1)
        wait.until(clickable((By.ID, 'use-phone-link'))).send_keys(Keys.RETURN)
        twofa = two_factor_input()
        for index, number in enumerate(twofa):
            driver.find_element(By.CSS_SELECTOR, "input[data-index='{}']".format(index)).send_keys(number)
        alarm(0)
    except ZeroDivisionError:
        print(" 5min timer for SMS 2FA expired. Exiting application")
        exit()


def two_factor_input():
    good2_fa = 0
    while good2_fa != 1:
        twofa = input('::::::: SMS 6-Digit Code ---> ')
        if len(twofa) <= 5 or len(twofa) >= 7:
            print("Check your 2FA Code! Either too long or too short")
        else:
            try:
                int(twofa)
                good2_fa = 1
            except ValueError:
                print("Not a number entered! Try again")
    return twofa


def remember_me():
    checked = driver.find_element(By.XPATH, '//*[@id="remember-me"]').get_property("checked")
    if checked != 'True':
        wait.until(ec.element_to_be_clickable((By.ID, "remember-me"))).send_keys(Keys.SPACE)
        sleep(1)



if __name__ == '__main__':
    login()
    sleep(2)
    driver.get("https://diagnostics.apple.com")
    keepalive = False
    driver.implicitly_wait(30)
    wait.until(ec.visibility_of_all_elements_located((By.XPATH, '//*[@id="sidebar]')))
    sessions = len(driver.find_elements(By.XPATH, '//*[ends-with(@id, "card")]'))
    # print(sessions)
    # while keepalive:
    # for x in sessions:
    # pass
    sleep(50)
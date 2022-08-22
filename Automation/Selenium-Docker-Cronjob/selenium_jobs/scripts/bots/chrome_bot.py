import logging
import time
import random
from os.path import expanduser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger()
fileHandler = logging.FileHandler('../selenium_automation.log')
formatter = logging.Formatter("%(asctime)s :%(levelname)s :%(name)s :%(message)s")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
# logger.setLevel(logging.DEBUG)

log_path = expanduser("~") + '/Selenium_Logs/'


class BotListener(AbstractEventListener):
    def before_find(self, by, value, driver):
        # TODO: add logging
        # self.do_random_sleep()
        # self.check_for_recaptcha(by, value, driver)
        pass

    def do_random_sleep(self):
        print("Sleeping to avoid bot detection...")
        # time.sleep(random.uniform(1.0, 2.0))
        time.sleep(random.randint(1, 3))

    def check_for_recaptcha(self, by, value, driver):
        recaptcha_sleep = 10
        find_tries = 10
        for find_try in range(find_tries):
            try:
                driver.find_element(by, value)
                break
            except:
                print("Couldn't find element, checking for recaptcha")
                while True:
                    try:
                        # recaptcha element
                        driver.find_element_by_xpath(
                            "//*[contains(@class, 're-captcha')]")
                        # Wait 10 seconds for user to process captcha
                        print("Recaptcha found!")
                        print("Waiting for human intervention!")
                        time.sleep(recaptcha_sleep)
                    except:
                        print("No recaptcha found!")
                        # break from attempt loop
                        break

    def on_exception(self, exception, driver):
        pass
        # For now, exception screenshots are commented out, because it would take up too much space.
        # I need to figure out how to filter screenshots for trivial exceptions.
        """
        screenshot_name = "%s-exception.png" % datetime.datetime.now()
        driver.get_screenshot_as_file(log_path + screenshot_name)
        print("Screenshot of exception captured: %s" % screenshot_name)
        """


class ChromeBot():
    def __init__(self, incognito=True):
        chrome_options = Options()
        # Get the latest chromium build for Linux here:
        # https://chromium.woolyss.com/#linux
        chrome_options.binary_location = "/usr/bin/chromium"
        # TODO: uncomment before deploying to cron server.
        #chrome_options.add_argument("headless")
        """
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        #chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--proxy-auto-detect")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-data-dir=/tmp/user-data")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=99")
        #chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--data-path=/tmp/data-path")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--homedir=/tmp")
        chrome_options.add_argument("--disk-cache-dir=/tmp/cache-dir")
        """
        chrome_options.add_argument("user-agent=Mozilla/5.0 "
                                    "(X11; Linux x86_64) "
                                    "AppleWebKit/537.36 "
                                    "(KHTML, like Gecko) "
                                    "Chrome/61.0.3163.100 "
                                    "Safari/537.36")
        if incognito:
            chrome_options.add_argument("--incognito")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver = EventFiringWebDriver(driver, BotListener())
        self.driver.implicitly_wait(5)

    def __goto_page(self, url):
        try:
            self.driver.get(url)
            print("URL successfully opened.")
        except Exception as exception_message:
            print("URL could not be opened. Exception: %s" % exception_message)

    def setup(self, url):
        print("Opening URL")
        self.__goto_page(url)

    def check_element(self, by: By, value: str):
        try:
            if self.driver.find_element(by, value):
                logger.info("Element found: {}, {}".format(str(by), value))
                return True
        except:
            pass
        logger.info("Element NOT found: {}, {}".format(str(by), value))
        return False

    def wait_for_element(self, by: By, element_value: str, timeout=20):
        try:
            second_count = 0
            while not self.driver.find_element(by, element_value):
                time.sleep(1)
                second_count += 1
                if second_count == timeout:
                    break
        except:
            pass

    def wait_for_not_element(self, by: By, element_value: str, timeout=20):
        try:
            second_count = 0
            while self.driver.find_element(by, element_value):
                time.sleep(1)
                second_count += 1
                if second_count == timeout:
                    break
        except:
            pass

    def wait_for_clickable(self, by: By, element_value: str, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, element_value))).click()
        except:
            pass

    def wait_for_visible(self, by: By, element_value: str, timeout=20):
        """
        Waits for an element to be visible. Does not click it.
        :param by:
        :param element_value:
        :param timeout:
        :return:
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, element_value)))
        except:
            pass

#!/usr/bin/python3
import time
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium_jobs.scripts.bots.chrome_bot import ChromeBot

logger = logging.getLogger()


class ForemanBot(ChromeBot):
    def __init__(self):
        super().__init__()
        self.setup('https://dashboard.foreman.mn/dashboard/')

    def is_logged_in(self):
        """
        Checks to see if logged into Foreman, returns true if so.
        :return:
        """
        time.sleep(2)
        if self.check_element(By.XPATH, "//span[contains(.,'Dashboard')]"):
            return True
        return False

    # Login to Foreman
    def login(self, email, password):
        """
        Log into Foreman -- don't forget to wait for the dashboard to load after running this.
        :str email: login email
        :str password: login password
        :return:
        """
        if self.is_logged_in():
            logger.info("Already logged in.")
            pass
        else:
            logger.info("Logging in.")
            self.driver.find_element(By.NAME, "username").click()
            self.driver.find_element(By.NAME, "username").clear()
            self.driver.find_element(By.NAME, "username").send_keys(email)
            self.driver.find_element(By.NAME, "password").click()
            self.driver.find_element(By.NAME, "password").clear()
            self.driver.find_element(By.NAME, "password").send_keys(password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

    def open_sidebar_page(self, page: str):
        self.wait_for_clickable(By.XPATH, "//a[contains(., '{}')]".format(page))

    def view_issues(self, issue_type: str):
        """
        Click 'Show Miners' for category in issues page.
        """
        self.driver.find_element(By.XPATH, "//tr[contains(., '{}')]/td/button".format(issue_type)).click()

    def clear_any_filters(self, timeout=8):
        """
        Clears filters in Foreman.
        :param timeout:
        :return:
        """
        logger.info("Clearing filters.")
        tries = 0
        while tries < timeout:
            try:
                tries += 1
                self.driver.find_element(By.XPATH, "//a[@onclick='clearFilters();']").click()
                time.sleep(2)
                break
            except:
                time.sleep(1)

    def bulk_edit_button_click(self):
        """
        Click the bulk edit button on the miner's page. Use before selecting miners to bulk edit.
        :return:
        """
        self.wait_for_clickable(By.XPATH, "//button[contains(., 'Bulk Edit Miners')]")

    def bulk_edit_action(self, action: str):
        """
        For interacting with the bulk edit popup.
        :str action: A string containing the full or partial text of the bulk edit action to apply.
        :return:
        """
        action_field = self.driver.find_element(
            By.XPATH, "//input[@placeholder='Choose items to edit for selected miners']")
        action_field.click()
        action_field.send_keys(action)
        action_field.send_keys(Keys.ENTER)
        self.driver.find_element(By.XPATH, "//button[contains(., 'Apply')]").click()

    def bulk_edit_select_all(self, timeout=20):
        """
        Selects all miners shown on the miners page, for doing bulk edits.
        :param timeout:
        :return:
        """
        logger.info("Clicking select all button on miners page.")
        self.wait_for_visible(
            By.CLASS_NAME, "bulk-edit-table-select", timeout)
        self.wait_for_clickable(
            By.CSS_SELECTOR, ".sorting_disabled > #bulk-edit-table-select-all > .fa-square-o", timeout)

    def bulk_edit_edit_button_click(self):
        """
        For the second click of the bulk edit button. Use after selecting miners to bulk edit.
        :return:
        """
        self.wait_for_clickable(By.XPATH, "//button[@onclick='openBulkEditPopup();']")

    def bulk_edit(self, action):
        """
        Easy function for performing the entire bulk edit process.
        :param action:
        :return:
        """
        logger.info("Clicking bulk edit button.")
        self.bulk_edit_button_click()
        logger.info("Selecting all miners.")
        self.bulk_edit_select_all()
        logger.info("Clicking bulk edit for selected miners.")
        self.bulk_edit_edit_button_click()
        logger.info("Waiting for bulk edit popup to show.")
        self.wait_for_bulk_action_popup()
        logger.info("Applying bulk edit action.")
        self.bulk_edit_action(action)
        logger.info("Waiting for the remote commands popoup to be visible. "
                    "This indicates that the bulk edit completed.")
        self.wait_for_visible(
            By.XPATH, "//span[contains(., 'Clear Completed')]", 5)
        # time.sleep(2)
        logger.info("Close remote commands popup.")
        self.close_remote_commands_popup()

    def wait_for_miners_page_load(self, timeout=20):
        """
        Wait for the 'Miners' page to fully load. Do this before running bulk edits.
        :param timeout:
        :return:
        """
        self.wait_for_element(By.CLASS_NAME, "sorting_1", timeout)

    def wait_for_dashboard_load(self, timeout=20):
        """
        Use this to wait for the Foreman dashboard to fully load.
        Scripts often crash if the Dashboard has not loaded fully.
        :int timeout: How long in seconds to wait for the dashboard to load
        :return:
        """
        # Look for the gear spinning element
        self.wait_for_not_element(By.CSS_SELECTOR, "fa fa-cog fa-spin", timeout)

    def wait_for_bulk_action_popup(self, timeout=20):
        """
        Wait for the bulk edit popup to show.
        :param timeout:
        :return:
        """
        self.wait_for_visible(
            By.XPATH, "//*[contains(., 'Please choose items from above to edit.')]", timeout)

    def close_remote_commands_popup(self):
        self.remote_commands_click()

    def remote_commands_click(self):
        """
        Click the remote commands button, shows the popup/dropdown.
        :return:
        """
        self.wait_for_clickable(By.XPATH, "//a[@title='Remote Commands']")

    def select_client(self, client):
        """
        Interacts with the client/site selection in Foreman's topbar.
        :param client:
        :return:
        """
        self.driver.find_element(By.ID, "dd-available-clients").find_element(By.CLASS_NAME, "client-label").click()
        self.wait_for_visible(By.CLASS_NAME, "select2-search__field")
        self.driver.find_element(By.CLASS_NAME, "select2-search__field").send_keys(client)
        self.driver.find_element(By.CLASS_NAME, "select2-search__field").send_keys(Keys.RETURN)
        self.wait_for_dashboard_load()

    def get_alert_trigger_checkboxes(self):
        """
        Returns array with all checkbox/toggle WebElements from the Alerts & Triggers page.
        :return:
        """
        return self.driver.find_elements(By.XPATH, "//div[@class='triggering-condition-toggle']/fieldset/div/div/label")

    def alerts_and_triggers_save(self):
        """
        Click the save button on the Alerts & Triggers page.
        :return:
        """
        self.driver.find_element(By.XPATH, "//button[contains(.,'Save')]").click()

import unittest
from selenium import webdriver
import settings


class SearchText(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        #navigate to application home page
        self.driver.get("https://my.wealthsimple.com/app/login?locale=en-ca")

    def get_login_credentials(self):
        # TODO: To check if .env information is filled out?
        # Get the Email Textbox
        self.email_textbox = self.driver.find_element_by_id(
            'input--b3695a77-df8b-4e64-b32e-d4bc8756bed1')
        # Input information
        self.email_textbox.send_keys(settings.WS_USERNAME)
        # Get the password Textbox
        self.password_textbox = self.driver.find_element_by_xpath(
            'input--244423b7-be19-4fc6-8ca4-1256f097365a')
        self.password_textbox.send_keys(settings.WS_PASSWORD)
        # Get the login button
        self.login_button = self.driver.find_element_by_xpath(
            '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/div/div/div/div[5]/button'
        )
        # Click the login button
        self.login_button.click()

        self.driver.implicitly_wait(10)

        # Two-step verification page. Stop here?
        self.TFA_code_textbox = self.driver.find_element_by_id(
            'input--84218225-36ab-40a5-8215-0c7ef2208962')
        self.assertNotEqual(0, self.TFA_code_textbox.size)

    def get_login_credentials_fail(self):
        # Just click the login button
        self.login_button = self.driver.find_element_by_xpath(
            '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/div/div/div/div[5]/button'
        )
        self.login_button.click()

        self.driver.implicitly_wait(10)

        # Check if login failed
        self.driver.fail_text = self.driver.find_element_by_xpath(
            '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/div/div/div/div[2]/div/p'
        )
        self.assertEqual('The login credentials you entered are invalid',
                         self.driver.fail_text.text)

    def tearDown(self):
        # Close the browser window
        self.driver.quit()


test = SearchText()
test.setUp()
test.get_login_credentials_fail()
test.tearDown()
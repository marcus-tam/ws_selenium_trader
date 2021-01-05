# Written By Marcus Tam
"""
    Basic selenium application to trade stocks on WealthSimple. 

    This is meant to be a personal application, but feel free to use and modify. If you notice any glaring errors, please write an issue
    and I'll be sure to get to it soon. 

    This application is for education purposes. I (Marcus Tam) do not take responsibility of you gain or lose money if you choose to use 
    this application. 
"""

import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
import settings
import ws_bot_discord as dns  #discord notification system

# TODO: Implement a headless version to run in background.
# test.py
# in tfa() -> tick 30 days (or maybe have that as option)
# in trading_tab() -> consider the URL switching as opposed to
# Instead of sleeps, use implicit waits
# Figure out way to get stock_high and stock_low to match self.buy_price and self.sell_price (use yahoo_fin?)
# Could be issue with 15 minute delay on WealthSimple?
# settings.py -> secrets.py? Seems excessive with .env but more secure???
# Controllable with discord bot? STRETCH GOAL
# Find way to grab URL of STOCK_TICKER without hard coding it.
# Multithreading tab to dns to see if stock dips below comfortable amount.


class ws_bot():
    def __init__(self, override=False):
        """
            Initialize the chromedriver. Uncomment chrome_options if you want to run in background.
        """
        CHROMEDRIVER_PATH = settings.CHROMEDRIVER_PATH
        # chrome_options = Options()
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--headless")
        # Okay maybe headless doesn't work. Could be issue with Chrome Browser not taking in xpath arguments.

        self.holdings = False
        self.current_shares = 0

        self.buy_price = 0
        self.sell_price = 0
        self.quantity = 0

        # If set to True, discord webhook will trigger on events
        self.discord = False

        # If on, manually edit buy and sell price during execution.
        self.override = override

        # Used to set the URL of the STOCK_TICKER, initially it is empty, but will be temporarily populated when the application is run.
        self.stock_ticker_url = ""

        # Option to enable chrome_options to be implemented?
        # selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 85
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH)

        print("Driver initialized!")
        if self.discord == True:
            dns.discord_message("Spinning up driver...")

        if self.override == True:
            print("Override activated")
            if self.discord == True:
                dns.discord_message(
                    "Bot override. Human Intervention Required... ")
            high = input("Input Lowest Buy Price: ")
            low = input("Input Highest Sell Price: ")
            quantity = input("Input quantity to Buy AND Sell")
            self.buy_price = high
            self.sell_price = low
            self.quantity = quantity

    def login(self):
        """
            Login into wealthsimple. 
            Get your information from settings.py 
            Using selenium, input obtained values to login, most likely you will have to enter a 2FA code.
            Please read two_factor_auth to deal with that.
            Otherwise, you will login into WealthSimple. 
        """
        print("Attempting to login...")

        # WealthSimple Login Page
        self.driver.get("https://my.wealthsimple.com/app/login?locale=en-ca")
        username = settings.WS_USERNAME
        password = settings.WS_PASSWORD
        sleep(8)

        # Email
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/div/div/div/div[2]/div/input"
        ).send_keys(username)
        print("Entered email")

        # Password
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/div/div/div/div[3]/div/input"
        ).send_keys(password)
        print("Entered password")

        # Submit Form
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/div/div/div/div[5]/button"
        ).click()
        print("Submit form...")
        sleep(8)

        try:
            ws_bot.two_factor_auth(self)
        except:
            print("TFA bypassed...")
        # Test if login is successful?
        finally:
            if self.discord == True:
                dns.discord_message("Logged into WealthSimple!")
            sleep(4)

    def two_factor_auth(self):
        """
            There is a great chance you will have to enter a 2FA code. Please go to your email and enter the code into your terminal.
        """

        print("Requirement: Two Factor Authentication")

        # Two Factor Authentication Input Box
        tfa_box = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/login-two-factor-form/div/div/ws-micro-app-loader/two-factor-auth-details/span/div/div/div/div/div[1]/div/input'
        tfa = input(
            "Go to your email and enter your two factor authentication here: ")
        self.driver.find_element_by_xpath(tfa_box).send_keys(tfa)

        # Submit TFA Form
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/login-two-factor-form/div/div/ws-micro-app-loader/two-factor-auth-details/span/div/div/div/div/div[3]/button[1]'
        ).click()

        #TODO: Tick remember me for 30 days
        sleep(8)
        print("Login Successful!")
        ws_bot.trading_tab(self)

    def trading_tab(self):
        """
            Navigate to the trading page after your login. 
        """
        print("Enter trading webpage...")

        # Click Trading Page
        # TODO: Consider Switching to using a URL instead of clicking on XPATH
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-product-switcher-breather-component/ws-micro-app-loader/product-switcher-breather/span/div/div/div/div/div[3]/button'
        ).click()
        sleep(8)
        print("Entered trading page!")

    def get_stock(self):
        """
            Get specific stock in wealthsimple in the search bar. to be used after you've logged in AND navigated to the trading tab
        """
        #TODO Ensure that we are on the get_stock page. Perhaps match URL? Or try catch
        STOCK_TICKER = settings.STOCK_TICKER
        print(f"Getting Stock: {STOCK_TICKER}")

        #Search bar xpath
        sb_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/header-component/header/ws-micro-app-loader[1]/page-header/span/div/div[2]/div/div[1]/div[2]/input'
        self.driver.find_element_by_xpath(sb_xpath).send_keys(STOCK_TICKER)
        sleep(3)

        # From search, Pick First entry, then enter.
        self.driver.find_element_by_xpath(sb_xpath).send_keys(Keys.DOWN)
        sleep(3)
        self.driver.find_element_by_xpath(sb_xpath).send_keys(Keys.ENTER)
        sleep(3)

        print(f"Directed to {STOCK_TICKER} page")
        # TODO: Please check this once I land
        self.stock_ticker_url = self.driver.current_url

    def get_market_details(self):
        """
            To be executed AFTER get_stock
            This gets all the market information from WealthSimple on a certain stock
        """
        # Xpaths for Open/High/Close
        stock_open_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/p[2]'
        stock_high_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[1]/div[3]/div/div[1]/div[2]/p[2]'
        stock_low_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[1]/div[3]/div/div[1]/div[3]/p[2]'

        stock_open = self.driver.find_element_by_xpath(stock_open_xpath)
        stock_high = self.driver.find_element_by_xpath(stock_high_xpath)
        stock_low = self.driver.find_element_by_xpath(stock_low_xpath)

        # TODO: This is sketchy; high's and lows are calculated during the day. If this runs in the morning, it will have no data. Especially with WS 15 minute delay
        # Perhaps we can use yahoo_fin to extract real time data?
        self.buy_price = stock_low.text[1:]
        self.sell_price = stock_high.text[1:]
        if self.discord == 1:
            dns.discord_message(
                f"Market Details for {settings.STOCK_TICKER} \nOpen : {stock_open.text}\nHigh : {stock_high.text}\nLow : {stock_low.text}"
            )

    def check_holdings(self):
        """
            Checks if user currently has a position in the current stock. Use after get_stock()
        """
        # Check if user
        your_holdings_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[1]/div[2]/h3'
        try:
            your_holdings_text = self.driver.find_element_by_xpath(
                your_holdings_xpath).text
            if your_holdings_text == "Your holdings":
                self.holdings = True
            current_shares = self.driver.find_element_by_xpath(
                '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[1]/div[2]/div/button/div[1]/div[1]/div[1]/div/p'
            ).text.split()  #splits number and word shares
            self.current_shares = current_shares[0]
            total_val = self.driver.find_element_by_xpath(
                '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[1]/div[2]/div/button/div[1]/div[1]/div[2]/p'
            ).text
            if self.discord == True:
                dns.discord_message(
                    f"Current position\n{self.current_shares}\nTotal Value : {total_val} "
                )
            self.holdings = True
        except:
            if self.discord == True:
                dns.discord_message(
                    f"Currently no positions in {settings.STOCK_TICKER}")
            self.holdings = False

    def limit_buy(self):
        """
            Makes a limit buy
            TODO:   Ensure user is on get_stock() -- (Use self.stock_ticker_url attribute)
                    Ensure self.holdings = False
                    Get MAX quantity of shares user will buy
                    Select Limit Buy
                    Enter Highest PPS user is willing to pay
                    Enter in quantity. 
                    Click BUY
                    DNS "Executed Limit Buy Order of {N shares} of {STOCK_TICKER} Estimated Cost (Scrape value of est)
                    CLICK VIEW ORDER STATUS
                    Loop on Pending orders til it doesnt exist.
                    Execute limit BUY 
        """
        if self.holdings == True:
            self.limit_sell
        # if self.override == True:
        #     print("Override activated")
        #     if self.discord == True:
        #         dns.discord_message(
        #             "Bot override. Human Intervention Required... ")
        #     high = input("Input Buy Price: ")
        #     low = input("Input Sell Price: ")
        #     self.buy_price = high
        #     self.sell_price = low

        # ws_bot.get_stock(self)
        # TODO: Temporary -- Adds robustness atm, looking for cleaner execution
        self.driver.get(
            'https://my.wealthsimple.com/app/trade/security/sec-s-a124b41224594fa48f2a8498be43d100'
        )
        sleep(8)

        # BUY / SELL -> BUY
        buy_order_button_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[1]/button[1]'
        self.driver.find_element_by_xpath(buy_order_button_xpath).click()
        sleep(1)

        # TODO: Must find which account to use to buy stocks. Personal or otherwise.
        # In this scenario, we could set an init attibute called account_type
        # To specify which account to use. Will default to TFSA.

        # Order Type ... Limit BUY
        limit_buy_dropdown_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div[2]/select/option[2]'
        self.driver.find_element_by_xpath(limit_buy_dropdown_xpath).click()
        sleep(1)

        # Highest Price Per Share You'd BUY
        highest_pps_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/div[3]/div/div/input'
        self.driver.find_element_by_xpath(highest_pps_xpath).send_keys(
            self.buy_price)
        sleep(1)

        # How many Shares
        shares_quantity_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div[2]/input'
        self.driver.find_element_by_xpath(shares_quantity_xpath).send_keys(
            self.current_shares)
        sleep(4)

        # Scroll to bottom script
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)

        # Sell Stock
        sell_stock_button_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/button'
        self.driver.find_element_by_xpath(sell_stock_button_xpath).click()
        sleep(8)

        place_order_button_xpath = '/html/body/span/div/div/div[2]/div/div[4]/div/button[1]'
        self.driver.find_element_by_xpath(place_order_button_xpath).click()

        sleep(8)
        # view_order_status_xpath = '/html/body/span/div/div/div[2]/div/button[2]'
        # self.driver.find_element_by_xpath(view_order_status_xpath).click()

        estimated_cost = self.driver.find_element_by_xpath(
            '/html/body/span/div/div/div[2]/div/p[2]').text
        if self.discord == True:
            dns.discord_message(
                f"Executed Limit Sell Order of {self.current_shares} of {settings.STOCK_TICKER} stock. {estimated_cost} "
            )
        # Takes you to activity page to check pending orders
        # TODO: (Implement) Use self.stocker_ticker_url
        self.driver.get('https://my.wealthsimple.com/app/trade/activities')
        # Reformat logic for this
        self.holdings = True

    def limit_sell(self):
        """
           Makes a limit sell
            TODO:   Loop on Pending orders til it doesnt exist.
                    Execute limit sell 
        """
        # Exception Handler to check if we have any active holdings.
        if self.holdings == False:
            ws_bot.limit_buy
        if self.override == True:
            print("Override activated")
            if self.discord == True:
                dns.discord_message(
                    "Bot override. Human Intervention Required... ")
            high = input("Input Buy Price: ")
            low = input("Input Sell Price: ")
            self.buy_price = high
            self.sell_price = low

        # ws_bot.get_stock(self)
        # Temporary -- Adds robustness atm, looking for cleaner execution
        self.driver.get(
            'https://my.wealthsimple.com/app/trade/security/sec-s-a124b41224594fa48f2a8498be43d100'
        )
        sleep(8)

        # BUY / SELL -> SELL
        sell_order_button_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[1]/button[2]'
        self.driver.find_element_by_xpath(sell_order_button_xpath).click()
        sleep(1)

        # Order Type ... Limit Sell
        limit_sell_dropdown_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div[2]/select/option[2]'
        self.driver.find_element_by_xpath(limit_sell_dropdown_xpath).click()
        sleep(1)

        # Lowest Price Per Share You'd Sell
        lowest_pps_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/div[3]/div/div/input'
        self.driver.find_element_by_xpath(lowest_pps_xpath).send_keys(
            self.sell_price)
        sleep(1)

        # How many Shares
        shares_quantity_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/div[4]/div/div/div[1]/div[2]/input'
        self.driver.find_element_by_xpath(shares_quantity_xpath).send_keys(
            self.current_shares)
        sleep(4)

        # Scroll to bottom script
        # This needs to execute becuase entire page doesn't load properly, must scroll down to activate some elements of the page.
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)

        # Sell Stock
        sell_stock_button_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/span/div[3]/div/div[2]/div/div/div/div/div[2]/div/button'
        self.driver.find_element_by_xpath(sell_stock_button_xpath).click()
        sleep(8)

        place_order_button_xpath = '/html/body/span/div/div/div[2]/div/div[4]/div/button[1]'
        self.driver.find_element_by_xpath(place_order_button_xpath).click()

        sleep(8)
        # view_order_status_xpath = '/html/body/span/div/div/div[2]/div/button[2]'
        # self.driver.find_element_by_xpath(view_order_status_xpath).click()

        estimated_cost = self.driver.find_element_by_xpath(
            '/html/body/span/div/div/div[2]/div/p[2]').text
        if self.discord == True:
            dns.discord_message(
                f"Executed Limit Sell Order of {self.current_shares} of {settings.STOCK_TICKER} stock. {estimated_cost} "
            )
        # Takes you to activity page to check pending orders
        self.driver.get('https://my.wealthsimple.com/app/trade/activities')

        #WHILE LOOP TO ENSURE ORDER IS PENDING > THEN EXECUTE LIMIT BUY

    def pending(self):
        # Pseudocode:
        # NOTE: This code should ALWAYS execute after limit_buy and limit_sell.
        # Navigate to pending page
        # while
        # Every minute or something check if the first xpath says pending
        # if not pending, exit while loop
        # Go to limit buy or sell depending on if holdings == True or False
        url = 'https://my.wealthsimple.com/app/trade/activities'
        pending_trigger = False
        pending_xpath = '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/ws-micro-app-loader/routes/span/div/div[2]/div/div[2]/div/div[1]/h3'

        # Run this while loop while our order is still pending. Once 'Pending' Turns into past, switch pending_trigger to True to exit.
        while not pending_trigger:
            pending_text = self.driver.find_element_by_xpath(pending_xpath)
            if pending_text != 'Pending':
                pending_trigger = True
            else:
                sleep(60)

    def ws_override(self):
        override_input = input("Enable override? (y/n) ")
        override = False
        if override_input == 'y':
            override = True
            return override
        else:
            return override


bot = ws_bot()
# bot.login()
# sleep(4)
# bot.get_stock()

# # Do specific checks (holdings, current_shares) automate process?

# bot.get_market_details()
# bot.check_holdings()

# NOTE user can have 2 states (active_positions = True or False)
# if positions = False
# get_market_details
# else
# check_holdings (DO SOME CALCULATION)

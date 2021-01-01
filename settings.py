# settings.py
from dotenv import load_dotenv
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # Python 3.6+ only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import os
# REQUIRED
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

WS_USERNAME = os.getenv("WS_USERNAME")
WS_PASSWORD = os.getenv("WS_PASSWORD")

STOCK_TICKER = os.getenv("STOCK_TICKER")

# OPTIONAL
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
DISCORD_AVATAR_URL = os.getenv("DISCORD_AVATAR_URL")
DISCORD_USERNAME = os.getenv("DISCORD_USERNAME")

ALPHA_VANTAGE_API = os.getenv("ALPHA_VANTAGE_API")

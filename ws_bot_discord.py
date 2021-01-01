# importing the requests library
# discord notification service
import requests
import pprint
import settings

DISCORD_WEBHOOK = settings.DISCORD_WEBHOOK
DISCORD_AVATAR_URL = settings.DISCORD_AVATAR_URL
username = settings.DISCORD_USERNAME


def discord_message(message):
    """
        Use this POST method to interact with your discord server through webhooks. 
    """
    data = {
        'username': username,
        'avatar_url': DISCORD_AVATAR_URL,
        'content': message
    }
    requests.post(url=DISCORD_WEBHOOK, data=data)

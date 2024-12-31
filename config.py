import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'headless': True,
    
    'windscribe': {
        'url': 'https://windscribe.com/login',
        'username': os.getenv('WINDSCRIBE_USERNAME'),
        'password': os.getenv('WINDSCRIBE_PASSWORD'),
        '2fa_secret': os.getenv('WINDSCRIBE_2FA_SECRET')
    },
    
    'qbittorrent': {
        'url': 'https://mrcaters.me/qbittorrent/',
        'username': os.getenv('QBITTORRENT_USERNAME'),
        'password': os.getenv('QBITTORRENT_PASSWORD')
    },

    'chrome_binary_path': os.getenv('CHROME_BINARY_PATH')
}
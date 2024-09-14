from datetime import datetime
from bot import bot, config
import time, traceback
from requests.exceptions import ReadTimeout


if __name__ == '__main__':
    try:
        bot.start()

    except ReadTimeout as rt:
        print('err', traceback.format_exc())
        if config.get('send_notify'):
            bot.notify.error(f'{rt} at {datetime.now()}')
    except Exception as e:
        print('err', traceback.format_exc())
        if config.get('send_notify'):
            bot.notify.error(f'{e} at {datetime.now()}')
    finally:
        print('bot was stopped!')
        if config.get('send_notify'):
            bot.notify.error('Bot was stopped!')
        
   
        
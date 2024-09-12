from datetime import datetime
from bot import bot, config
import time, traceback


if __name__ == '__main__':
    try:
        bot.start()
    except Exception as e:
        print('err', traceback.format_exc())
        if config.get('send_notify'):
            bot.notify.error_notify(f'Error ({e}) at {datetime.now()}')
    finally:
        if config.get('send_notify'):
            bot.notify.bot_status(f'starting reboot at {datetime.now()}')
        print('reloading...')
        time.sleep(5)
        bot.start()
   
        
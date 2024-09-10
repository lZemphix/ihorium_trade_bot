from datetime import datetime
from bot import bot, config
import time




if __name__ == '__main__':
    try:
        bot.activate()
    except Exception as e:
        print(e, e.args)
        if config.get('send_notify'):
            bot.notify.error_notify(f'{e}, at {datetime.now()}')
    finally:
        if config.get('send_notify'):
            bot.notify.error_notify(f'starting reboot at {datetime.now()}')
        print('reloading...')
        time.sleep(5)
        bot.activate()
   
        
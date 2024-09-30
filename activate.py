from datetime import datetime
from bot import bot, config
import traceback
from modules.telenotify import polling
import threading
import logging
from modules.profit_calc import profit

if __name__ == '__main__':
    try:
        threading.Thread(target=bot.start).start()
        threading.Thread(target=polling.update(profit.send_file)).start()
        
    except Exception as e:
        print('err', traceback.format_exc())
        print('bot was stoped!')

        logging.info(traceback.format_exc())
        if config.get('send_notify'):
            bot.notify.warning('Bot was stoped!')
            bot.notify.error(f'Time: {datetime.now()}')

   
        
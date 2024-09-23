from datetime import datetime
from bot import bot, config
import traceback
from requests.exceptions import ReadTimeout

attempts = 0

if __name__ == '__main__':
    try:
        bot.start()

    except Exception as e:
        print('err', traceback.format_exc())
        print('bot was stoped!')
        if config.get('send_notify'):
            bot.notify.error(f'{e} at {datetime.now()}')
            bot.notify.warning('Bot was stoped!')
        if attempts <= 5:
            if config.get('send_notify'):
                bot.notify.bot_status(f'trying to reboot...')
            bot.start()
            attempts += 1
        elif attempts > 5:
            if config.get('send_notify'):
                bot.notify.error('attempts > 5! bot was stoped!')

   
        
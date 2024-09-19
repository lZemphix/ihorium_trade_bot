from .telenotify import SendNotify
import logging

class NotifySettings:

    def __init__(self, telegram_notify: bool = True, logging_notify: bool = True, print_notify: bool = True) -> None:
        self.telegram_notify = telegram_notify
        self.logging_notify = logging_notify
        self.print_notify = print_notify

    def notify(self, level: int, message: str) -> None:
        """level=comment
        levels: 0 - bot_status, 1 - bought, 2 - sold, 3 - warning, 4 - error"""
        
        if self.telegram_notify:
            ntf = SendNotify(True)
            if level == 0:
                ntf.bot_status(message)
            elif level == 1:
                ntf.bought(message)
            elif level == 2:
                ntf.sold(message)
            elif level == 3:
                ntf.warning(message)
            elif level == 4:
                ntf.error(message)
            
        if self.logging_notify:
            if level == 0:
                logging.info(f'[Bot status]: {message}')
            elif level == 1:
                logging.info(f'[Bought]: {message}')
            elif level == 2:
                logging.info(f'[Sold]: {message}')
            elif level == 3:
                logging.info(f'[Warning]: {message}')
            elif level == 4:
                logging.info(f'[Error]: {message}')

        if self.print_notify:
            if level == 0:
                print(f'[Bot status]: {message}')
            elif level == 1:
                print(f'[Bought]: {message}')
            elif level == 2:
                print(f'[Sold]: {message}')
            elif level == 3:
                print(f'[Warning]: {message}')
            elif level == 4:
                print(f'[Error]: {message}')
        

ntf = NotifySettings()

if __name__ == '__main__':
    try:
        ntf.notify(0, 'test')
    except Exception as e:
        print(e)
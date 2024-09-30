import time
import requests, os, dotenv

dotenv.load_dotenv()

class SendNotify:
    def __init__(self, status: bool) -> None:
        self.status = status
        self.TOKEN = os.getenv('BOT_TOKEN')
        self.CHAT_ID = os.getenv('CHAT_ID')

    def send_message(self, title: str, message: str) -> int:
        if self.status:
            msg = f'*{title}*\n{message}'
            url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
            payload = {
                'chat_id': self.CHAT_ID,
                'text': msg,
                'parse_mode': 'Markdown'
            }
            
            resp = requests.post(url, json=payload)
            return resp.status_code
        else:
            pass
    
    
    def bot_status(self, message: str):
        status_code = self.send_message('🔔Bot status!', message)
        return status_code
    
    def bought(self, message: str):
        status_code = self.send_message('📉Buy!', message)
        return status_code

    def sold(self, message: str):
        status_code = self.send_message('📈Sell!', message)
        return status_code

    def error(self, message: str):
        status_code = self.send_message('❌Error!', message)
        return status_code

    def warning(self, message: str):
        status_code = self.send_message('⚠️Warning!', message)
        return status_code
    
    def send_file(self, file_path: str, title: str = None, caption: str = None):
        if self.status:
            url = f"https://api.telegram.org/bot{self.TOKEN}/sendDocument"
            data = {'chat_id': self.CHAT_ID}
            if caption and title:

                msg = f'*{title}*\n{caption}'
                data['caption'] = msg
                data['parse_mode'] = 'Markdown'

            files = {'document': open(file_path, 'rb')}
            
            resp = requests.post(url, files=files, data=data)
            return resp.status_code
        else:
            pass

class Pooling:
    def __init__(self) -> None:
        self.TOKEN = os.getenv('BOT_TOKEN')
        self.CHAT_ID = os.getenv('CHAT_ID')


    def get_updates(self, offset=None):
        url = f"https://api.telegram.org/bot{self.TOKEN}/getUpdates"
        params = {'timeout': 100,
                  'offset': offset}
        resp = requests.get(url, params=params)
        return resp.json()
    
    def update(self, func):
        offset = None
        while True:
            updates = self.get_updates(offset)
            for update in updates['result']:
                if 'message' in update:
                    text = update['message']['text']
                    if text.lower() == "/profit":
                        func()
                    offset = update['update_id'] + 1
            time.sleep(1)

polling = Pooling()
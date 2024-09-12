import os
from pushbullet import PushBullet
from dotenv import load_dotenv

load_dotenv()

class Notify:
    def __init__(self) -> None:
        self.device_token = os.getenv('DEVICE_TOKEN')
        self.pb = PushBullet(self.device_token)

    def send_notify(self, title: str, text: str) -> None:
        self.pb.push_note(title, text)

    def trade_status(self, text: str) -> None:
        self.pb.push_note('Trading status', text)

    def bot_status(self, text: str) -> None:
        self.pb.push_note('Bot status', text)

    def balance_status(self, text: str) -> None:
        self.pb.push_note('Balance status', text)

    def error_notify(self, text: str) -> None:
        self.pb.push_note('Error', text)

class FakeNotify:
    
    def send_notify(self, title: str, text: str):
        pass
    def trade_status(self, text: str):
        pass
    def bot_status(self, text: str):
        pass
    def balance_status(self, text: str):
        pass
    def error_notify(self, text: str):
        pass
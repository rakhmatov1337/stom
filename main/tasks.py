import requests


class TelegramBotService:
    BOT_TOKEN = '7780875320:AAF-xLME-WRTeqMu6XC_XuM5WZIxHGc8E1A'
    
    ADMIN_CHAT_IDS = ['5255423236', '6709695039']  # example additional admins

    @classmethod
    def send_to_user(cls, chat_id, text):
        cls._send(chat_id, text)

    @classmethod
    def send_to_admin(cls, text):
        for admin_id in cls.ADMIN_CHAT_IDS:
            cls._send(admin_id, text)

    @classmethod
    def _send(cls, chat_id, text):
        url = f"https://api.telegram.org/bot{cls.BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"Telegram xatolik: {e}")

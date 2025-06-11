import jwt

SECRET_KEY = "SAME_SECRET_AS_IN_BOT"  # bot tomonda yaratgan secret
ALGORITHM = "HS256"


def decode_telegram_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # {'telegram_id': 123456789, ...}
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

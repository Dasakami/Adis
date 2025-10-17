import random
from django.conf import settings
from twilio.rest import Client
from .models import PhoneVerificationCode

def generate_code():
    return str(random.randint(100000, 999999))

def send_sms_code_to_number(phone_number: str) -> str:
    code = generate_code()
    PhoneVerificationCode.objects.create(phone_number=phone_number, code=code)
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        body=f"Ваш код подтверждения: {code}",
        from_="+12294713777",
        to=phone_number
    )
    print("Twilio SID:", msg.sid)
    return code

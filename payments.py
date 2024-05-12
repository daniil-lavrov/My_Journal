import uuid

import yookassa
from yookassa import Configuration, Payment
import config

Configuration.account_id = config.YO_KASSA_ACC_ID
Configuration.secret_key = config.YO_KASSA_SECRET_KEY


def create(amount, chat_id, description):
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/myJjjournal_bot"
        },
        "capture": True,
        "metadata": {
            'chat_id': chat_id
        },
        "description": description
    }, id_key)

    return payment.confirmation.confirmation_url, payment.id

def check(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False

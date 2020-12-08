from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from requests_html import HTMLSession

session = HTMLSession()
from .models import Patient, Answer
import requests
import random
import string
import json


def send_survey_link(sender, instance=None, **kwargs):
    if instance is not None:
        unique_id = instance.uuid
        survey_id = instance.survey.id

        subject = "Complete Your Survey"
        html_message = render_to_string("send_survey_link.html", context={"uuid": unique_id, "survey_id": survey_id})
        if instance.is_used is False:
            response = session.post(
                "https://api.mailgun.net/v3/sandbox5301a79097994dd5a621705473034cc2.mailgun.org/messages",
                auth=("api", settings.MAILGUN_API_KEY),
                data={
                    "from": settings.DEFAULT_EMAIL,
                    "to": [instance.email],
                    "subject": subject,
                    "text": html_message,
                },
            )


def send_acknowledgement(sender, instance=None, **kwargs):
    if instance is not None:

        html_message = render_to_string("send_acknowledgement.html", context=None)

        if instance.patient.is_used is False:
            pass
        else:
            print("Invalid link")

        response = session.post(
            settings.MAILGUN_API_URL,
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": settings.DEFAULT_EMAIL,
                "to": [instance.patient.email],
                "subject": "ESH Survey",
                "text": html_message,
            },
        )

        instance.patient.is_used = True
        instance.patient.save()


def random_alphanumeric(length=6):
    str_ = string.ascii_lowercase + string.digits
    result = "".join((random.choice(str_) for i in range(length)))
    return result


def send_money(sender, instance=None, **kwargs):

    if instance.patient.is_used is False:
        pass
    else:
        print("Invalid link")

    headers = {
        "Authorization": f"Bearer {settings.RAVE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "account_bank": instance.patient.bank_name,
        "account_number": instance.patient.account_number,
        "amount": instance.survey.reward_amount,
        "narration": "ESH Survey",
        "currency": "NGN",
        "beneficiary_name": "Test Name",
        "reference": f"ESH-{random_alphanumeric()}",
        "debit_currency": "NGN",
        "meta": {
            "first_name": instance.patient.first_name,
            "last_name": instance.patient.last_name,
            "email": instance.patient.email,
            "mobile_number": instance.patient.mobile_number,
        },
    }

    req = requests.post(
        "https://api.flutterwave.com/v3/transfers",
        data=json.dumps(payload),
        headers=headers,
    )
    instance.patient.is_paid = True
    instance.patient.save()
    print(req.json())


def send_sms(sender, instance=None, **kwargs):

    if instance.patient.is_used is False:
        pass
    else:
        print("Invalid link")
    params = {
        "user": settings.SMS_USER,
        "password": settings.SMS_PASSWORD,
        "mobile": "09060528731",
        "senderid": "ESH Survey",
        "message": "We don wire you money o! check your aza",
    }

    response = requests.get("https://sms.com.ng/sendsms.php", params=params)

    print(response.text)


post_save.connect(
    send_survey_link, sender=Patient, dispatch_uid="send_survey_link"
)

post_save.connect(
    send_acknowledgement, sender=Answer, dispatch_uid="send_acknowledgement"
)

post_save.connect(send_money, sender=Answer, dispatch_uid="send_money")

post_save.connect(send_sms, sender=Answer, dispatch_uid="send_sms")

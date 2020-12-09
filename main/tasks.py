import os
import json
import requests
import random
import string
from django.template.loader import render_to_string
from requests_html import HTMLSession

session = HTMLSession()
from django.conf import settings
from background_task import background
from .models import Patient


@background(schedule=10)
def send_acknowledgement(survey_id, uuid):
    patient = Patient.objects.get(uuid=uuid, survey__id=survey_id)

    html_message = render_to_string("send_acknowledgement.html", context=None)

    if patient.is_used is False:
        pass
    else:
        print("Invalid link")

    response = session.post(
        settings.MAILGUN_API_URL,
        auth=("api", settings.MAILGUN_API_KEY),
        data={
            "from": settings.DEFAULT_EMAIL,
            "to": [patient.email],
            "subject": "ESH Survey",
            "text": html_message,
        },
    )


"""
@background(schedule=10)
def send_sms(survey_id, uuid):

	patient = Patient.objects.get(uuid=uuid, survey__id=survey_id)

	if patient.is_used is False:
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
"""


def random_alphanumeric(length=6):
    str_ = string.ascii_lowercase + string.digits
    result = "".join((random.choice(str_) for i in range(length)))
    return result


@background(schedule=15)
def send_money(survey_id, uuid):
    patient = Patient.objects.get(uuid=uuid, survey__id=survey_id)

    if patient.is_used is False and patient.is_paid is False:

        headers = {
            "Authorization": f"Bearer {settings.RAVE_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "account_bank": patient.bank_name,
            "account_number": patient.account_number,
            "amount": patient.survey.reward_amount,
            "narration": "ESH Survey",
            "currency": "NGN",
            "beneficiary_name": "Test Name",
            "reference": f"ESH-{random_alphanumeric()}",
            "debit_currency": "NGN",
            "meta": {
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "email": patient.email,
                "mobile_number": patient.mobile_number,
            },
        }

        req = requests.post(
            "https://api.flutterwave.com/v3/transfers",
            data=json.dumps(payload),
            headers=headers,
        )

        patient.is_used = True
        patient.is_paid = True
        patient.save()

        print(req.json())

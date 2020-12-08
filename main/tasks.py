from django.template.loader import render_to_string
from django.conf import settings
from requests_html import HTMLSession

session = HTMLSession()
from background_task import background
from .models import Patient
import requests
import json
import string
import random


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
		"dnd": 1,
	}

	response = requests.get(
		"https://sms.com.ng/sendsms.php",
		params=params
	)

	print(response.text)


def random_alphanumeric(length=6):
    str_ = string.ascii_lowercase + string.digits
    result = "".join((random.choice(str_) for i in range(length)))
    return result


@background(schedule=10)
def send_money(survey_id, uuid):

	patient = Patient.objects.get(uuid=uuid, survey__id=survey_id)

	if patient.is_used is False:
		pass
	else:
		print("Invalid link")

	headers = {
	    "Authorization": f"Bearer {settings.RAVE_API_KEY}",
	    "Content-Type": "application/json"
	}

	payload = {
	    "account_bank": "044",
	    "account_number": "0690000040",
	    "amount": patient.survey.reward_amount,
	    "narration": "ESH Survey",
	    "currency": "NGN",
	    "beneficiary_name": "Test Name",
	    "reference": f"ESH-{random_alphanumeric()}",
	    "debit_currency": "NGN",
	    "meta": {
	        "first_name": "Test",
	        "last_name": "Name",
	        "email": patient.email,
	        "mobile_number": patient.mobile_number,
	    },
	}

	req = requests.post("https://api.flutterwave.com/v3/transfers", data=json.dumps(payload), headers=headers)
	print(req.json())


@background(schedule=10)
def send_acknowledgement(survey_id, uuid):
	
	patient = Patient.objects.get(uuid=uuid, survey__id=survey_id)

	html_message = render_to_string(
		"send_acknowledgement.html", context=None
	)

	if patient.is_used is False:
		pass
	else:
		print("Invalid link")
		
	response = session.post(
		"https://api.mailgun.net/v3/sandbox5301a79097994dd5a621705473034cc2.mailgun.org/messages",
		auth=("api", settings.MAILGUN_API_KEY),
		data={
			"from": settings.DEFAULT_EMAIL,
			"to": [patient.email],
			"subject": "ESH Survey",
			"text": html_message,
		},
	)

	patient.is_used = True
	patient.save()

	send_money(survey_id, uuid)

	send_sms(survey_id, uuid)
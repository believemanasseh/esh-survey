from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from requests_html import HTMLSession

session = HTMLSession()
from .models import Patient, Answer
import requests
import json
import string
import random
from background_task import background


@background(schedule=15)
def send_survey_link(sender, instance=None, **kwargs):
	if instance is not None:
		unique_id = instance.uuid
		survey_id = instance.survey.id

		subject = "Complete Your Survey"
		html_message = render_to_string(
			"send_survey_link.html", {"survey_id": survey_id, "uuid": unique_id}
		)

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


@background(schedule=15)
def send_sms(sender, instance=None, **kwargs):
	if instance is not None:
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


@background(schedule=15)
def send_money(sender, instance=None, **kwargs):
	if instance is not None:
		if instance.patient.is_used is False:
			pass
		else:
			print("Invalid link")

		headers = {
		    "Authorization": "Bearer FLWSECK-1bf181d6b2922c6e5840206ea1f7b3b6-X",
		    "Content-Type": "application/json"
		}

		payload = {
		    "account_bank": "044",
		    "account_number": "0690000040",
		    "amount": instance.survey.reward_amount,
		    "narration": "ESH Survey",
		    "currency": "NGN",
		    "beneficiary_name": "Test Name",
		    "reference": f"ESH-{random_alphanumeric()}",
		    "callback_url": "https://webhook.site/b3e505b0-fe02-430e-a538-22bbbce8ce0d",
		    "debit_currency": "NGN",
		    "meta": {
		        "first_name": "Test",
		        "last_name": "Name",
		        "email": instance.patient.email,
		        "mobile_number": instance.patient.mobile_number,
		    },
		}

		req = requests.post("https://api.flutterwave.com/v3/transfers", data=json.dumps(payload), headers=headers)
		print(req.json())


@background(schedule=15)
def send_acknowledgement(sender, instance=None, **kwargs):
	if instance is not None:
		patient_email = instance.patient.email

		html_message = render_to_string(
			"send_acknowledgement.html", context=None
		)

		if instance.patient.is_used is False:
			pass
		else:
			print("Invalid link")
			
		response = session.post(
			"https://api.mailgun.net/v3/sandbox5301a79097994dd5a621705473034cc2.mailgun.org/messages",
			auth=("api", settings.MAILGUN_API_KEY),
			data={
				"from": settings.DEFAULT_EMAIL,
				"to": [patient_email],
				"subject": "ESH Survey",
				"text": html_message,
			},
		)
		patient = Patient.objects.get(uuid=instance.patient.uuid)
		patient.is_used = True
		patient.save()



post_save.connect(
	send_survey_link, sender=Patient, dispatch_uid="send_survey_link"
)

post_save.connect(send_sms, sender=Answer, dispatch_uid="send_sms")

post_save.connect(
	send_money, sender=Answer, dispatch_uid="send_money"
)

post_save.connect(
	send_acknowledgement, sender=Answer, dispatch_uid="send_acknowledgement"
)

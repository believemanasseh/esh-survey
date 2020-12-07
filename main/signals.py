from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from requests_html import HTMLSession

session = HTMLSession()
from .models import Patient, Answer
import json


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


def send_acknowledgement(sender, instance=None, **kwargs):
	if instance is not None:
		patient_email = instance.patient.email

		html_message = render_to_string(
			"send_acknowledgement.html", context=None
		)

		if instance.patient.is_used is False:
			
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


def send_sms(sender, instance=None, **kwargs):
	if instance is not None:
		if instance.patient.is_used is False:
			data = {
				"username": settings.SMS_USERNAME,
				"password": settings.SMS_PASSWORD,
				"sender": "ESH Survey",
				"recipient": instance.patient.mobile_number,
				"message": "We don wire you money o! check your aza"
			}

			import requests

			response = requests.post(
				"https://sms.com.ng/api",
				data=json.dumps(data),
			)

			print(response.text)


post_save.connect(
	send_survey_link, sender=Patient, dispatch_uid="send_survey_link"
)

post_save.connect(send_sms, sender=Answer, dispatch_uid="send_sms")

post_save.connect(
	send_acknowledgement, sender=Answer, dispatch_uid="send_acknowledgement"
)

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from requests_html import HTMLSession

session = HTMLSession()
from .models import Patient


def send_survey_link(sender, instance=None, **kwargs):
	if instance is not None:
		unique_id = instance.uuid
		survey_id = instance.survey.id

		subject = "Complete Your Survey"
		html_message = render_to_string("send_survey_link.html", context={"uuid": unique_id, "survey_id": survey_id})
		if instance.sent_email is False:
			response = session.post(
				settings.MAILGUN_API_URL,
				auth=("api", settings.MAILGUN_API_KEY),
				data={
					"from": settings.DEFAULT_EMAIL,
					"to": [instance.email],
					"subject": subject,
					"text": html_message,
				},
			)
			instance.sent_email = True
			instance.save()

post_save.connect(
	send_survey_link, sender=Patient, dispatch_uid="send_survey_link"
)
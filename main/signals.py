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

post_save.connect(
    send_survey_link, sender=Patient, dispatch_uid="send_survey_link"
)
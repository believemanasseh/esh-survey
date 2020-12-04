from django.db import models
from django.utils import timezone
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from .constants import BANKS
import uuid


class Survey(models.Model):
    title = models.CharField(max_length=250, blank=True, null=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    reward_amount = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    ANSWER_TYPE = (
        ("Multiselect", "Multiselect"),
        ("Short text", "Short text"),
        ("Paragraph", "Paragraph"),
        ("Rating", "Rating"),
    )

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, blank=True, null=False)
    answer_type = models.CharField(max_length=20, choices=ANSWER_TYPE, default='')
    options = models.TextField(blank=True, null=True)
    ratings = models.TextField(blank=True, null=True)
    serial_no = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Patient(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False
    )
    account_name = models.CharField(max_length=250, blank=True, null=False)
    account_number = models.CharField(max_length=250, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=False)
    bank_name = models.CharField(max_length=3, choices=BANKS, default='')
    is_used = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    def __str__(self):
        return self.account_name


class Answer(models.Model):
    text = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.text

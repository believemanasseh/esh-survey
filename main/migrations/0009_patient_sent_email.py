# Generated by Django 3.1 on 2020-12-09 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_survey_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='sent_email',
            field=models.BooleanField(default=False),
        ),
    ]

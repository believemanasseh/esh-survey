from django.contrib import admin
from . import models


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
	list_filter = ["id", "title", "start_date", "end_date", "reward_amount", "description"]
	list_display = ["id", "title", "start_date", "end_date", "reward_amount", "description"]


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
	list_filter = ["id", "survey_id", "title", "answer_type", "options", "serial_no", "pub_date"]
	list_display = ["id", "survey_id", "title", "answer_type", "options", "serial_no", "pub_date"]


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
	list_filter = ["id", "text", "question", "patient", "survey"]
	list_display = ["id", "text", "question", "patient", "survey"]


@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
	list_filter = ["uuid", "last_name", "bank_name", "is_used"]
	list_display = ["uuid", "last_name", "bank_name", "is_used"]


admin.site.site_title = "ESH Survey"
admin.site.site_header = "ESH Survey Administration"
admin.site.index_title = "Admin Panel"
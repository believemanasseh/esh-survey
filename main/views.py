from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Patient, Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
import uuid


@api_view(["GET", "POST"])
def survey(request, survey_id, uuid):
	try:
		patient = Patient.objects.get(
			uuid=uuid, survey__id=survey_id
		)
		questions = Question.objects.filter(
			survey__id=survey_id,
		)
	except Question.DoesNotExist:
		raise Http404

	if request.method == "GET":
		serializer = QuestionSerializer(questions, many=True)
		if patient.is_used == True:
			return Response({
				"status": "error",
				"message": "Invalid link",
			}, status=status.HTTP_404_DOES_NOT_EXIST)

		return Response({
			"status": "success",
			"message": "Survey retreived successfully",
			"survey_title": questions[0].survey.title,
			"data": {
				"questions": serializer.data
			}
		}, status=status.HTTP_200_OK)
	
	elif request.method == "POST":
		serializer = AnswerSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			text = serializer.validated_data["text"]
			if patient.is_used == True:
				return Response({
					"status": "error",
					"message": "Invalid link",
				}, status=status.HTTP_404_DOES_NOT_EXIST)

			for obj in text:
				question = Question.objects.get(id=obj["question"])
				Answer.objects.create(
					text=obj["text"], question=question, patient=patient
				)
			Response({
				"status": "success",
				"message": "Survey submitted successfully",
			})
	

	return Response({
		"status": "error",
		"message": "Invalid request",
		"error": serializer.errors
	}, status=status.HTTP_400_BAD_REQUEST)

















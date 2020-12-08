from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg2.utils import swagger_auto_schema
from .models import Survey, Patient, Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
import uuid
import json


@swagger_auto_schema(
	method="get",
	operation_description="GET /{survey_id}/{uuid}/",
	tags=["Survey"],
)
@swagger_auto_schema(
	method="post",
	operation_description="POST /{survey_id}/{uuid}/",
	request_body=AnswerSerializer,
	tags=["Survey"],
)
@api_view(["GET", "POST"])
def survey(request, survey_id, uuid):
	try:
		patient = Patient.objects.get(uuid=uuid, survey__id=survey_id)
		questions = Question.objects.filter(
			survey__id=survey_id,
		)
	except Exception:
		return Response(
			{
				"status": "error",
				"message": "Invalid link"
			},
			status=status.HTTP_404_NOT_FOUND,
		)

	if request.method == "GET":
		base_domain = "https://survey-b.herokuapp.com/"
		serializer = QuestionSerializer(questions, many=True)
		if patient.is_used == True:
			return Response(
				{
					"status": "error",
					"message": "Invalid link",
				},
				status=status.HTTP_404_NOT_FOUND,
			)

		return Response(
			{
				"status": "success",
				"message": "Survey retreived successfully",
				"title": questions[0].survey.title,
				"description": questions[0].survey.description,
				"data": {"questions": serializer.data},
			},
			status=status.HTTP_200_OK,
		)

	elif request.method == "POST":
		serializer = AnswerSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			text = serializer.validated_data["text"]
			if patient.is_used == True:
				return Response(
					{
						"status": "error",
						"message": "Invalid link",
					},
					status=status.HTTP_404_NOT_FOUND,
				)

			for obj in text:
				question = Question.objects.get(id=obj["question"])
				survey = Survey.objects.get(id=survey_id)
				Answer.objects.create(
					text=obj["text"],
					question=question,
					patient=patient,
					survey=survey,
				)

			return Response(
				{
					"status": "success",
					"message": "Survey submitted successfully",
				},
				status=status.HTTP_200_OK,
			)

	return Response(
		{
			"status": "error",
			"message": "Invalid request",
			"error": serializer.errors,
		},
		status=status.HTTP_400_BAD_REQUEST,
	)


@csrf_exempt
@require_POST
def webhook(request):
	request_body = request.body
	json_data= json.loads(request_body)

	if json_data["data"]["status"] == "SUCCESSFUL":
		try:
			user_email = json_data["data"]["meta"]["email"]
			patient = Patient.objects.get(email=user_email)
		except ObjectDoesNotExist:
			raise Http404

		patient.is_paid = True
		patient.save()

		return HttpResponse(status=200)

	elif json_data["data"]["status"] == "FAILED":

		return HttpResponse(status=200)


	return HttpResponse("Webhook url for ESH survey!")



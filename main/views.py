from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg2.utils import swagger_auto_schema
from .models import Patient, Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
import uuid


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
    except Question.DoesNotExist:
        raise Http404

    if request.method == "GET":
        serializer = QuestionSerializer(questions, many=True)
        if patient.is_used == True:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid link",
                },
                status=status.HTTP_404_DOES_NOT_EXIST,
            )

        return Response(
            {
                "status": "success",
                "message": "Survey retreived successfully",
                "survey_title": questions[0].survey.title,
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
                Answer.objects.create(
                    text=obj["text"], question=question, patient=patient
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

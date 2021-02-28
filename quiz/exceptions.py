from rest_framework import status
from rest_framework.exceptions import APIException

class QuizNotTakenException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'User did not attempted this quiz.'
    default_code = 'invalid'
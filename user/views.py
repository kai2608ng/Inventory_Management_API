from rest_framework.views import APIView
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response

User = get_user_model

class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data = {'messages': 'Account created successfully'})
        return Response(serializer.errors)

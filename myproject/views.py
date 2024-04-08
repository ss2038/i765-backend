from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Person
from ..myapp.serializers import PersonSerializer

class PersonView(APIView):
    def post(self, request, format=None):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

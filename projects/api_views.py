from rest_framework import viewsets
from rest_framework.response import Response

class ProjectViewSet(viewsets.ModelViewSet):
    def list(self, request):
        return Response({"message": "API Coming Soon!"})

class ProjectMembershipViewSet(viewsets.ModelViewSet):
    def list(self, request):
        return Response({"message": "API Coming Soon!"})

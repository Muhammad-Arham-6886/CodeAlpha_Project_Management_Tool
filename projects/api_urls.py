from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet)
router.register(r'memberships', api_views.ProjectMembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework import routers

from tables import views


router = routers.SimpleRouter()

router.register('api/table', views.TableView, basename='table')

urlpatterns = router.urls

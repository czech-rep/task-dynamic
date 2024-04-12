from django.urls import path, include
from rest_framework import routers

from tables import views


# app_name = 'rooms'

router = routers.SimpleRouter()
# router.include_root_view = False

router.register('api/table', views.TableView, basename='table')

urlpatterns = router.urls
# [
#     path('', include(router.urls)),
# ]

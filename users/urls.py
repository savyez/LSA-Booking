from django.urls import path
from .views import ParentView, LSASearchView

urlpatterns = [
    #parents urls
    path('parents/', ParentView.as_view(), name="parent-view"),

    #LSAs urls
    path('lsas/search/', LSASearchView.as_view(), name="LSA-search"),
]
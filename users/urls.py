from django.urls import path
from .views import ParentView, LSAProfileView, LSASearchView

urlpatterns = [
    # parents urls
    path('parents/', ParentView.as_view(), name="parent-view"),

    # LSAs urls
    path('lsas/', LSAProfileView.as_view(), name="lsa-profile"),
    path('lsas/search/', LSASearchView.as_view(), name="LSA-search"),
]
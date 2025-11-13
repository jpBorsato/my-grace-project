from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("entries/", views.EntryListView.as_view(), name="entry-list"),
    path("entry/<int:pk>/", views.EntryDetailView.as_view(), name="entry-detail-id"),
    path(
        "entry/<slug:slug>/", views.EntryDetailView.as_view(), name="entry-detail-slug"
    ),
    path("search/", views.search, name="search"),
]

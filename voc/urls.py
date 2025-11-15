from django.urls import path

from . import views


urlpatterns = [
    # Home
    path("", views.index, name="index"),
    # Entries (global)
    path("entries/", views.EntryListView.as_view(), name="entry-list"),
    path("entries/<slug:slug>/", views.EntryDetailView.as_view(), name="entry-detail"),
    # Authors
    path("authors/", views.AuthorListView.as_view(), name="author-list"),
    path(
        "authors/<slug:author_slug>/entries/",
        views.AuthorEntryListView.as_view(),
        name="author-entry-list",
    ),
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path(
        "categories/entries/",
        views.EntryByCategoryListView.as_view(),
        name="entry-by-category-list",
    ),
    path(
        "categories/<slug:category_slug>/entries/",
        views.CategoryEntryListView.as_view(),
        name="category-entry-list",
    ),
    # Search
    path("search/", views.search, name="search"),
]

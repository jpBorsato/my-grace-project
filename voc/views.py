import os
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db import connection
from django.views.generic import ListView, DetailView
from datetime import datetime
from dotenv import load_dotenv


from voc.models import Author, Entry, TradTerm

load_dotenv()


def query(query_object):
    with connection.cursor() as cursor:
        return cursor.execute(**query_object).fetchall()


def index(request):
    return redirect("author-list")


def status(request):
    updated_at = datetime.now().isoformat()

    db_version_res = query({"sql": "SHOW server_version;"})
    db_version_val = db_version_res[0][0]

    db_max_conn_res = query({"sql": "SHOW max_connections;"})
    db_max_conn_val = db_max_conn_res[0][0]

    db_name = os.getenv("POSTGRES_DB")
    db_open_conn_res = query(
        {
            "sql": "SELECT count(*)::int FROM pg_stat_activity WHERE datname = %s",
            "params": (db_name,),
        }
    )
    db_open_conn_val = db_open_conn_res[0][0]

    data = {
        "updated_at": updated_at,
        "dependencies": {
            "database": {
                "version": db_version_val,
                "max_connections": db_max_conn_val,
                "opened_connections": db_open_conn_val,
            },
        },
    }

    return JsonResponse(data)


class EntryListView(ListView):
    model = Entry
    template_name = "voc/entry_list.html"
    context_object_name = "entry_list"
    paginate_by = 100

    def get_queryset(self):
        queryset = Entry.objects.all().order_by_abc_lowercase()

        # Get query string parameters
        author_filter = self.request.GET.getlist("author")
        trad_term_filter = self.request.GET.get("category")

        # Apply filters based on query parameters
        if author_filter:
            author = get_list_or_404(Author, slug__in=author_filter)
            queryset = queryset.filter(cotext__reference__authors__in=author)

        if trad_term_filter:
            trad_term = get_object_or_404(TradTerm, slug=trad_term_filter)
            queryset = queryset.filter(trad_term=trad_term)

        return queryset


class EntryDetailView(DetailView):
    model = Entry
    template_name = "voc/entry_detail.html"
    context_object_name = "entry"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = context["entry"]
        context["related_entries"] = []
        for related_list, type in [
            (entry.antonyms(), "antonym"),
            (entry.homonyms(), "homonym"),
            (entry.synonyms(), "synonym"),
            (entry.near_synonyms(), "near-synonym"),
        ]:
            for e in related_list:
                context["related_entries"].append(
                    {
                        "type": type,
                        "author": {
                            "name": e.cotext.reference.formatted_authors(),
                            "slugs": e.authors_slugs(),
                        },
                        "entry": e,
                    }
                )
        return context


class AuthorListView(ListView):
    model = Author
    template_name = "voc/author_list.html"
    context_object_name = "author_list"
    paginate_by = 100


class AuthorEntryListView(ListView):
    model = Entry
    template_name = "voc/author_entry_list.html"
    context_object_name = "entry_list"
    paginate_by = 100

    @property
    def author(self):
        author_slug = self.kwargs["author_slug"]
        author = get_object_or_404(Author, slug=author_slug)
        return author

    def get_queryset(self):
        queryset = Entry.objects.filter(
            cotext__reference__authors=self.author
        ).order_by_abc_lowercase()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = self.author
        return context


class CategoryListView(ListView):
    model = TradTerm
    template_name = "voc/category_list.html"
    context_object_name = "category_list"
    paginate_by = 100


class EntryByCategoryListView(ListView):
    model = Entry
    template_name = "voc/entry_by_category_list.html"
    context_object_name = "entry_list"
    paginate_by = 100

    def get_queryset(self):
        queryset = Entry.objects.all().order_by_abc_lowercase(["trad_term"])
        return queryset


class CategoryEntryListView(ListView):
    model = Entry
    template_name = "voc/category_entry_list.html"
    context_object_name = "entry_list"
    paginate_by = 100

    @property
    def trad_term(self):
        trad_term_slug = self.kwargs["category_slug"]
        trad_term = get_object_or_404(TradTerm, slug=trad_term_slug)
        return trad_term

    def get_queryset(self):
        queryset = Entry.objects.filter(
            trad_term=self.trad_term
        ).order_by_abc_lowercase()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.trad_term
        return context


def search(request):
    """
    Handles both JSON and HTML search results.
    If the request is AJAX (live typing), return JSON.
    If it's a normal GET (button click or Enter), render a template.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        # For empty search, show empty page or redirect

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"results": {}})
        return render(request, "voc/search_results.html", {"query": "", "results": {}})

    entries_objs = Entry.objects.filter(term__text__icontains=query)
    entries_list = [
        {"slug": entry.slug, "text": str(entry)} for entry in entries_objs[:5]
    ]
    authors_objs = Author.objects.filter(full_name__icontains=query)
    authors_list = [
        {"slug": author.slug, "text": str(author)} for author in authors_objs[:5]
    ]
    categories_objs = TradTerm.objects.filter(text__icontains=query)
    categories_list = [
        {"slug": category.slug, "text": str(category)}
        for category in categories_objs[:5]
    ]

    # Handle AJAX (dropdown)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "results": {
                    "entries": {"list": entries_list, "url": "entries/"},
                    "authors": {"list": authors_list, "url": "entries/?author="},
                    "categories": {
                        "list": categories_list,
                        "url": "entries/?category=",
                    },
                }
            }
        )

    # Handle full search (button click or enter)
    return render(
        request,
        "voc/search_results.html",
        {
            "query": query,
            "results": {
                "entries": entries_objs,
                "authors": authors_objs,
                "categories": categories_objs,
            },
        },
    )

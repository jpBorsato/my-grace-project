from django.contrib import admin
from django.utils.html import format_html
from .models import *


@admin.register(Cotext)
class CotextAdmin(admin.ModelAdmin):
    list_display = ("short_text", "text_date", "reference")
    search_fields = ("text", "reference__title", "reference__authors__last_name")
    list_filter = ("text_date",)
    autocomplete_fields = ["reference"]

    @admin.display(description="Cotext")
    def short_text(self, obj):
        return obj.short_text


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ("title", "authors__last_name", "authors__first_name")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    search_fields = ("text",)


@admin.register(GeneralChar)
class GeneralCharAdmin(admin.ModelAdmin):
    search_fields = ("text",)


@admin.register(TradTerm)
class TradTermAdmin(admin.ModelAdmin):
    search_fields = ("text",)


@admin.register(TradRelation)
class TradRelationAdmin(admin.ModelAdmin):
    search_fields = ("text",)


@admin.register(GrammClass)
class GrammClassAdmin(admin.ModelAdmin):
    search_fields = ("text",)


@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):
    search_fields = ("text",)


def pretty_numbered_text(numbered_objs):
    n = len(numbered_objs)
    if n == 0:
        return ""
    elif n == 1:
        return numbered_objs[0][1]
    return format_html(
        " ".join(
            [
                f'<span style="font-weight: bold;">{index}.\n</span> {obj}'
                for index, obj in numbered_objs
            ]
        )
    )


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = [
        "entry",
        "term_definitions",
        "cotexts",
        "concept_anl",
        "general_char",
        "specific_chars",
        "trad_term",
        "trad_term_def",
        "trad_relation",
        "term_gramm_class",
        "note",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["homonym_number"]
    list_filter = [
        "term",
        "general_char",
        "trad_term",
        "trad_relation",
        "term_gramm_class",
    ]
    search_fields = (
        "term__text",
        "term_def__text",
        "cotext__text",
        "concept_anl",
        "specific_char__text",
    )
    autocomplete_fields = [
        "term",
        "general_char",
        "trad_term",
        "trad_relation",
        "term_gramm_class",
    ]
    filter_vertical = ["term_def", "cotext", "specific_char"]

    @admin.display(description="Entry")
    def entry(self, obj):
        return obj
    
    @admin.display(description="Term Definitions")
    def term_definitions(self, obj):
        numbered_defs = [
            (index, obj) for index, obj in enumerate(obj.term_def.all(), 1)
        ]
        return pretty_numbered_text(numbered_defs)

    @admin.display(description="Cotexts")
    def cotexts(self, obj):
        numbered_cotexts = [
            (index, obj.short_text) for index, obj in enumerate(obj.cotext.all(), 1)
        ]
        return pretty_numbered_text(numbered_cotexts)

    @admin.display(description="Specific Characteristics")
    def specific_chars(self, obj):
        return "; ".join([char.text for char in obj.specific_char.all()]) + "."

    @admin.display(description="Trad. Term Definition")
    def trad_term_def(self, obj):
        if obj.trad_term:
            return obj.trad_term.definition
        return None


admin.site.register(Author)
admin.site.register(SpecificChar)

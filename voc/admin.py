from django.contrib import admin
from django.utils.html import format_html
from .models import *


@admin.register(Cotext)
class CotextAdmin(admin.ModelAdmin):
    list_display = ("id", "short_text", "text_date", "date_granularity", "reference")
    search_fields = ("id", "text", "reference__title", "reference__authors__last_name")
    list_filter = ("text_date",)
    autocomplete_fields = ["reference"]

    @admin.display(description="Cotext")
    def short_text(self, obj):
        return obj.short_text(100)


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


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


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


@admin.register(EntryRelations)
class EntryRelationsAdmin(admin.ModelAdmin):
    list_display = [
        "edit",
        "type",
        "entry",
        "view_entry_on_site",
        "related_entry",
        "view_rel_entry_on_site",
        "has_symmetrical"
    ]

    list_display_links = ["edit",]

    @admin.display(description="Edit")
    def edit(self, obj):
        return "Edit"
    
    @admin.display(description="Has Symmetrical", boolean=True)
    def has_symmetrical(self, obj):
        return obj.has_symmetrical

    @admin.display(description="View Entry On Site")
    def view_entry_on_site(self, obj):
        return format_html(f"<a target='_blank' href={obj.entry.get_absolute_url()}>View</a>")

    @admin.display(description="View Rel. Entry On Site")
    def view_rel_entry_on_site(self, obj):
        return format_html(f"<a target='_blank' href={obj.related_entry.get_absolute_url()}>View</a>")


class EntryRelationsInline(admin.TabularInline):
    model = EntryRelations
    fk_name = "entry"
    extra = 1
    fields = (
        "type",
        "related_entry",
    )
    autocomplete_fields = ("related_entry",)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "edit",
        "view_on_site",
        "edit_term",
        "phonetic_transcription",
        "term_definitions",
        "edit_cotext",
        "cotext__text_date",
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

    list_display_links = ["edit"]

    inlines = [
        EntryRelationsInline,
    ]

    fields = [
        "view_on_site",
        "term",
        "term_def",
        "cotext",
        "concept_anl",
        "general_char",
        "specific_char",
        "trad_term",
        "trad_relation",
        "term_gramm_class",
        "note",
        "slug",
        "homonym_number",
    ]
    readonly_fields = ["view_on_site", "homonym_number"]

    list_filter = [
        "trad_term",
        "general_char",
        "specific_char",
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
        "cotext",
        "general_char",
        "trad_term",
        "trad_relation",
        "term_gramm_class",
    ]
    filter_vertical = ["term_def", "specific_char"]

    @admin.display(description="Cotext", ordering="cotext")
    def edit_cotext(self, obj):
        cotext = obj.cotext
        full_text = cotext.display_text(full=True, id=False) if cotext else "No Cotext"
        short_text = cotext.display_text(max_length=50) if cotext else "No Cotext"
        return format_html(
            f"<span title='{full_text}'><a target='_blank' href='/admin/voc/cotext/{cotext.id}/change/?_to_field=id&_popup=1'>{short_text}</a></span>"
        )

    @admin.display(description="Term", ordering="term")
    def edit_term(self, obj):
        return format_html(
            f"<a target='_blank' href='/admin/voc/term/{obj.term.id}/change/?_to_field=id&_popup=1'>{obj}</a>"
        )

    @admin.display(description="Phonetic Transcription", ordering="term")
    def phonetic_transcription(self, obj):
        return obj.term.phonetic_transcription

    @admin.display(description="Term Definitions")
    def term_definitions(self, obj):
        numbered_defs = [
            (index, obj) for index, obj in enumerate(obj.term_def.all(), 1)
        ]
        return pretty_numbered_text(numbered_defs)

    @admin.display(description="Cotext date")
    def date(self, obj):
        return obj.cotext.text_date

    @admin.display(description="Specific Characteristics")
    def specific_chars(self, obj):
        return "; ".join([char.text for char in obj.specific_char.all()]) + "."

    @admin.display(description="Trad. Term Definition")
    def trad_term_def(self, obj):
        if obj.trad_term:
            return obj.trad_term.definition
        return None

    @admin.display(description="View On Site")
    def view_on_site(self, obj):
        return format_html(f"<a target='_blank' href={obj.get_absolute_url()}>View</a>")

    @admin.display(description="Edit")
    def edit(self, obj):
        return "Edit"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Logic to create the symmetrical EntryRelations instance
        for relation in obj.relations_as_source.all():
            if not EntryRelations.objects.filter(
                entry=relation.related_entry,
                related_entry=relation.entry,
                type=relation.type,
            ).exists():
                EntryRelations.objects.create(
                    entry=relation.related_entry,
                    related_entry=relation.entry,
                    type=relation.type,
                )

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        # Logic to create the symmetrical EntryRelations instance for inline formsets
        for form_instance in formset.save(commit=False):
            if form_instance.related_entry and form_instance.entry:
                if not EntryRelations.objects.filter(
                    entry=form_instance.related_entry,
                    related_entry=form_instance.entry,
                    type=form_instance.type,
                ).exists():
                    EntryRelations.objects.create(
                        entry=form_instance.related_entry,
                        related_entry=form_instance.entry,
                        type=form_instance.type,
                    )


admin.site.register(SpecificChar)

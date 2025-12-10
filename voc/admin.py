from django import forms
from django.contrib import admin
from django.utils import formats
from django.utils.html import format_html
from django.contrib.admin.widgets import AdminDateWidget
from django.conf import settings
from .models import *


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

current_date_format = formats.get_format("DATE_INPUT_FORMATS")[0].replace("%", "")

class CotextAdminForm(forms.ModelForm):
    class Meta:
        model = Cotext
        fields = '__all__'
        widgets = {
            'text_date': AdminDateWidget(attrs={'placeholder': current_date_format}),
        }

@admin.register(Cotext)
class CotextAdmin(admin.ModelAdmin):
    form = CotextAdminForm
    list_display = (
        "id",
        "edit",
        "cotext_text",
        "text_date",
        "date_granularity",
        "reference",
        "location",
    )
    list_display_links = ("edit",)
    search_fields = ("id", "text", "reference__title", "reference__authors__last_name")
    list_filter = (
        "reference__authors",
        "reference",
    )
    autocomplete_fields = ["reference"]

    @admin.display(description="Edit")
    def edit(self, obj):
        return "Edit"

    @admin.display(description="Text")
    def cotext_text(self, obj):
        cotext = obj
        full_text = cotext.display_text(full=True, id=False, ref=False)
        short_text = cotext.display_text(max_length=100, id=False, ref=False)
        return format_html(
            f"<span title='{full_text}'>{short_text}</span>"
        )

    @admin.display(description="Location")
    def location(self, obj):
        return obj.loc_in_ref


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


entry_definition_intermediate = Entry.term_def.through


class DefinitionInlineAdmin(admin.TabularInline):
    model = entry_definition_intermediate
    autocomplete_fields = ["definition"]
    verbose_name = "Definition"
    verbose_name_plural = "Definitions"
    extra = 0


@admin.register(SpecificChar)
class SpecificCharAdmin(admin.ModelAdmin):
    fields = [
        "text",
    ]
    search_fields = ("text",)


entry_spec_char_intermediate = Entry.specific_char.through


class SpecificCharlineAdmin(admin.TabularInline):
    model = entry_spec_char_intermediate
    autocomplete_fields = ["specificchar"]
    verbose_name = "Specific Characteristic"
    verbose_name_plural = "Specific Characteristics"
    extra = 0

    @admin.display(description="Specific Characteristic")
    def specific_char(self, obj):
        return obj.specificchar.text


@admin.register(EntryRelations)
class EntryRelationsAdmin(admin.ModelAdmin):
    list_display = [
        "edit",
        "type",
        "entry",
        "view_entry_on_site",
        "related_entry",
        "view_rel_entry_on_site",
        "has_symmetrical",
    ]

    list_display_links = [
        "edit",
    ]

    @admin.display(description="Edit")
    def edit(self, obj):
        return "Edit"

    @admin.display(
        description="Has Symmetrical", boolean=True, ordering="has_symmetrical"
    )
    def has_symmetrical(self, obj):
        return obj.has_symmetrical

    @admin.display(description="View Entry On Site")
    def view_entry_on_site(self, obj):
        return format_html(
            f"<a target='_blank' href={obj.entry.get_absolute_url()}>View</a>"
        )

    @admin.display(description="View Rel. Entry On Site")
    def view_rel_entry_on_site(self, obj):
        return format_html(
            f"<a target='_blank' href={obj.related_entry.get_absolute_url()}>View</a>"
        )

    def delete_queryset(self, request, queryset):
        """
        Override bulk delete to ensure each instance's delete() is called,
        triggering symmetrical deletion logic.
        """
        for obj in queryset:
            obj.delete()


class EntryRelationsInline(admin.TabularInline):
    model = EntryRelations
    fk_name = "entry"
    verbose_name = "Entry Relation"
    verbose_name_plural = "Entry Relations"
    extra = 0
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
        "view",
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

    inlines = [DefinitionInlineAdmin, SpecificCharlineAdmin, EntryRelationsInline]

    fields = [
        "term",
        "cotext",
        "concept_anl",
        "general_char",
        "trad_term",
        "trad_relation",
        "term_gramm_class",
        "note",
        "slug",
        "homonym_number",
    ]
    readonly_fields = [
        "homonym_number",
    ]

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
        "term_def",
        "cotext",
        "general_char",
        "trad_term",
        "trad_relation",
        "term_gramm_class",
    ]

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
    def view(self, obj):
        return format_html(f"<a target='_blank' href={obj.get_absolute_url()}>View</a>")

    @admin.display(description="Edit")
    def edit(self, obj):
        return "Edit"

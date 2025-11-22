from django.db import models
from django.db.models import F, Max
from django.db.models.functions import Lower
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify


class Author(models.Model):
    """Represents an author of a bibliographic reference."""

    first_name = models.CharField("First name", max_length=100, blank=True)
    last_name = models.CharField("Last name", max_length=100)
    full_name = models.CharField(
        "Full name",
        max_length=255,
        help_text="Used when author name does not fit standard first/last pattern (e.g. Michel de Montaigne).",
        blank=True,
    )
    description = models.TextField("Description", blank=True, null=True)
    slug = models.SlugField(
        "Slug",
        unique=True,
        blank=True,
        null=True,
        max_length=255,
        help_text="Auto-generated from name if not provided.",
    )

    def __str__(self):
        if self.full_name:
            return self.full_name
        return (
            f"{self.last_name}, {self.first_name}"
            if self.first_name
            else self.last_name
        )

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ["last_name", "first_name"]

    def save(self, *args, **kwargs):
        """
        Automatically:
        - Generate a unique slug from name.
        """
        if not self.slug:
            self.slug = slugify(self)
        super().save(*args, **kwargs)


class Reference(models.Model):
    """Stores bibliographic references with structured metadata."""

    authors = models.ManyToManyField(Author, related_name="references", blank=True)
    title = models.CharField("Title", max_length=500)
    year = models.PositiveIntegerField("Publication year", null=True, blank=True)
    publisher = models.CharField("Publisher", max_length=255, null=True, blank=True)
    city = models.CharField("Publication city", max_length=255, null=True, blank=True)
    source_type = models.CharField(
        "Source type",
        max_length=50,
        choices=[
            ("BOOK", "Book"),
            ("ARTICLE", "Article"),
            ("CHAPTER", "Book Chapter"),
            ("THESIS", "Thesis"),
            ("ONLINE", "Online Resource"),
            ("OTHER", "Other"),
        ],
        default="BOOK",
    )
    citation = models.TextField(
        "Formatted citation",
        blank=True,
        help_text="Optional preformatted citation text (e.g. APA or ABNT style).",
    )

    def formatted_authors(self):
        authors = self.authors.all()
        if not authors:
            return "Unknown author"
        if len(authors) == 1:
            return str(authors[0])
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."

    def __str__(self):
        base = f"{self.formatted_authors()}: {self.title}"
        if self.year:
            base += f" ({self.year})"
        return base

    class Meta:
        verbose_name = "Reference"
        verbose_name_plural = "References"
        ordering = ["title"]


class Cotext(models.Model):
    text = models.TextField("Cotext")
    text_date = models.DateField("Cotext date", null=True, blank=True)
    date_granularity = models.SmallIntegerField(
        "Cotext date granularity",
        choices=[
            (0, "No date"),
            (1, "Year"),
            (2, "Year and month"),
            (3, "Full date"),
        ],
        default=3,
    )
    reference = models.ForeignKey(
        Reference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cotexts",
    )
    loc_in_ref = models.CharField(
        "Location in reference",
        help_text="e.g. p. 84.",
        max_length=100,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.display_text(30)

    class Meta:
        verbose_name = "Cotext"
        verbose_name_plural = "Cotexts"

    def display_text(self, max_length=100, full=False, id=True, ref=True):
        end = (
            max(self.text.find(" ", max_length), max_length)
            if not full
            else len(self.text)
        )
        ret_str = "..." if end < (len(self.text) - 3) else ""
        loc_str = f" {self.loc_in_ref}." if self.loc_in_ref else ""
        ref_str = (f" ({self.reference}.{loc_str})" if self.reference else "") if ref else ""
        id_str = f" [id: {self.id}]" if id else ""
        return self.text[:end] + ret_str + ref_str + id_str

    @property
    def full_description(self):
        loc_str = f" {self.loc_in_ref}." if self.loc_in_ref else ""
        ref_str = f" ({self.reference}.{loc_str})" if self.reference else ""
        return self.text + ref_str

    @property
    def template_date_format(self):
        formats = {0: None, 1: "Y", 2: "M, Y", 3: "M j, Y"}
        return formats[self.date_granularity]


class TradTerm(models.Model):
    text = models.CharField("Traditional term", max_length=255)
    definition = models.TextField("Traditional term definition")
    slug = models.SlugField(
        "Slug",
        unique=True,
        blank=True,
        null=True,
        max_length=255,
        help_text="Auto-generated from text if not provided.",
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Traditional Term"
        verbose_name_plural = "Traditional Terms"
        ordering = ["text"]

    def save(self, *args, **kwargs):
        """
        Automatically:
        - Generate a unique slug from text.
        """
        if not self.slug:
            self.slug = slugify(self.text)
        super().save(*args, **kwargs)


class GeneralChar(models.Model):
    text = models.CharField("General characteristic", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "General Characteristic"
        verbose_name_plural = "General Characteristics"
        ordering = ["text"]


class Term(models.Model):
    text = models.TextField("Term")
    phonetic_transcription = models.CharField(
        "Phonetic transcription", max_length=100, null=True, blank=True
    )

    def __str__(self):
        return self.text or f"Entry {self.id}"

    class Meta:
        verbose_name = "Term"
        verbose_name_plural = "Terms"
        ordering = ["text"]


class Definition(models.Model):
    text = models.TextField("Definition")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Definition"
        verbose_name_plural = "Definitions"


class SpecificChar(models.Model):
    text = models.CharField("Specific characteristic", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Specific Characteristic"
        verbose_name_plural = "Specific Characteristics"
        ordering = ["text"]


class TradRelation(models.Model):
    text = models.CharField("Relation", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Relation Between Term and Traditional Term"
        verbose_name_plural = "Relations Between Term and Traditional Term"
        ordering = ["text"]


class GrammClass(models.Model):
    text = models.CharField("Grammatical class", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Grammatical Class"
        verbose_name_plural = "Grammatical Classes"
        ordering = ["text"]


class EntryRelations(models.Model):
    entry = models.ForeignKey(
        "Entry",
        verbose_name="Entry",
        on_delete=models.CASCADE,
        related_name="relations_as_source",
    )
    type = models.CharField(
        "Relation type",
        max_length=50,
        choices=[
            ("SYNONYM", "Synonym"),
            ("ANTONYM", "Antonym"),
        ],
    )
    related_entry = models.ForeignKey(
        "Entry",
        verbose_name="Related Entry",
        on_delete=models.CASCADE,
        related_name="relations_as_target",
    )

    class Meta:
        verbose_name = "Entry Relations"
        verbose_name_plural = verbose_name
        ordering = ["entry", "type", "related_entry"]
        unique_together = ("entry", "type", "related_entry")

    def __str__(self):
        return f"{self.type.capitalize()}: \"{self.entry}\" with \"{self.related_entry}\""

    @property
    def has_symmetrical(self):
        return EntryRelations.objects.filter(entry=self.related_entry, type=self.type, related_entry=self.entry).exists()
    
    def get_symmetrical(self):
        if self.has_symmetrical:
            symmetrical = EntryRelations.objects.get(entry=self.related_entry, type=self.type, related_entry=self.entry)
            return symmetrical
        return None

    def save(self, *args, **kwargs):
        """
        Save relation and ensure the symmetrical relation also exists.
        Prevent infinite recursion by tracking creation stage.
        """
        creating = self.pk is None
        super().save(*args, **kwargs)

        if creating and not self.has_symmetrical:
            # Create the reverse relation
            EntryRelations.objects.create(
                entry=self.related_entry,
                type=self.type,
                related_entry=self.entry
            )

    def delete(self, *args, **kwargs):
        """
        Delete this relation and also delete the symmetrical one if it exists.
        """
        symmetrical = self.get_symmetrical()
        super().delete(*args, **kwargs)
        if symmetrical:
            symmetrical.delete()

class EntryQuerySet(models.QuerySet):
    def order_by_abc_lowercase(self, precedent_fields=[], subsequent_fields=[]):
        return self.annotate(term_lowercase=Lower(F("term__text"))).order_by(
            *precedent_fields, "term_lowercase", "homonym_number", *subsequent_fields
        )


class EntryManager(models.Manager):
    def get_queryset(self):
        return EntryQuerySet(self.model, using=self._db)


class Entry(models.Model):
    term = models.ForeignKey(
        Term, verbose_name="Term", on_delete=models.CASCADE, related_name="entries"
    )
    homonym_number = models.PositiveSmallIntegerField(
        "Homonym number",
        default=1,
        help_text="Used to distinguish homonymous entries of the same term (e.g., ¹, ², ³).",
    )
    related_entries = models.ManyToManyField(
        "self",
        verbose_name="Related entries",
        through=EntryRelations,
        blank=True,
    )
    term_def = models.ManyToManyField(
        Definition, verbose_name="Term definition", related_name="entries"
    )
    cotext = models.ForeignKey(
        Cotext,
        on_delete=models.SET_NULL,
        verbose_name="Cotext",
        related_name="entries",
        null=True,
        blank=True,
    )
    concept_anl = models.TextField("Conceptual analysis")
    general_char = models.ForeignKey(
        GeneralChar,
        verbose_name="General characteristic",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries",
    )
    specific_char = models.ManyToManyField(
        SpecificChar, verbose_name="Specific characteristic", related_name="entries"
    )
    trad_term = models.ForeignKey(
        TradTerm,
        verbose_name="Traditional term",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries",
    )
    trad_relation = models.ForeignKey(
        TradRelation,
        verbose_name="Relation Term and Trad. Term",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries",
    )
    term_gramm_class = models.ForeignKey(
        GrammClass,
        verbose_name="Term grammatical class",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries",
    )
    note = models.TextField("Note", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated at", auto_now=True)
    slug = models.SlugField(
        "Slug",
        unique=True,
        blank=True,
        null=True,
        max_length=255,
        help_text="Auto-generated from term text and homonym number if not provided.",
    )

    objects = EntryManager()

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        ordering = ["id"]
        unique_together = ("term", "homonym_number")

    def __str__(self):
        return f"{self.term}{self.homonym_suffix}"

    def authors_slugs(self):
        return [author.slug for author in self.cotext.reference.authors.all()]

    @property
    def has_antonyms(self):
        return self.relations_as_source.filter(type="ANTONYM").exists()

    def antonyms(self):
        return [
            relation.related_entry
            for relation in self.relations_as_source.filter(type="ANTONYM")
        ]

    @property
    def has_homonyms(self):
        return Entry.objects.filter(term=self.term).count() > 1

    @property
    def has_synonyms(self):
        return self.relations_as_source.filter(type="SYNONYM").exists()

    def synonyms(self):
        return [
            relation.related_entry
            for relation in self.relations_as_source.filter(type="SYNONYM")
        ]

    @property
    def homonym_suffix(self):
        """Return the superscript number for display."""
        superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        if not self.has_homonyms and self.homonym_number <= 1:
            return ""
        number_str = "".join(superscripts[int(d)] for d in str(self.homonym_number))
        return number_str

    def homonyms(self):
        return (
            Entry.objects.filter(term=self.term)
            .exclude(homonym_number=self.homonym_number)
            .order_by("homonym_number")
        )

    def definitions(self):
        return self.term_def.all()

    def definitions_textblock(self):
        defs = self.definitions()
        if defs.count() > 1:
            return " ".join([f"{n}. {d}" for n, d in enumerate(defs, 1)])
        return defs.first()

    def get_absolute_url(self):
        return reverse("entry-detail", args=[str(self.slug)])

    def save(self, *args, **kwargs):
        """
        Automatically:
        - Assign next homonym number if needed.
        - Generate a unique slug from term text and homonym number.
        """
        creating = not self.pk
        # 1️⃣ Assign homonym number if this is a new entry
        if creating and self.term:
            last_number = Entry.objects.filter(term=self.term).aggregate(
                Max("homonym_number")
            )["homonym_number__max"]
            self.homonym_number = (last_number or 0) + 1

        # 2️⃣ Generate slug
        if not self.slug:
            base_slug = slugify(self.term.text)

            # ensure uniqueness (in case of manual edits)
            unique_slug = base_slug
            counter = 1
            while Entry.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                counter += 1
                unique_slug = f"{base_slug}-{counter}"

            self.slug = unique_slug

        super().save(*args, **kwargs)

entry_definition_intermediate = Entry.term_def.through
entry_definition_intermediate.__str__ = lambda obj: ""

entry_specificchar_intermediate = Entry.specific_char.through
entry_specificchar_intermediate.specificchar.verbose_name = "Specific characteristic"
entry_specificchar_intermediate.__str__ = lambda obj: ""
entry_specificchar_intermediate._meta.ordering = ["entry", "specificchar"]

# 🔁 SIGNAL: Reorder homonym numbers after deletion
@receiver(post_delete, sender=Entry)
def reorder_homonym_numbers(sender, instance, **kwargs):
    """
    After an entry is deleted, renumber remaining entries of the same term.
    """
    siblings = Entry.objects.filter(term=instance.term).order_by("homonym_number", "id")

    for i, entry in enumerate(siblings, start=1):
        if entry.homonym_number != i:
            entry.homonym_number = i
            entry.save(update_fields=["homonym_number"])

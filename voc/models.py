from django.db import models
from django.db.models import Max
from django.db.models.signals import post_delete
from django.dispatch import receiver


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
        loc_str = f" {self.loc_in_ref}." if self.loc_in_ref else ""
        ref_str = f" ({self.reference}.{loc_str})" if self.reference else ""
        return self.text + ref_str

    class Meta:
        verbose_name = "Cotext"
        verbose_name_plural = "Cotexts"

    @property
    def short_text(self):
        end = max(self.text.find(" ", 100), 100)
        ret_str = "..." if end < (len(self.text) - 3) else ""
        loc_str = f" {self.loc_in_ref}." if self.loc_in_ref else ""
        ref_str = f" [{self.reference}.{loc_str}]" if self.reference else ""
        return self.text[:end] + ret_str + ref_str


class TradTerm(models.Model):
    text = models.CharField("Traditional term", max_length=255)
    definition = models.TextField("Traditional term definition")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Traditional Term"
        verbose_name_plural = "Traditional Terms"
        ordering = ["text"]


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


class Entry(models.Model):
    term = models.ForeignKey(
        Term, verbose_name="Term", on_delete=models.CASCADE, related_name="entries"
    )
    homonym_number = models.PositiveSmallIntegerField(
        "Homonym number",
        default=1,
        help_text="Used to distinguish homonymous entries of the same term (e.g., ¹, ², ³).",
    )
    term_def = models.ManyToManyField(
        Definition, verbose_name="Term definition", related_name="entries"
    )
    cotext = models.ManyToManyField(
        Cotext, verbose_name="Cotext", related_name="entries"
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

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        ordering = ["-updated_at"]
        unique_together = ("term", "homonym_number")

    def __str__(self):
        return f"{self.term}{self.homonym_suffix}"

    @property
    def has_homonyms(self):
        return Entry.objects.filter(term=self.term).count() > 1

    @property
    def homonym_suffix(self):
        """Return the superscript number for display."""
        superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        if not self.has_homonyms and self.homonym_number <= 1:
            return ""
        number_str = "".join(superscripts[int(d)] for d in str(self.homonym_number))
        return number_str

    def save(self, *args, **kwargs):
        """
        Automatically assign the next available homonym number
        if this is a new entry for an existing term.
        """
        if not self.pk and self.term:  # Only on creation
            last_number = Entry.objects.filter(term=self.term).aggregate(
                Max("homonym_number")
            )["homonym_number__max"]
            if last_number:
                self.homonym_number = last_number + 1
            else:
                self.homonym_number = 1
        super().save(*args, **kwargs)


# 🔁 SIGNAL: Reorder homonym numbers after deletion
@receiver(post_delete, sender=Entry)
def reorder_homonym_numbers(sender, instance, **kwargs):
    """
    After an entry is deleted, renumber remaining entries of the same term
    so that homonym_number stays sequential (1, 2, 3...).
    """
    siblings = Entry.objects.filter(term=instance.term).order_by("homonym_number", "id")

    for i, entry in enumerate(siblings, start=1):
        if entry.homonym_number != i:
            entry.homonym_number = i
            entry.save(update_fields=["homonym_number"])

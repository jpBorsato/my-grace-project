from django.db import models


class Context(models.Model):
    text = models.TextField("Context")
    text_date = models.DateField("Context date", null=True, blank=True)
    source = models.CharField("Context source", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Context"
        verbose_name_plural = "Contexts"
        ordering = ["text_date"]


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
    contexts = models.ManyToManyField(
        Context, through="Entry", verbose_name="Contexts", related_name='terms')

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
        ordering = ["text"]


class SpecificChar(models.Model):
    text = models.CharField("Specific characteristic", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Specific Characteristic"
        verbose_name_plural = "Specific Characteristics"
        ordering = ["text"]

class TradRelation(models.Model):
    text = models.CharField("Traditional relation", max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Traditional Relation"
        verbose_name_plural = "Traditional Relations"
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
        Term,
        verbose_name="Term",
        on_delete=models.CASCADE,
        related_name="entries"
    )
    term_def = models.ManyToManyField(
        Definition, verbose_name="Term definition", related_name="entries"
    )
    context = models.ForeignKey(
        Context,
        verbose_name="Context",
        on_delete=models.CASCADE,
        related_name="entries"
    )
    concept_anl = models.TextField("Conceptual analysis")
    general_char = models.ForeignKey(
        GeneralChar,
        verbose_name="General Characteristic",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries"
    )
    specific_char = models.ManyToManyField(
        SpecificChar, verbose_name="Specific characteristic", related_name="entries"
    )
    trad_term = models.ForeignKey(
        TradTerm,
        verbose_name="Traditional term",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries"
    )
    trad_relation = models.ForeignKey(
        TradRelation,
        verbose_name="Traditional relation",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries")
    term_gramm_class = models.ForeignKey(
        GrammClass,
        verbose_name="Term grammatical class",
        null=True,
        on_delete=models.SET_NULL,
        related_name="entries")
    note = models.TextField("Note", null=True, blank=True)

    def __str__(self):
        return f'{self.term} | {self.context}'

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
        ordering = ["term"]

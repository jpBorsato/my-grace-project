from django.core.management.base import BaseCommand
from django.utils.text import slugify
from voc.models import Entry, Author, TradTerm


class Command(BaseCommand):
    help = "Save objects to rebuild missing or empty slugs."

    def handle(self, *args, **options):
        for entry in Entry.objects.all():
            if not entry.slug:
                entry.save()

        for author in Author.objects.all():
            if not author.slug:
                author.save()
        
        for trad_term in TradTerm.objects.all():
            if not trad_term.slug:
                trad_term.save()

from django.core.management.base import BaseCommand
from ...models import *
import csv


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/category.csv', 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                row = ",".join(row)
                row = row.split(',')
                Category.objects.create(
                    name=row[0]
                    )
        self.stdout.write(self.style.SUCCESS(
            'Countries added Successfully!!'
        ))

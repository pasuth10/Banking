from django.core.management.base import BaseCommand, CommandError

from bank.models import Customer


class Command(BaseCommand):
    def handle(self, *args, **options):
        list = [ { "id": 1, "name": "Arisha Barron" }, { "id": 2, "name": "Branden Gibson" }, { "id": 3, "name": "Rhonda Church" }, { "id": 4, "name": "Georgina Hazel" } ]
        for li in list:
            customer = Customer.objects.get_or_create(name=li.get('name',''))
            print(li.get('name',''))
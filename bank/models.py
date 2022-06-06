from django.db import models

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=200)


class Bank(models.Model):
    bank_name = models.CharField(max_length=200)
    bank_number = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amounts = models.DecimalField(decimal_places=2)


class History(models.Model):
    bank_from = models.ForeignKey(Bank, related_name='histories_bank_from', on_delete=models.CASCADE)
    bank_to = models.ForeignKey(Bank, related_name='histories_bank_to', on_delete=models.CASCADE)
    value = models.IntegerField()

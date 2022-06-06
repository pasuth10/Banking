from rest_framework import serializers

from bank.models import Customer, Bank, History


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name']


class BankSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name')

    class Meta:
        model = Bank
        fields = ['id', 'bank_name', 'bank_number', 'amounts', 'customer_id', 'customer_id', 'customer_name']


class HistorySerializer(serializers.ModelSerializer):
    bank_from_name = serializers.CharField(source='bank_from.bank_name')
    bank_from_number = serializers.CharField(source='bank_from.bank_number')
    bank_to_name = serializers.CharField(source='bank_to.bank_name')
    bank_to_number = serializers.CharField(source='bank_to.bank_number')

    class Meta:
        model = History
        fields = ['id', 'value', 'bank_from_id', 'bank_to_id', 'bank_from_name',
                  'bank_from_number', 'bank_to_name', 'bank_to_number']

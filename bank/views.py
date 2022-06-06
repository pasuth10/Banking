from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Bank, History
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
# Create your views here.
from .serializers import CustomerSerializer, BankSerializer, HistorySerializer


class FormCreateBank(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'create_bank.html'

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(data={'posts': serializer.data})


class FormTransferBank(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'transfer.html'

    def get(self, request):
        bank = Bank.objects.all()
        serializer = BankSerializer(bank, many=True)
        return Response(data={'posts': serializer.data})


class GetCustomerList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(data={'posts': serializer.data})


def add_bank(request):
    customer = request.POST['customer']
    bank_name = request.POST['bank_name']
    bank_number = request.POST['bank_number']
    amounts = request.POST['amounts']
    if Bank.objects.filter(bank_name=bank_name).exists():
        messages.info(request, 'Banking Name is using')
        return redirect('/create_bank')
    elif Bank.objects.filter(bank_number=bank_number).exists():
        messages.info(request, 'Banking Number is using')
        return redirect('/create_bank')
    elif bank_name == '' or bank_number == '' or amounts < 0:
        messages.info(request, 'Data is Wrong !!')
        return redirect('/create_bank')
    else:
        banks = Bank.objects.get_or_create(
            customer_id=customer,
            bank_name=bank_name,
            bank_number=bank_number,
            amounts=amounts
        )
        messages.info(request, 'Success')
        return redirect('/create_bank')


class GetBanksList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'report_balances.html'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request):
        filters = Q()
        search = request.POST.get('search')
        if request.POST.get('search'):
            filters = (filters & Q(id__icontains=search) | Q(amounts__icontains=search) |
                    Q(bank_name__icontains=search) |
                    Q(bank_number__icontains=search) |
                    Q(customer__name__icontains=search)
                    )
        banks = Bank.objects.filter(filters)
        serializer = BankSerializer(banks, many=True)
        return Response(data={'posts': serializer.data})


class GetTransfer(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'report_transfer.html'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request):
        filters = Q()
        search = request.POST.get('search')
        if request.POST.get('search'):
            filters = (filters & Q(id__icontains=search) | Q(value__icontains=search) |
                    Q(bank_from__bank_name__icontains=search) |
                    Q(bank_from__bank_number__icontains=search) |
                    Q(bank_to__bank_name__icontains=search) |
                    Q(bank_to__bank_number__icontains=search)
                    )

        history = History.objects.filter(filters)
        serializer = HistorySerializer(history, many=True)
        return Response(data={'posts': serializer.data})


def transfer(request):
    bank_from = request.POST['bank_from']
    bank_to = request.POST['bank_to']
    amounts = int(request.POST['amounts'])

    banks = Bank.objects.filter(id=bank_from)
    serializer = BankSerializer(banks)
    data = Bank.objects.filter(id=bank_from).values()
    check_amounts = (data[0]['amounts']*1)

    if bank_from == bank_to:
        messages.info(request, 'Bank Account is not same')
        return redirect('/transfer')
    elif check_amounts < amounts:
        txt = 'Amounts in Bank Account is lower {}'
        messages.info(request, txt.format(amounts))
        return redirect('/transfer')
    elif amounts < 0:
        messages.info(request, 'Amounts is Positive !!')
        return redirect('/transfer')
    else:
        history = History.objects.create(
            bank_from_id=bank_from,
            bank_to_id=bank_to,
            value=amounts
        )

        banks = Bank.objects.get(id=bank_from)
        banks.amounts = check_amounts-amounts
        banks.save()

        banks = Bank.objects.get(id=bank_to)
        banks.amounts = amounts+banks.amounts
        banks.save()

        messages.info(request, 'Success')
        return redirect('/transfer')

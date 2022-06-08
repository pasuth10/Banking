from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

from bank.models import Customer, Bank, History
from bank.serializers import (
    CustomerSerializer,
    BankSerializer,
    HistorySerializer
)


# Create your views here.
class FormCreateBank(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'create_bank.html'

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        response_dict = {'posts': serializer.data}
        return Response(data=response_dict, status=status.HTTP_200_OK)


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


class AddBankAPIView(APIView):

    def post(self, request):
        customer = request.data.get('customer')
        bank_name = request.data.get('bank_name')
        bank_number = request.data.get('bank_number')
        amounts = float(request.data.get('amounts'))
        if Bank.objects.filter(bank_name=bank_name).exists():
            messages.info(request, 'Banking Name is using')
            return redirect('/create_bank')

        if Bank.objects.filter(bank_number=bank_number).exists():
            messages.info(request, 'Banking Number is using')
            return redirect('/create_bank')

        if bank_name == '' or bank_number == '' or amounts < 0:
            messages.info(request, 'Data is Wrong !!')
            return redirect('/create_bank')

        Bank.objects.get_or_create(
            customer_id=customer,
            bank_name=bank_name,
            bank_number=bank_number,
            amounts=amounts
        )
        messages.success(request, 'Success')
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
                    Q(customer__name__icontains=search))
        banks = Bank.objects.filter(filters)
        serializer = BankSerializer(banks, many=True)

        return Response(data={'posts': serializer.data}, status=status.HTTP_200_OK)


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
                    Q(bank_to__bank_number__icontains=search))

        history = History.objects.filter(filters)
        serializer = HistorySerializer(history, many=True)
        return Response(data={'posts': serializer.data})


class AddTransferAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        bank_from = request.POST.get('bank_from')
        bank_to = request.POST.get('bank_to')
        amounts = float(request.POST.get('amounts')) # int 1,2,3 : float 1.1, 3.2 ,5.5

        bank_from = Bank.objects.filter(id=bank_from).first()
        if not bank_from:
            txt = 'Bank from not found'
            messages.info(request, txt.format(amounts))
            return redirect('/transfer')

        bank_to = Bank.objects.filter(id=bank_to).first()
        if not bank_to:
            txt = 'Bank to not found'
            messages.info(request, txt.format(amounts))
            return redirect('/transfer')

        # banks = Bank.objects.filter(id=bank_from)
        # serializer = BankSerializer(banks)
        # data = Bank.objects.filter(id=bank_from).values()
        # check_amounts = (data[0]['amounts']*1)
        check_amounts = bank_from.amounts
        if bank_from == bank_to:
            messages.info(request, 'Bank Account is not same')
            return redirect('/transfer')

        if check_amounts < amounts:
            txt = 'Amounts in Bank Account is lower {}'
            messages.info(request, txt.format(amounts))
            return redirect('/transfer')

        if amounts < 0:
            messages.info(request, 'Amounts is Positive !!')
            return redirect('/transfer')

        History.objects.create(
            bank_from=bank_from,
            bank_to=bank_to,
            value=amounts
        )

        bank_from.amounts = float(check_amounts) - amounts
        bank_from.save()

        bank_to.amounts = amounts+float(bank_to.amounts)
        bank_to.save()

        messages.success(request, 'Success')
        return redirect('/transfer')

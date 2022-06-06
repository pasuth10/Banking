"""my_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from bank import views
urlpatterns = [
    path('', include('bank.urls')),
    path('create_bank/', views.FormCreateBank.as_view()),
    path('transfer/', views.FormTransferBank.as_view()),
    path('transfer/transfer', views.transfer),
    path('admin/', admin.site.urls),
    path('create_bank/addbank', views.add_bank),
    path('balances/', views.GetBanksList.as_view(), name='report-balances'),
    path('report_transfer/', views.GetTransfer.as_view(), name='report-transfer')
]

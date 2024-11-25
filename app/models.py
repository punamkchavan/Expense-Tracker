from django.db import models

class UserData(models.Model):
    date = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    phone_no = models.PositiveIntegerField(unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_premium = models.BooleanField(default=False)
    total_expense = models.PositiveIntegerField(default=0)
    total_income = models.PositiveIntegerField(default=0)
    savings = models.PositiveIntegerField(default=0)

class YearlyReport(models.Model):
    year = models.CharField(max_length=255)
    total_income = models.PositiveIntegerField(default=0)
    total_expense = models.PositiveIntegerField(default=0)
    savings = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)

class OrderData(models.Model):
    payment_id = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)

class MoneyData(models.Model):
    date = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    source_type = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)


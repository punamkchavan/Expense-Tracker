from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import OrderData, UserData,MoneyData, YearlyReport
from django.db import transaction
import bcrypt
from django.conf import settings
from datetime import datetime
from django.shortcuts import render
from django.db.models import F
import razorpay
from django.views.decorators.csrf import csrf_exempt
from dotenv import dotenv_values
from django.core.mail import send_mail
from django.template.loader import render_to_string
config = dotenv_values(".env")


RAZORPAY_KEY_ID = config['RAZORPAYKEYID']
RAZORPAY_KEY_SECRET = config['RAZORPAYSECRET']
rzp = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@csrf_exempt
def get_index(request):
    return render(request, 'homePage.html')

@csrf_exempt
def get_before_login_page(request):
    return render(request,'HeaderBeforeLogin.html')

@transaction.atomic
@csrf_exempt
def purchase_premium(request):
    if not request.user:
        return JsonResponse({'message': 'User not found'}, status=400)

    try:
        result = rzp.order.create({'amount': 2000, 'currency': 'INR'})
        user_instance = UserData.objects.get(id=request.user.id)
        order = OrderData.objects.create(order_id=result['id'], status='PENDING', user=user_instance)
        return JsonResponse({'order': result, 'key_id': RAZORPAY_KEY_ID}, status=201)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@transaction.atomic
@csrf_exempt
def update_transaction(request):
    body = request.POST
    order_id = body.get('order_id')
    payment_id = body.get('payment_id')
    if not order_id:
        return JsonResponse({'message': 'Order ID required'}, status=400)

    try:
        if payment_id:
            order_response = OrderData.objects.get(order_id=order_id)
            request.user.is_premium = True
            request.user.save()
            order_response.paymentid = payment_id
            order_response.status = 'SUCCESSFUL'
            order_response.save()
            html_content = render_to_string('transaction_email.html')
            send_mail(
                'Transaction Successful',
                "",
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
                html_message=html_content
            )
            return JsonResponse({'success': True, 'message': 'TRANSACTION SUCCESSFUL'}, status=202)
        else:
            order_response = OrderData.objects.get(order_id=order_id)
            order_response.status = 'FAILED'
            order_response.save()
            return JsonResponse({'success': False, 'message': 'TRANSACTION FAILED'}, status=401)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@csrf_exempt
def check_premium(request):
    if not request.user:
        return JsonResponse({'message': 'User not found'}, status=400)

    try:
        premium_user = UserData.objects.filter(id=request.user.id, is_premium=True).exists()
        return JsonResponse({'result': 'true'} if premium_user else {'result': 'false'})
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@csrf_exempt
def get_registration_page(request):
    return render(request, 'RegistrationPage.html')

@csrf_exempt
def get_login_page(request):
    return render(request, 'LoginPage.html')

@csrf_exempt
@transaction.atomic
def post_registration_data(request):
    if request.method == 'POST':
        body = request.POST
        name = body.get('nameInput')
        phone_no = body.get('phoneInput')
        email = body.get('emailInput')
        password = body.get('passwordInput')
        date = formatDate(datetime.now())

        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = UserData.objects.create(name=name, phone_no=phone_no, email=email, password=hashed_password, date=date)
            user.save()
            return JsonResponse({'message': 'success'}, status=201)
        except Exception as e:
            if 'unique constraint' in str(e):
                return JsonResponse({'message': 'exist'}, status=409)
            else:
                print(e)
                return JsonResponse({'message': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)

@transaction.atomic
@csrf_exempt 
def check_login(request):
    if request.method == 'POST':
        body = request.POST
        email = body.get('email')
        password = body.get('password')
        try:
            user = UserData.objects.get(email=email)
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({'message': 'success', 'token': user.id}, status=201)
            else:
                return JsonResponse({'message': 'Failed'}, status=401)
        except UserData.DoesNotExist:
            return JsonResponse({'message': 'NotExist'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)


@csrf_exempt
def get_expense_main_home_page(request):
    return render(request, 'mainHome.html')

@csrf_exempt
def get_expense_main_page(request):
    return render(request, 'expenseMain.html')


@transaction.atomic
@csrf_exempt
def add_expense(request):
    if request.method == 'POST':
        body = request.POST
        user_id = request.user.id
        amount = int(body.get('Amount'))
        description = body.get('Desc')
        source_type = body.get('Type')
        etype = body.get('Etype')
        date = datetime.now().strftime('%d-%m-%Y')
        formatted_date = datetime.now().strftime('%m-%Y')
        try:
            result = UserData.objects.filter(id=user_id).values('total_expense', 'total_income').first()
            yearly_result = YearlyReport.objects.filter(user_id=user_id, year=formatted_date).values('total_expense', 'total_income', 'year').first()
            total_expense = int(result['total_expense'])
            total_income = int(result['total_income'])
            monthly_total_expense = 0
            monthly_total_income = 0
            if yearly_result:
                monthly_total_expense = int(yearly_result['total_expense'])
                monthly_total_income = int(yearly_result['total_income'])
            money_data_obj = MoneyData.objects.create(
                amount=amount,
                date=date,
                description=description,
                source_type=source_type,
                type=etype,
                user_id=user_id
            )
            if etype == 'Expense':
                if yearly_result:
                    if yearly_result['year'] == formatted_date:
                        YearlyReport.objects.filter(user_id=user_id, year=formatted_date).update(total_expense=monthly_total_expense + amount)
                else:
                    YearlyReport.objects.create(year=formatted_date, total_income=amount, user_id=user_id)
                UserData.objects.filter(id=user_id).update(date=date, total_expense=total_expense + amount)
                calculate_and_update_savings(user_id)
                calculate_and_update_yearly_savings(user_id, formatted_date)
            else:
                if yearly_result:
                    if yearly_result['year'] == formatted_date:
                        YearlyReport.objects.filter(user_id=user_id, year=formatted_date).update(total_income=monthly_total_income + amount)
                else:
                    YearlyReport.objects.create(year=formatted_date, total_income=amount, user_id=user_id)
                UserData.objects.filter(id=user_id).update(date=date, total_income=total_income + amount)
                calculate_and_update_savings(user_id)
                calculate_and_update_yearly_savings(user_id, formatted_date)
            return JsonResponse({'message': 'Data Added Successfully'}, status=201)
        except Exception as e:
            print(e)
            transaction.rollback()
            return JsonResponse({'message': 'Internal Server Error'}, status=500)
    return JsonResponse({'message': 'Invalid Request Method'}, status=400)

@csrf_exempt
def get_expenses_view_page(request):
    return render(request, 'viewExpenses.html')

@csrf_exempt
def get_expenses_data(request):
    if request.method == 'GET':
        limit = int(request.GET.get('rows', 5))
        page = int(request.GET.get('page', 1))
        user_id = request.user.id
        try:
            total_items = MoneyData.objects.filter(user_id=user_id).count()
            expenses_data = MoneyData.objects.filter(user_id=user_id).order_by('-id')[(page - 1) * limit:page * limit]
            return JsonResponse({
                'result': list(expenses_data.values()),
                'currentPage': page,
                'hasNextPage': limit * page < total_items,
                'nextPage': page + 1 if limit * page < total_items else None,
                'hasPreviousPage': page > 1,
                'previousPage': page - 1 if page > 1 else None,
                'lastPage': total_items // limit + 1
            }, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Internal Server Error'}, status=500)
    return JsonResponse({'message': 'Invalid Request Method'}, status=400)

@csrf_exempt
def get_yearly_expenses_data(request):
    user_id = request.user.id
    try:
        yearly_expenses_data = YearlyReport.objects.filter(user_id=user_id).values()
        return JsonResponse(list(yearly_expenses_data), safe=False, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)


@transaction.atomic
@csrf_exempt
def delete_expense_data(request):
    if request.method == 'POST':
        user_id = request.user.id
        body = request.POST
        expense_id = body['id']
        amount = int(body['Amount'])
        etype = body['Etype']
        date = datetime.now().strftime('%d-%m-%Y')
        formatted_date = datetime.now().strftime('%m-%Y')
        try:
            money_data_record = MoneyData.objects.get(id=expense_id, user_id=user_id)
            yearly_result = YearlyReport.objects.get(user_id=user_id, year=formatted_date)
            if etype == 'Expense':
                yearly_result.total_expense -= amount
                yearly_result.savings += amount
                UserData.objects.filter(id=user_id).update(date=date, total_expense=F('total_expense') - amount, savings=F('savings') + amount)
            else:
                yearly_result.total_income -= amount
                yearly_result.savings -= amount
                UserData.objects.filter(id=user_id).update(date=date, total_income=F('total_income') - amount, savings=F('savings') - amount)
            yearly_result.save()
            money_data_record.delete()
            return JsonResponse({'message': 'Expense Deleted Successfully'}, status=200)
        except Exception as e:
            print(e)
            transaction.rollback()
            return JsonResponse({'message': 'Internal Server Error'}, status=500)
    return JsonResponse({'message': 'Invalid Request Method'}, status=400)

@transaction.atomic
@csrf_exempt
def update_expense(request):
    if request.method == 'POST':
        user_id = request.user.id
        body = request.POST
        new_expense_amount = int(body.get('data[Amount]'))
        new_description = body.get('data[Desc]')
        new_expense_type = body.get('data[Type]')
        etype = body.get('Etype')
        expense_id = body.get('id')
        date = datetime.now().strftime('%d-%m-%Y')
        formatted_date = datetime.now().strftime('%m-%Y')
        try:
            with transaction.atomic():
                money_data_record = MoneyData.objects.select_for_update().get(id=expense_id, user_id=user_id)
                old_expense_amount = money_data_record.amount
                money_data_record.date = date
                money_data_record.amount = new_expense_amount
                money_data_record.description = new_description
                money_data_record.source_type = new_expense_type
                money_data_record.save()
                
                yearly_result = YearlyReport.objects.select_for_update().get(user_id=user_id, year=formatted_date)
                expense_amount_difference = old_expense_amount - new_expense_amount

                if etype == 'Expense':
                    yearly_result.total_expense -= expense_amount_difference
                    yearly_result.savings += expense_amount_difference
                    UserData.objects.filter(id=user_id).update(date=date, total_expense=F('total_expense') - expense_amount_difference, savings=F('savings') + expense_amount_difference)
                else:
                    yearly_result.total_income -= expense_amount_difference
                    yearly_result.savings -= expense_amount_difference
                    UserData.objects.filter(id=user_id).update(date=date, total_income=F('total_income') - expense_amount_difference, savings=F('savings') - expense_amount_difference)

                yearly_result.save()
                
                return JsonResponse({'message': 'Expense Updated Successfully'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Internal Server Error'}, status=500)
    return JsonResponse({'message': 'Invalid Request Method'}, status=400)

@csrf_exempt
def get_leader_board_page(request):
    return render(request, 'expenseLeaderBoard.html')

@csrf_exempt
def get_leader_board_data(request):
    try:
        leader_board_data = UserData.objects.all().order_by('-savings').values('name', 'total_expense', 'total_income', 'savings')
        return JsonResponse(list(leader_board_data), safe=False, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@csrf_exempt
def get_view_monetary_page(request):
    return render(request, 'viewMonetaryData.html')

@csrf_exempt
def view_report_expenses_data(request):
    user_id = request.user.id
    try:
        report_expenses_data = MoneyData.objects.filter(user_id=user_id).values()
        return JsonResponse(list(report_expenses_data), safe=False, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@csrf_exempt
def get_savings_data(request):
    user_id = request.user.id
    try:
        savings_data = YearlyReport.objects.filter(user_id=user_id).values()
        return JsonResponse(list(savings_data), safe=False, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Internal Server Error'}, status=500)

@csrf_exempt
def get_expense_graph(request):
    return render(request, 'GraphView.html')

@csrf_exempt
def calculate_and_update_yearly_savings(user_id, formatted_date):
    try:
        yearly_result = YearlyReport.objects.filter(user_id=user_id, year=formatted_date).first()
        if yearly_result:
            total_expense = int(yearly_result.total_expense)
            total_income = int(yearly_result.total_income)
            savings = total_income - total_expense
            yearly_result.savings = savings
            yearly_result.save()
            return savings
        return 0
    except Exception as e:
        print(e)
        return 0

@csrf_exempt
def calculate_and_update_savings(user_id):
    try:
        result = UserData.objects.filter(id=user_id).first()
        if result:
            total_expense = int(result.total_expense)
            total_income = int(result.total_income)
            savings = total_income - total_expense
            result.savings = savings
            result.save()
            return savings
        return 0
    except Exception as e:
        print(e)
        return 0

@csrf_exempt
def formatDate(current_date):
    return current_date.strftime('%d/%m/%Y')
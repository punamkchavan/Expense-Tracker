from django.urls import path
from . import views

urlpatterns = [
    path('user/register/', views.get_registration_page, name='register'),
    path('user/login/', views.get_login_page, name='login'),
    path('user/addUser/', views.post_registration_data, name='add_user'),
    path('user/check-login/', views.check_login, name='check_login'),
    path('', views.get_index, name='homepage'),
    path('payment/premiummember/', views.purchase_premium, name='premium_member'),
    path('payment/updateTransacation/', views.update_transaction, name='update_transaction'),
    path('payment/checkPremium/', views.check_premium, name='check_premium'),
    path('expense/MainHome/', views.get_expense_main_home_page, name='main_home'),
    path('expense/expenseMain/', views.get_expense_main_page, name='expense_main'),
    path('expense/post-expense/', views.add_expense, name='post_expense'),
    path('expense/viewExpenses/', views.get_expenses_view_page, name='view_expenses'),
    path('expense/viewExpensesData/', views.get_expenses_data, name='view_expenses_data'),
    path('expense/deleteExpensedata/', views.delete_expense_data, name='delete_expense_data'),
    path('expense/update-expense/', views.update_expense, name='update_expense'),
    path('expense/leaderBoardPage/', views.get_leader_board_page, name='leader_board'),
    path('expense/viewLeaderBoardData/', views.get_leader_board_data, name='view_leader_board_data'),
    path('expense/viewMonetaryData/', views.get_view_monetary_page, name='view_monetary_data'),
    path('expense/viewYearlyExpensesData/', views.get_yearly_expenses_data, name='view_yearly_expenses_data'),
    path('expense/viewReportExpensesData/', views.view_report_expenses_data, name='view_report_expenses_data'),
    path('expense/viewExpenseGraph/', views.get_expense_graph, name='view_expense_graph'),
    path('expense/getSavingsData/', views.get_savings_data, name='get_savings_data')
]

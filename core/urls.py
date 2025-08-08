from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),

    # Dashboard - protected
    path('dashboard/', views.dashboard, name='dashboard'),

    # Add income/expense - protected
    path('add-income/', views.add_income, name='add_income'),
    path('add-expense/', views.add_expense, name='add_expense'),

    # Signup
    path('signup/', views.signup_view, name='signup'),

    # Login
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),

    # Loans
    path('loan/apply/', views.apply_loan, name='apply_loan'),
    path('loan/view/', views.view_loans, name='view_loans'),
    path('loan/repay/<int:loan_id>/', views.repay_loan, name='repay_loan'),

    # Projects
    path('projects/', views.project_list, name='projects'),
    path('projects/new/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/mark-paid/', views.mark_project_paid, name='mark_project_paid'),
    
    path('print-invoice/', views.print_invoice, name='print_invoice'),

    # Reset Data
    path('reset/', views.reset_data, name='reset_data'),
]

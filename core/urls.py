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
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

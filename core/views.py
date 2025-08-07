from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import IncomeForm, ExpenseForm
from .models import Income, Expense
from django.db.models import Sum
from datetime import timedelta, date

# Public homepage or redirect to dashboard
# def home(request):
#     """
#     Public home page. If authenticated, redirect to dashboard.
#     """
#     if request.user.is_authenticated:
#         return redirect('core:dashboard')
#     return render(request, 'core/home.html')
def home_view(request):
    return render(request, 'core/home.html')


# User signup
def signup_view(request):
    """
    Handles user registration and logs them in upon success.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


# Dashboard
@login_required
def dashboard(request):
    """
    Displays the user's dashboard: financial summaries and charts.
    """
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    net_savings = total_income - total_expense

    labels = []
    income_data = []
    expense_data = []

    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        labels.append(day.strftime('%b %d'))

        daily_income = incomes.filter(date=day).aggregate(total=Sum('amount'))['total'] or 0
        daily_expense = expenses.filter(date=day).aggregate(total=Sum('amount'))['total'] or 0

        income_data.append(daily_income)
        expense_data.append(daily_expense)

    context = {
        'incomes': incomes[:5],
        'expenses': expenses[:5],
        'total_income': total_income,
        'total_expense': total_expense,
        'net_savings': net_savings,
        'chart_labels': labels,
        'chart_income_data': income_data,
        'chart_expense_data': expense_data,
    }

    return render(request, 'core/dashboard.html', context)


# Add Income
@login_required
def add_income(request):
    """
    Handles form for adding a new income entry.
    """
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('core:dashboard')
    else:
        form = IncomeForm()

    return render(request, 'core/add_income.html', {'form': form})


# Add Expense
@login_required
def add_expense(request):
    """
    Handles form for adding a new expense entry.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('core:dashboard')
    else:
        form = ExpenseForm()

    return render(request, 'core/add_expense.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import IncomeForm, ExpenseForm
from .models import Income, Expense
from django.db.models import Sum
from datetime import timedelta, date
from decimal import Decimal
from .forms import LoanForm
from .models import Loan
from .models import Project
from .forms import ProjectForm
from django.contrib import messages
from django.http import JsonResponse

# Public homepage or redirect to dashboard
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
    
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    net_savings = total_income - total_expense
    savings = total_income * Decimal('0.10')  # 10% savings calculation

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
        'savings': savings,
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

# Loan Views
@login_required
def apply_loan(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user

            # Check eligibility: total income >= 1000
            total_income = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
            if total_income >= 1000:
                loan.approved = True
                loan.save()
                messages.success(request, 'Your loan has been approved!')
                return redirect('core:view_loans')
            else:
                form.add_error(None, "Not eligible for loan. Minimum income required is Ksh 1000.")
    else:
        form = LoanForm()

    return render(request, 'core/apply_loan.html', {'form': form})

@login_required
def view_loans(request):
    loans = Loan.objects.filter(user=request.user)
    return render(request, 'core/view_loans.html', {'loans': loans})

@login_required
def repay_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)
    if loan.approved and hasattr(loan, 'is_repaid') and not loan.is_repaid:
        loan.is_repaid = True
        loan.save()
        messages.success(request, 'Loan repaid successfully!')
    return redirect('core:view_loans')

# Projects Views
@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/project_list.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('core:projects')  # This should redirect to project list
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form})

@login_required
def project_detail(request, project_id):
    """View project details and related income entries"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    # Get income entries related to this project
    related_income = Income.objects.filter(user=request.user, project=project).first()
    
    context = {
        'project': project,
        'related_income': related_income,
    }
    return render(request, 'core/project_detail.html', context)

@login_required
def mark_project_paid(request, project_id):
    """Mark a project as paid and automatically create income entry"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        if project.status != 'paid':
            # Manually create income entry
            existing_income = Income.objects.filter(project=project).exists()
            
            if not existing_income:
                # Create income entry
                Income.objects.create(
                    user=project.user,
                    source=f"Project: {project.account_name}",
                    amount=project.amount,
                    date=timezone.now().date(),
                    project=project,
                    description=f"Payment for {project.task or 'Task completion'}"
                )
            
            # Update project status
            project.status = 'paid'
            project.paid_at = timezone.now()
            project.save()
            
            messages.success(request, f'Project marked as paid! Income of Ksh {project.amount} has been added to your dashboard.')
        else:
            messages.info(request, 'Project is already marked as paid.')
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'status': project.status,
            'message': 'Project marked as paid successfully!'
        })
    
    return redirect('core:project_detail', project_id=project.id)
from django import forms
from .models import Income, Expense, Loan, Project

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'description', 'date', 'project']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date']

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['account_name', 'task', 'amount', 'status', 'details']

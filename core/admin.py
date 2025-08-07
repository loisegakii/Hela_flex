from django.contrib import admin
from .models import Income, Expense

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'amount', 'date')

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date')

admin.site.register(Income, IncomeAdmin)
admin.site.register(Expense, ExpenseAdmin)

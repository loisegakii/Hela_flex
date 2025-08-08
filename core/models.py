from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone


# Projects Model
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    task = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
    ], default='pending')
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)  # ✅ New field

    def __str__(self):
        return self.account_name

    def save(self, *args, **kwargs):
        # Check if project is being newly marked as 'paid'
        is_new_paid = False
        if self.pk:
            # Existing object - check previous status
            previous = Project.objects.get(pk=self.pk)
            if previous.status != 'paid' and self.status == 'paid':
                is_new_paid = True
        elif self.status == 'paid':
            # New object being created directly as paid
            is_new_paid = True

        # Save the project first
        super().save(*args, **kwargs)

        # If newly paid, create income if not already created
        if is_new_paid:
            existing_income = Income.objects.filter(project=self).exists()
            if not existing_income:
                Income.objects.create(
                    user=self.user,
                    amount=self.amount,
                    date=timezone.now().date(),
                    project=self,
                    source=f"Project: {self.account_name}",
                    description=f"Payment for {self.task or 'Task'}"
                )
            # Update paid_at time
            self.paid_at = timezone.now()
            super().save(update_fields=['paid_at'])


# Income Model
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=200, default='Manual Entry')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        if self.project:
            return f"Project Payment: {self.project.account_name} - {self.amount}"
        return f"{self.source} - {self.amount} on {self.date}"


# Expense Model
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - {self.amount}"


# Loan Model
class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    term_months = models.PositiveIntegerField(default=12)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_repayment(self):
        return self.amount + (self.amount * self.interest_rate / 100)

    def __str__(self):
        return f"{self.user.username} - Loan of {self.amount}"

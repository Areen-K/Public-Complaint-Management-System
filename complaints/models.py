from django.db import models
from django.contrib.auth.models import User


STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]


class Complaint(models.Model):

    CATEGORY_CHOICES = [
        ('Road', 'Road'),
        ('Water', 'Water'),
        ('Electricity', 'Electricity'),
        ('Garbage', 'Garbage'),
        ('Other', 'Other'),
    ]


    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    priority = models.CharField(
    max_length=10,
    choices=PRIORITY_CHOICES,
    default='Low'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    before_image = models.ImageField(upload_to='complaints/before/', null=True, blank=True)
    after_image = models.ImageField(upload_to='complaints/after/', null=True, blank=True)

    admin_comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.status}"

class ComplaintUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE,related_name='updates')
    remark = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now_add=True)

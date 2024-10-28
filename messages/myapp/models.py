from django.db import models

class EmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  
    
    def __str__(self):
        return self.email

class EmailMessage(models.Model):
    account = models.ForeignKey(EmailAccount, null=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    body = models.TextField()
    attachments = models.JSONField(default=list) 
    
    def __str__(self):
        return f"{self.subject} - {self.account.email}"
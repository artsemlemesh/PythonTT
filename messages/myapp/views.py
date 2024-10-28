from django.shortcuts import render
from django.http import JsonResponse
from .models import EmailMessage, EmailAccount
from .services import EmailFetcher

def email_list_view(request):
    """
    Display the list of emails with a progress bar.
    """
    emails = EmailMessage.objects.all()
    return render(request, 'emails/list.html', {'emails': emails})

def start_email_import(request, account_id):
    """
    Initiates the email fetch process for the specified account.
    """
    try:
        account = EmailAccount.objects.get(id=account_id)
        fetcher = EmailFetcher(account)
        if fetcher.login():
            fetcher.fetch_messages()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Login failed"})
    except EmailAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Account not found"})
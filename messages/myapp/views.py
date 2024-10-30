from django.shortcuts import render
from django.http import JsonResponse
from .models import EmailMessage, EmailAccount
from .services import EmailFetcher
from django.views.decorators.http import require_POST
import json

def fetch_emails_view(request):
    email_account = EmailAccount.objects.get(id=1) 
    fetcher = EmailFetcher(email_account)  

    try:
        fetcher.login()  
        emails = fetcher.fetch_messages()  
        return render(request, "emails/list.html", {"emails": emails}) 
    except Exception as e:
        return render(request, "emails/list.html", {"emails": [], "error": str(e)})  


def email_list_view(request):
    emails = EmailMessage.objects.all()
    return render(request, 'emails/list.html', {'emails': emails})


@require_POST
def start_email_import(request, account_id):
    try:
        data = json.loads(request.body)
        email = data.get('email')  
        password = data.get('password')  
        
        account = EmailAccount.objects.get(id=account_id)
        
        fetcher = EmailFetcher(email, password)  
        
        if fetcher.login():  
            fetcher.fetch_messages()  
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Login failed"})
    except EmailAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Account not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
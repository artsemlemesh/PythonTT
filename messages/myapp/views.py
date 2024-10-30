from django.shortcuts import render
from django.http import JsonResponse
from .models import EmailMessage, EmailAccount
from .services import EmailFetcher
from django.views.decorators.http import require_POST
import json

def fetch_emails_view(request):
    email_account = EmailAccount.objects.get(id=1)  # Replace with dynamic selection
    fetcher = EmailFetcher(email_account)  # Use EmailFetcher directly

    # Attempt to fetch emails
    try:
        fetcher.login()  # Log in using EmailFetcher
        emails = fetcher.fetch_messages()  # Fetch real emails
        return render(request, "emails/list.html", {"emails": emails})  # Pass fetched emails to the template
    except Exception as e:
        return render(request, "emails/list.html", {"emails": [], "error": str(e)})  # Handle errors


def email_list_view(request):
    """
    Display the list of emails with a progress bar.
    """
    emails = EmailMessage.objects.all()
    return render(request, 'emails/list.html', {'emails': emails})


@require_POST
def start_email_import(request, account_id):
    """
    Initiates the email fetch process for the specified account.
    """
    try:
        # Get the email and password from the request body
        data = json.loads(request.body)
        email = data.get('email')  # Get email from request
        password = data.get('password')  # Get password from request
        
        # Initialize EmailAccount or directly use email (if you want dynamic fetching)
        account = EmailAccount.objects.get(id=account_id)
        
        # Create an EmailFetcher instance with the provided credentials
        fetcher = EmailFetcher(email, password)  # Update this line to pass email and password
        
        if fetcher.login():  # Attempt to log in with the provided credentials
            # Start fetching emails in the background or via WebSocket
            fetcher.fetch_messages()  # Call the fetching directly
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Login failed"})
    except EmailAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Account not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
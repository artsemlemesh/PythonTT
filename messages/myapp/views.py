from django.shortcuts import render
from django.http import JsonResponse
from .models import EmailMessage, EmailAccount
from .services import EmailFetcher
from .email_client import EmailClient
from django.views.decorators.http import require_POST



def fetch_emails_view(request):
    email_account = EmailAccount.objects.get(id=1)  # Replace with dynamic selection
    client = EmailClient(
        email_service=email_account.provider,
        username=email_account.username,
        password=email_account.password,
    )

    if client.connect():
        emails = client.fetch_emails()  # Fetch real emails
        client.logout()  # Logout after fetching
        return render(request, "emails/list.html", {"emails": emails})  # Pass fetched emails to the template
    else:
        return render(request, "emails/list.html", {"emails": [], "error": "Failed to connect to email server."})


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
        print('before account')
        account = EmailAccount.objects.get(id=account_id)
        print('after account', account)
        fetcher = EmailFetcher(account)
        print('after fetcher', fetcher)
        print("Starting email fetch...")
        if fetcher.login():
            # Start fetching emails in the background or via WebSocket
            fetcher.fetch_messages()  # Call the fetching directly
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Login failed"})
    except EmailAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Account not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
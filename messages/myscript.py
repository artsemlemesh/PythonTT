import imaplib

EMAIL = 'bublikteam1@gmail.com'
PASSWORD = 'bzdy wyke ygzy uygm'  # Use an app password if 2FA is enabled

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL, PASSWORD)
    print("Login successful!")
    mail.logout()
except imaplib.IMAP4.error as e:
    print(f"Login failed! Error: {e}")
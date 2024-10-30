# Project Setup

Before you begin, ensure you have met the following requirements:
- IMAP access enabled in your email account.
- Redis server running for handling WebSocket connections.
- Django and required packages installed.


### Email Configuration

When configuring the email settings, please ensure you enter:

- **Email**: Your full email address.
- **App Password**: Use an app-specific password for authentication (not your regular email password). Make sure IMAP is enabled in your email settings.

### Limitations

For convenience, the application has the following limitations:

	•	A maximum of 10 messages will be fetched at a time.
	•	The body of each email will be displayed with a maximum length of 30 symbols.
   •	Attachments are shown by their names and extensions. If necessary, additional file types can be included upon request.


## Installation Steps

1. **Clone the Repository**: 
   Clone your project repository to your local machine.
   
   ```bash
   git clone <your-repository-url>
   cd <your-project-directory>
   ```

2. **Install Dependencies**:
   Install required packages listed in `requirements.txt`:
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Redis Setup**:
   Ensure Redis is installed and running. You can start Redis with:

   ```bash
   redis-server
   ```

4. **Database Setup**:
   Run migrations to set up the database schema:
   
   ```bash
   python manage.py migrate
   ```

5. **Collect Static Files**:
   If your project uses static files, run:

   ```bash
   python manage.py collectstatic
   ```

## Running the Project

To launch your Django app with WebSocket functionality:

1. **Start Redis** (if not already running):

   ```bash
   redis-server
   ```

2. **Start the Daphne Server**:

   ```bash
   daphne -p 8000 messages.asgi:application
   ```

3. **Managing the Server**:
   - If the app becomes unresponsive on port 8000, check for processes using this port:
   
     ```bash
     lsof -i :8000
     ```

   - Then, terminate the process with the following command (replace `[PID]` with the specific process ID):

     ```bash
     kill -9 [PID]
     ```


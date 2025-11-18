# User Feedback App

## Overview
The User Feedback app allows users to submit feedback which is automatically sent to a designated admin email address. All feedback is stored in the database and can be viewed through the Django admin panel.

## Features
- ✅ Public feedback submission (no authentication required)
- ✅ Automatic email notification to admin
- ✅ Database storage of all feedback
- ✅ Admin panel for viewing and managing feedback
- ✅ Mark feedback as read/unread
- ✅ Input validation
- ✅ RESTful API endpoint

## Model Fields

### UserFeedback
- `title` - CharField (max 200 characters) - Feedback title/subject
- `email` - EmailField - User's email address
- `content` - TextField - Feedback message content
- `created_at` - DateTimeField - Timestamp when feedback was submitted
- `is_read` - BooleanField - Status flag for tracking if admin has read the feedback

## API Endpoint

### Submit Feedback
**Endpoint:** `POST /api/user-feedback/submit/`  
**Authentication:** Not required (Public)  
**Description:** Submit new feedback

**Request Body:**
```json
{
    "title": "Feedback title",
    "email": "user@example.com",
    "content": "Detailed feedback message"
}
```

**Response (201 Created):**
```json
{
    "message": "Feedback submitted successfully",
    "email_status": "Email sent successfully",
    "feedback": {
        "id": 1,
        "title": "Feedback title",
        "email": "user@example.com",
        "content": "Detailed feedback message",
        "created_at": "2025-11-13T10:30:00Z",
        "is_read": false
    }
}
```

**Validation Errors (400 Bad Request):**
```json
{
    "error": "Invalid feedback data",
    "details": {
        "title": ["Title must be at least 3 characters long."],
        "content": ["Content must be at least 10 characters long."]
    }
}
```

## Configuration

### Email Settings
Add the following to your `.env` file:

```env
# Email Configuration (Already in your project)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

# Feedback admin email (Optional - defaults to EMAIL_HOST_USER)
FEEDBACK_ADMIN_EMAIL=admin@yourdomain.com
```

### Gmail Setup
If using Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password as `EMAIL_HOST_PASSWORD`

## Admin Panel

Access the admin panel at `/admin/` to:
- View all submitted feedback
- Search feedback by title, email, or content
- Filter by read/unread status
- Mark feedback as read/unread
- View submission timestamps

## Validation Rules
- **Title:** Minimum 3 characters
- **Email:** Must be a valid email format
- **Content:** Minimum 10 characters

## Usage Examples

### Using cURL
```bash
curl -X POST http://localhost:8000/api/user-feedback/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Great App!",
    "email": "user@example.com",
    "content": "I really love using this application. Keep up the good work!"
  }'
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/api/user-feedback/submit/"
data = {
    "title": "Feature Request",
    "email": "user@example.com",
    "content": "Would be great to have dark mode!"
}

response = requests.post(url, json=data)
print(response.json())
```

### Using JavaScript/Fetch
```javascript
fetch('http://localhost:8000/api/user-feedback/submit/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Bug Report',
    email: 'user@example.com',
    content: 'Found a bug in the payment section.'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Security Notes
- The submission endpoint is publicly accessible (no authentication required)
- Email validation prevents invalid submissions
- Content validation prevents spam/empty submissions
- All feedback is logged to database even if email fails
- Admin panel requires authentication

## Troubleshooting

### Email Not Sending
1. Check your `.env` file has correct email credentials
2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
3. For Gmail, ensure App Password is being used
4. Check email logs in console for error messages

### Admin Panel Not Showing Feedback
1. Run migrations: `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Ensure 'user_feedback' is in INSTALLED_APPS

## Database Migration
```bash
python manage.py makemigrations user_feedback
python manage.py migrate
```

## Email Notification
When a user submits feedback, an email is automatically sent to the admin containing:
- Feedback title
- User's email address
- Feedback content
- Submission timestamp
- Feedback ID for database reference

The admin can then log into the admin panel to view, manage, and mark feedback as read.

## Integration
The feedback system is ready to use and can be integrated with any frontend (Flutter, React, etc.) by making POST requests to the submit endpoint.

---

**Feedback system is now active! 🎉**


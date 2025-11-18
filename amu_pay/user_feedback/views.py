from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .models import UserFeedback
from .serializers import UserFeedbackSerializer
import logging

logger = logging.getLogger(__name__)


class SubmitFeedbackView(APIView):
    """
    API endpoint to submit user feedback.
    No authentication required - public endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Submit user feedback"""
        serializer = UserFeedbackSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save feedback to database
            feedback = serializer.save()
            
            # Send email notification to admin
            try:
                self.send_feedback_email(feedback)
                email_status = "Email sent successfully"
            except Exception as e:
                logger.error(f"Error sending feedback email: {str(e)}")
                email_status = "Email sending failed (feedback saved)"
            
            return Response({
                'message': 'Feedback submitted successfully',
                'email_status': email_status,
                'feedback': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Invalid feedback data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def send_feedback_email(self, feedback):
        """Send feedback notification email to admin"""
        # Get admin email from settings
        admin_email = getattr(settings, 'FEEDBACK_ADMIN_EMAIL', None)
        
        if not admin_email:
            # Fallback to EMAIL_HOST_USER if FEEDBACK_ADMIN_EMAIL not set
            admin_email = settings.EMAIL_HOST_USER
        
        # Prepare email content
        subject = f"New User Feedback: {feedback.title}"
        message = f"""
You have received new user feedback:

Title: {feedback.title}
From: {feedback.email}
Submitted at: {feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Message:
{feedback.content}

---
This feedback has been saved to the database with ID: {feedback.id}
You can view all feedback in the admin panel.
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[admin_email],
            fail_silently=False,
        )

from django.db import models

class UserFeedback(models.Model):
    """Model for user feedback submissions"""
    title = models.CharField(max_length=200, help_text="Feedback title/subject")
    email = models.EmailField(help_text="User's email address")
    content = models.TextField(help_text="Feedback content/message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text="Has admin read this feedback?")
    
    class Meta:
        verbose_name = 'User Feedback'
        verbose_name_plural = 'User Feedbacks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.email}"

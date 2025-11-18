from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import os


def upload_to(instance, filename):
    """Generate upload path for post photos"""
    return f'posts/{instance.saraf_account.saraf_id}/{filename}'


class SarafPost(models.Model):
    """
    Model for exchange house posts
    """
    # Basic post information
    title = models.CharField(
        max_length=200,
        help_text="Post title"
    )
    content = models.TextField(
        help_text="Post content"
    )
    photo = models.ImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        help_text="Post photo"
    )
    
    # Saraf information
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Exchange house that created the post"
    )
    
    # User information (who created the post)
    created_by_saraf = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_posts',
        help_text="Exchange house who created the post"
    )
    created_by_employee = models.ForeignKey(
        'saraf_account.SarafEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_posts',
        help_text="Employee who created the post"
    )
    
    # Post status
    # Removed is_published and is_featured fields as requested
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the post was published"
    )
    
    class Meta:
        verbose_name = 'Exchange House Post'
        verbose_name_plural = 'Exchange House Posts'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['saraf_account']),
            models.Index(fields=['published_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['title']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.saraf_account.full_name}"
    
    def clean(self):
        """Model validation"""
        # Validate title
        if not self.title or len(self.title.strip()) == 0:
            raise ValidationError("Title cannot be empty")
        
        if len(self.title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")
        
        # Validate content
        if not self.content or len(self.content.strip()) == 0:
            raise ValidationError("Content cannot be empty")
        
        # Validate photo file size (max 10MB)
        if self.photo:
            if self.photo.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("Photo size cannot exceed 10MB")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_created_by_info(self):
        """Get information about who created the post"""
        if self.created_by_employee:
            return {
                'type': 'employee',
                'id': self.created_by_employee.employee_id,
                'name': self.created_by_employee.full_name
            }
        elif self.created_by_saraf:
            return {
                'type': 'saraf',
                'id': self.created_by_saraf.saraf_id,
                'name': self.created_by_saraf.full_name
            }
        return None
    
    def get_photo_url(self):
        """Get the photo URL"""
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return None
    
    def get_photo_name(self):
        """Get the photo filename"""
        if self.photo:
            return os.path.basename(self.photo.name)
        return None
    
    @property
    def word_count(self):
        """Get word count of the content"""
        if self.content:
            return len(self.content.split())
        return 0
    
    @property
    def character_count(self):
        """Get character count of the content"""
        return len(self.content) if self.content else 0
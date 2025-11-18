from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
import uuid

class SarafLike(models.Model):
    """Model for tracking likes from normal users to Saraf accounts"""
    
    like_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount', 
        on_delete=models.CASCADE, 
        related_name='likes_received'
    )
    normal_user = models.ForeignKey(
        'normal_user_account.NormalUser', 
        on_delete=models.CASCADE, 
        related_name='likes_given'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Saraf Like'
        verbose_name_plural = 'Saraf Likes'
        unique_together = ['saraf_account', 'normal_user']  # One like per user per Saraf
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['saraf_account', 'created_at']),
            models.Index(fields=['normal_user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.normal_user.full_name} likes {self.saraf_account.full_name}"

class SarafComment(models.Model):
    """Model for comments from normal users to Saraf accounts"""
    
    comment_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount', 
        on_delete=models.CASCADE, 
        related_name='comments_received'
    )
    normal_user = models.ForeignKey(
        'normal_user_account.NormalUser', 
        on_delete=models.CASCADE, 
        related_name='comments_given'
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(10, message="Comment must be at least 10 characters long"),
            MaxLengthValidator(500, message="Comment cannot exceed 500 characters")
        ],
        help_text="Comment content (10-500 characters)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Saraf Comment'
        verbose_name_plural = 'Saraf Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['saraf_account', 'created_at']),
            models.Index(fields=['normal_user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.normal_user.full_name} commented on {self.saraf_account.full_name}"

class SarafSocialStats(models.Model):
    """Model for caching Saraf social statistics"""
    
    stats_id = models.BigAutoField(primary_key=True)
    saraf_account = models.OneToOneField(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='social_stats'
    )
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Saraf Social Stats'
        verbose_name_plural = 'Saraf Social Stats'
    
    def __str__(self):
        return f"Stats for {self.saraf_account.full_name}: {self.total_likes} likes, {self.total_comments} comments"
    
    def update_stats(self):
        """Update statistics from actual data"""
        self.total_likes = self.saraf_account.likes_received.count()
        self.total_comments = self.saraf_account.comments_received.count()
        self.save()
    
    @classmethod
    def get_or_create_stats(cls, saraf_account):
        """Get or create stats for a Saraf account"""
        stats, created = cls.objects.get_or_create(saraf_account=saraf_account)
        if not created:
            stats.update_stats()
        return stats
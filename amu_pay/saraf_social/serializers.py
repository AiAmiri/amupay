from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SarafLike, SarafComment, SarafSocialStats
from saraf_account.models import SarafAccount
from normal_user_account.models import NormalUser

class SarafLikeSerializer(serializers.ModelSerializer):
    """Serializer for SarafLike model"""
    
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    user_name = serializers.CharField(source='normal_user.full_name', read_only=True)
    user_email = serializers.CharField(source='normal_user.email', read_only=True)
    
    class Meta:
        model = SarafLike
        fields = [
            'like_id', 
            'saraf_account', 
            'saraf_name',
            'normal_user', 
            'user_name',
            'user_email',
            'created_at'
        ]
        read_only_fields = ['like_id', 'created_at']

class SarafCommentSerializer(serializers.ModelSerializer):
    """Serializer for SarafComment model"""
    
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    user_name = serializers.CharField(source='normal_user.full_name', read_only=True)
    user_email = serializers.CharField(source='normal_user.email', read_only=True)
    
    class Meta:
        model = SarafComment
        fields = [
            'comment_id',
            'saraf_account',
            'saraf_name',
            'normal_user',
            'user_name',
            'user_email',
            'content',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'comment_id', 
            'created_at', 
            'updated_at'
        ]

class CreateSarafCommentSerializer(serializers.ModelSerializer):
    """Serializer for creating new Saraf comments"""
    
    saraf_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = SarafComment
        fields = ['saraf_id', 'content']
    
    def validate_content(self, value):
        """Validate comment content"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long")
        if len(value) > 500:
            raise serializers.ValidationError("Comment cannot exceed 500 characters")
        return value.strip()
    
    def validate_saraf_id(self, value):
        """Validate Saraf ID exists and is active"""
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=value, is_active=True)
            return value
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Saraf account not found or inactive")
    
    def create(self, validated_data):
        """Create comment with saraf_id instead of saraf_account"""
        saraf_id = validated_data.pop('saraf_id')
        saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
        validated_data['saraf_account'] = saraf_account
        return super().create(validated_data)

class SarafSocialStatsSerializer(serializers.ModelSerializer):
    """Serializer for Saraf social statistics"""
    
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    saraf_id = serializers.CharField(source='saraf_account.saraf_id', read_only=True)
    
    class Meta:
        model = SarafSocialStats
        fields = [
            'stats_id',
            'saraf_account',
            'saraf_id',
            'saraf_name',
            'total_likes',
            'total_comments',
            'last_updated'
        ]

class PublicSarafStatsSerializer(serializers.ModelSerializer):
    """Public serializer for Saraf statistics (limited fields)"""
    
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    saraf_id = serializers.CharField(source='saraf_account.saraf_id', read_only=True)
    
    class Meta:
        model = SarafSocialStats
        fields = [
            'saraf_id',
            'saraf_name',
            'total_likes',
            'total_comments'
        ]

class SarafCommentListSerializer(serializers.ModelSerializer):
    """Serializer for listing Saraf comments (public view)"""
    
    user_name = serializers.CharField(source='normal_user.full_name', read_only=True)
    
    class Meta:
        model = SarafComment
        fields = [
            'comment_id',
            'user_name',
            'content',
            'created_at'
        ]

class LikeToggleSerializer(serializers.Serializer):
    """Serializer for like operation (unlike removed)"""
    
    saraf_id = serializers.CharField()
    
    def validate_saraf_id(self, value):
        """Validate Saraf ID exists and is active"""
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=value, is_active=True)
            return value
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Saraf account not found or inactive")

class CommentDeleteSerializer(serializers.Serializer):
    """Serializer for comment deletion by normal users"""
    
    comment_id = serializers.IntegerField()
    
    def validate_comment_id(self, value):
        """Validate comment exists and belongs to user"""
        try:
            comment = SarafComment.objects.get(comment_id=value)
            return value
        except SarafComment.DoesNotExist:
            raise serializers.ValidationError("Comment not found")

from rest_framework import serializers
from .models import SarafPost


class SarafPostSerializer(serializers.ModelSerializer):
    """
    Serializer for SarafPost model
    """
    created_by_info = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    photo_name = serializers.SerializerMethodField()
    word_count = serializers.ReadOnlyField()
    character_count = serializers.ReadOnlyField()
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    
    class Meta:
        model = SarafPost
        fields = [
            'id',
            'title',
            'content',
            'photo',
            'photo_url',
            'photo_name',
            'saraf_account',
            'saraf_name',
            'created_by_info',
            'created_at',
            'updated_at',
            'published_at',
            'word_count',
            'character_count'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'created_by_info', 
            'photo_url', 
            'photo_name',
            'word_count',
            'character_count'
        ]
    
    def get_created_by_info(self, obj):
        """Get information about who created the post"""
        return obj.get_created_by_info()
    
    def get_photo_url(self, obj):
        """Get the photo URL"""
        return obj.get_photo_url()
    
    def get_photo_name(self, obj):
        """Get the photo filename"""
        return obj.get_photo_name()
    
    def validate_title(self, value):
        """Validate title"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty")
        
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters")
        
        return value.strip()
    
    def validate_content(self, value):
        """Validate content"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        
        return value.strip()


class SarafPostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating SarafPost
    """
    class Meta:
        model = SarafPost
        fields = [
            'title',
            'content',
            'photo',
            'published_at'
        ]
    
    def validate_title(self, value):
        """Validate title"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty")
        
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters")
        
        return value.strip()
    
    def validate_content(self, value):
        """Validate content"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        
        return value.strip()
    
    def validate_photo(self, value):
        """Validate photo"""
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Photo size cannot exceed 10MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only JPEG, PNG, GIF, and WebP images are allowed")
        
        return value


class SarafPostListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing SarafPosts
    """
    created_by_name = serializers.SerializerMethodField()
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    photo_url = serializers.SerializerMethodField()
    word_count = serializers.ReadOnlyField()
    
    class Meta:
        model = SarafPost
        fields = [
            'id',
            'title',
            'content',
            'photo_url',
            'saraf_name',
            'created_by_name',
            'created_at',
            'published_at',
            'word_count'
        ]
    
    def get_created_by_name(self, obj):
        """Get name of who created the post"""
        created_by_info = obj.get_created_by_info()
        if created_by_info:
            return created_by_info['name']
        return None
    
    def get_photo_url(self, obj):
        """Get the photo URL"""
        return obj.get_photo_url()


class SarafPostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating SarafPost
    """
    class Meta:
        model = SarafPost
        fields = [
            'title',
            'content',
            'photo',
            'published_at'
        ]
    
    def validate_title(self, value):
        """Validate title"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Title cannot be empty")
        
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters")
        
        return value.strip()
    
    def validate_content(self, value):
        """Validate content"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        
        return value.strip()
    
    def validate_photo(self, value):
        """Validate photo"""
        if value:
            # Check file size (max 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Photo size cannot exceed 10MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only JPEG, PNG, GIF, and WebP images are allowed")
        
        return value


class SarafPostDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for SarafPost
    """
    created_by_info = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    photo_name = serializers.SerializerMethodField()
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    word_count = serializers.ReadOnlyField()
    character_count = serializers.ReadOnlyField()
    
    class Meta:
        model = SarafPost
        fields = [
            'id',
            'title',
            'content',
            'photo',
            'photo_url',
            'photo_name',
            'saraf_account',
            'saraf_name',
            'created_by_info',
            'created_at',
            'updated_at',
            'published_at',
            'word_count',
            'character_count'
        ]
    
    def get_created_by_info(self, obj):
        """Get information about who created the post"""
        return obj.get_created_by_info()
    
    def get_photo_url(self, obj):
        """Get the photo URL"""
        return obj.get_photo_url()
    
    def get_photo_name(self, obj):
        """Get the photo filename"""
        return obj.get_photo_name()

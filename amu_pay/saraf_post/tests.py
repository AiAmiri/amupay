from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import SarafPost
from saraf_account.models import SarafAccount, SarafEmployee


class SarafPostModelTest(TestCase):
    """Test cases for SarafPost model"""
    
    def setUp(self):
        """Set up test data"""
        self.saraf_account = SarafAccount.objects.create(
            saraf_id=1,
            full_name="Test Saraf",
            email_or_whatsapp_number="test@example.com",
            exchange_name="Test Exchange",
            amu_pay_code="TEST001",
            province="Kabul"
        )
        
        self.employee = SarafEmployee.objects.create(
            saraf_account=self.saraf_account,
            username="test_employee",
            full_name="Test Employee"
        )
    
    def test_saraf_post_creation(self):
        """Test creating a saraf post"""
        post = SarafPost.objects.create(
            title="Test Post Title",
            content="This is a test post content",
            saraf_account=self.saraf_account,
            created_by_employee=self.employee
        )
        
        self.assertEqual(post.title, "Test Post Title")
        self.assertEqual(post.content, "This is a test post content")
        self.assertEqual(post.saraf_account, self.saraf_account)
        self.assertEqual(post.created_by_employee, self.employee)
    
    def test_title_validation(self):
        """Test title validation"""
        with self.assertRaises(Exception):
            SarafPost.objects.create(
                title="",  # Empty title
                content="This is a test post content",
                saraf_account=self.saraf_account
            )
    
    def test_content_validation(self):
        """Test content validation"""
        with self.assertRaises(Exception):
            SarafPost.objects.create(
                title="Test Post Title",
                content="",  # Empty content
                saraf_account=self.saraf_account
            )
    
    def test_get_created_by_info(self):
        """Test getting created by information"""
        post = SarafPost.objects.create(
            title="Test Post Title",
            content="This is a test post content",
            saraf_account=self.saraf_account,
            created_by_employee=self.employee
        )
        
        created_by_info = post.get_created_by_info()
        self.assertEqual(created_by_info['type'], 'employee')
        self.assertEqual(created_by_info['id'], self.employee.employee_id)
        self.assertEqual(created_by_info['name'], 'Test Employee')
    
    def test_word_count(self):
        """Test word count property"""
        post = SarafPost.objects.create(
            title="Test Post Title",
            content="This is a test post content with multiple words",
            saraf_account=self.saraf_account
        )
        
        self.assertEqual(post.word_count, 9)  # 9 words in content
    
    def test_character_count(self):
        """Test character count property"""
        content = "This is a test post content"
        post = SarafPost.objects.create(
            title="Test Post Title",
            content=content,
            saraf_account=self.saraf_account
        )
        
        self.assertEqual(post.character_count, len(content))
    
    def test_photo_upload(self):
        """Test photo upload functionality"""
        # Create a simple image file for testing
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        image_file = SimpleUploadedFile(
            "test_image.png",
            image_content,
            content_type="image/png"
        )
        
        post = SarafPost.objects.create(
            title="Test Post with Photo",
            content="This is a test post with photo",
            photo=image_file,
            saraf_account=self.saraf_account
        )
        
        self.assertTrue(post.photo)
        self.assertTrue("test_image" in post.get_photo_name())
    
    def test_str_representation(self):
        """Test string representation of the model"""
        post = SarafPost.objects.create(
            title="Test Post Title",
            content="This is a test post content",
            saraf_account=self.saraf_account
        )
        
        expected_str = f"Test Post Title - {self.saraf_account.full_name}"
        self.assertEqual(str(post), expected_str)


class SarafPostViewTest(TestCase):
    """Test cases for SarafPost views"""
    
    def setUp(self):
        """Set up test data"""
        self.saraf_account = SarafAccount.objects.create(
            saraf_id=1,
            full_name="Test Saraf",
            email_or_whatsapp_number="test@example.com",
            exchange_name="Test Exchange",
            amu_pay_code="TEST001",
            province="Kabul"
        )
        
        self.employee = SarafEmployee.objects.create(
            saraf_account=self.saraf_account,
            username="test_employee",
            full_name="Test Employee"
        )
    
    def test_saraf_post_list_view(self):
        """Test saraf post list view"""
        from .views import SarafPostListView
        self.assertTrue(SarafPostListView)
    
    def test_saraf_post_create_view(self):
        """Test saraf post create view"""
        from .views import SarafPostCreateView
        self.assertTrue(SarafPostCreateView)
    
    def test_saraf_post_detail_view(self):
        """Test saraf post detail view"""
        from .views import SarafPostDetailView
        self.assertTrue(SarafPostDetailView)


class SarafPostSerializerTest(TestCase):
    """Test cases for SarafPost serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.saraf_account = SarafAccount.objects.create(
            saraf_id=1,
            full_name="Test Saraf",
            email_or_whatsapp_number="test@example.com",
            exchange_name="Test Exchange",
            amu_pay_code="TEST001",
            province="Kabul"
        )
        
        self.employee = SarafEmployee.objects.create(
            saraf_account=self.saraf_account,
            username="test_employee",
            full_name="Test Employee"
        )
    
    def test_saraf_post_create_serializer(self):
        """Test SarafPostCreateSerializer"""
        from .serializers import SarafPostCreateSerializer
        
        data = {
            'title': 'Test Post Title',
            'content': 'This is a test post content'
        }
        
        serializer = SarafPostCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_saraf_post_create_serializer_validation(self):
        """Test SarafPostCreateSerializer validation"""
        from .serializers import SarafPostCreateSerializer
        
        # Test empty title
        data = {
            'title': '',
            'content': 'This is a test post content',
        }
        
        serializer = SarafPostCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
    
    def test_saraf_post_list_serializer(self):
        """Test SarafPostListSerializer"""
        from .serializers import SarafPostListSerializer
        
        post = SarafPost.objects.create(
            title="Test Post Title",
            content="This is a test post content",
            saraf_account=self.saraf_account,
            created_by_employee=self.employee
        )
        
        serializer = SarafPostListSerializer(post)
        self.assertEqual(serializer.data['title'], "Test Post Title")
        self.assertEqual(serializer.data['saraf_name'], "Test Saraf")
        self.assertEqual(serializer.data['created_by_name'], "Test Employee")
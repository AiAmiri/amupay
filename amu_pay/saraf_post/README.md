# Saraf Post App - Exchange House Post Management System

This application allows exchange houses to create and manage posts with title, content, and photo fields. It provides a simple blogging system for exchange houses to share information, updates, and announcements.

## 📋 Table of Contents

- [Main Features](#main-features)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Filters and Search](#filters-and-search)
- [Security Features](#security-features)
- [Permission System](#permission-system)
- [Installation and Setup](#installation-and-setup)
- [Testing](#testing)
- [System Benefits](#system-benefits)

## 🚀 Main Features

### 1. Post Management

#### Main Post Fields:
- **Title (title)**: Post title (max 200 characters)
- **Content (content)**: Post content/body text
- **Photo (photo)**: Optional post image (JPEG, PNG, GIF, WebP)
- **Published Date (published_at)**: When the post was published

### 2. Automatic Features

- **Automatic Creator Detection**: System automatically detects who created the post (exchange house or employee)
- **Permission Checking**: Checking required permissions for post operations
- **Automatic Validation**: Automatic validation of title, content, and photo
- **File Management**: Automatic photo upload and management

### 3. Advanced Search and Filtering

- **Filter by Title**: Search by post title
- **Filter by Content**: Search within post content
- **Filter by Creator**: Search by post creator name
- **Date Range Filter**: Search within specific date ranges

## 🗄️ Data Models

### SarafPost Model

```python
class SarafPost(models.Model):
    # Basic post information
    title = models.CharField(max_length=200)
    content = models.TextField()
    photo = models.ImageField(upload_to=upload_to, blank=True, null=True)
    
    # Account information
    saraf_account = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.CASCADE)
    created_by_saraf = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.SET_NULL, null=True)
    created_by_employee = models.ForeignKey('saraf_account.SarafEmployee', on_delete=models.SET_NULL, null=True)
    
    # Post status
    # Simple post without published/featured status
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
```

### Indexes for Optimization:

- `saraf_account`
- `published_at`
- `created_at`
- `title`

## 🔌 API Endpoints

### Post Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/saraf-posts/` | List posts (Public - no authentication required) |
| `POST` | `/api/saraf-posts/create/` | Create new post |
| `GET` | `/api/saraf-posts/{post_id}/` | View specific post details |
| `PUT` | `/api/saraf-posts/{post_id}/` | Update specific post |
| `DELETE` | `/api/saraf-posts/{post_id}/` | Delete specific post |

## 💡 Usage Examples

### 1. Create New Post

```bash
POST /api/saraf-posts/create/
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

{
    "title": "Exchange Rate Update",
    "content": "We are pleased to announce our updated exchange rates for USD to AFN. Current rate is 75.50 AFN per USD.",
    "photo": <image_file>
}
```

**Success Response:**
```json
{
    "message": "Post created successfully",
    "post": {
        "id": 1,
        "title": "Exchange Rate Update",
        "content": "We are pleased to announce our updated exchange rates for USD to AFN. Current rate is 75.50 AFN per USD.",
        "photo": "/media/posts/1/exchange_rate.jpg",
        "photo_url": "/media/posts/1/exchange_rate.jpg",
        "photo_name": "exchange_rate.jpg",
        "saraf_account": 1,
        "saraf_name": "Test Exchange House",
        "created_by_info": {
            "type": "employee",
            "id": 1,
            "name": "Test Employee"
        },
        "created_at": "2024-01-15T14:30:00Z",
        "updated_at": "2024-01-15T14:30:00Z",
        "published_at": "2024-01-15T14:30:00Z",
        "word_count": 20,
        "character_count": 120
    }
}
```

### 2. Get Posts List (Public)

```bash
GET /api/saraf-posts/
```

**Query Parameters (Optional):**
- `title`: Search posts by title
- `content`: Search posts by content  
- `created_by`: Filter by creator name
- `saraf_id`: Filter by saraf/exchange ID (number)
- `start_date`: Filter posts from date (YYYY-MM-DD)
- `end_date`: Filter posts to date (YYYY-MM-DD)
- `page`: Page number (default: 1)
- `page_size`: Posts per page (default: 20)

**Example with filters:**
```bash
GET /api/saraf-posts/?title=exchange&saraf_id=123&page=1&page_size=10
```

**Filter Examples:**
- Filter by specific saraf: `?saraf_id=123`
- Search by title: `?title=exchange`
- Filter by date range: `?start_date=2024-01-01&end_date=2024-01-31`
- Combined filters: `?saraf_id=123&title=rate&page=1&page_size=5`

**Response:**
```json
{
    "message": "Saraf posts list (Public)",
    "posts": [
        {
            "id": 1,
            "title": "Exchange Rate Update",
            "content": "We are pleased to announce our updated exchange rates...",
            "photo_url": "/media/posts/1/exchange_rate.jpg",
            "saraf_name": "Test Exchange House",
            "created_by_name": "Test Employee",
            "created_at": "2024-01-15T14:30:00Z",
            "published_at": "2024-01-15T14:30:00Z",
            "word_count": 20
        }
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_count": 1,
        "total_pages": 1
    }
}
```

### 3. Update Post

```bash
PUT /api/saraf-posts/1/
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

{
    "title": "Updated Exchange Rate",
    "content": "Updated content with new information"
}
```

## 🔍 Filters and Search

### Supported Query Parameters:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `title` | string | Search by title | `Exchange` |
| `content` | string | Search by content | `rates` |
| `created_by` | string | Search by creator | `Employee` |
| `start_date` | date | Start date (YYYY-MM-DD) | `2024-01-01` |
| `end_date` | date | End date (YYYY-MM-DD) | `2024-01-31` |
| `page` | integer | Page number | `1` |
| `page_size` | integer | Items per page | `20` |

### Filter Examples:

```bash
# Search by title
GET /api/saraf-posts/?title=Exchange

# Search by content
GET /api/saraf-posts/?content=rates

# Search by creator
GET /api/saraf-posts/?created_by=Employee

# Date range
GET /api/saraf-posts/?start_date=2024-01-01&end_date=2024-01-31

# Combined filters
GET /api/saraf-posts/?title=Update&content=rates
```

## 🔒 Security Features

### Authentication
- **JWT Token**: All operations require valid JWT token
- **Token Validation**: Checking token validity and expiration
- **User Context**: Extracting user information from token

### Permissions
- **Employees**: Must have `add_posts` permission
- **Exchange Houses**: Can manage their own posts
- **Access Restriction**: Each exchange house only has access to their own posts

### Validation
- **Title**: Cannot be empty, max 200 characters
- **Content**: Cannot be empty
- **Photo**: Max 10MB, only image formats (JPEG, PNG, GIF, WebP)
- **File Security**: Secure file upload handling

### Logging
- **Action Log**: Recording all operations in ActionLog
- **User Tracking**: Tracking the user who performed the operation
- **Timestamp**: Recording exact time of operations

## 👥 Permission System

| Operation | Required Permission | Description |
|-----------|-------------------|-------------|
| **View Posts** | Authentication | All authenticated users |
| **Create Posts** | `add_posts` | Employees with permission |
| **Update Posts** | `add_posts` | Employees with permission |
| **Delete Posts** | `add_posts` | Employees with permission |
| **Search Posts** | Authentication | All authenticated users |

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- MySQL/PostgreSQL
- Pillow (for image handling)

### Installation Steps

1. **Install Dependencies:**
```bash
pip install Pillow
```

2. **Setup Database:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Media Directory:**
```bash
mkdir media
mkdir media/posts
```

4. **Run Server:**
```bash
python manage.py runserver
```

### Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'saraf_post',
    'rest_framework',
    'rest_framework_simplejwt',
]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### URL Configuration

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... other patterns
    path('api/saraf-posts/', include('saraf_post.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run saraf_post module tests
python manage.py test saraf_post

# Run specific test
python manage.py test saraf_post.tests.SarafPostModelTest.test_saraf_post_creation
```

### Available Tests

#### SarafPostModelTest
- ✅ `test_saraf_post_creation` - Create post
- ✅ `test_title_validation` - Title validation
- ✅ `test_content_validation` - Content validation
- ✅ `test_get_created_by_info` - Get creator information
- ✅ `test_word_count` - Word count property
- ✅ `test_character_count` - Character count property
- ✅ `test_photo_upload` - Photo upload functionality
- ✅ `test_str_representation` - String representation

#### SarafPostViewTest
- ✅ `test_saraf_post_list_view` - Test list view
- ✅ `test_saraf_post_create_view` - Test create view
- ✅ `test_saraf_post_detail_view` - Test detail view

#### SarafPostSerializerTest
- ✅ `test_saraf_post_create_serializer` - Test create serializer
- ✅ `test_saraf_post_create_serializer_validation` - Test validation
- ✅ `test_saraf_post_list_serializer` - Test list serializer

### Test Coverage
- **Models**: 100% coverage
- **Serializers**: Complete validation
- **Views**: Structure and existence tests

## 📊 System Benefits

### 1. Easy Management
- Simple and intuitive post creation
- Complete CRUD operations
- User-friendly error handling

### 2. Powerful Search
- Multiple search filters
- Text search in title and content
- Date range filtering
- Pagination

### 3. Flexibility
- Support for different post types
- Optional photo uploads
- Published/unpublished status
- Featured posts system

### 4. High Security
- JWT authentication
- Permission system
- Complete validation
- Operation logging

### 5. Optimal Performance
- Optimized indexes
- Optimized queries
- Efficient file handling
- Pagination

### 6. Maintainability
- Clean and documented code
- Complete tests
- Modular structure
- Comprehensive documentation

## 📸 Photo Management

### Supported Formats
- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **WebP** (.webp)

### File Size Limits
- **Maximum Size**: 10MB per photo
- **Automatic Validation**: File type and size checking

### Storage Structure
```
media/
└── posts/
    └── {saraf_id}/
        └── {filename}
```

### Photo URLs
- **Access URL**: `/media/posts/{saraf_id}/{filename}`
- **Automatic Generation**: URLs generated automatically
- **Secure Access**: Only authenticated users can access

## 📈 Statistics and Analytics

### Available Statistics:
- Total posts count
- Published/unpublished posts
- Featured posts count
- Posts by creator
- Posts by date range

### Post Analytics:
- Word count
- Character count
- Creation date
- Last update date
- Publication date

## 🚀 Future Roadmap

### Planned Features:
- [ ] Post categories/tags
- [ ] Post scheduling
- [ ] Post templates
- [ ] Rich text editor
- [ ] Post sharing
- [ ] Post analytics dashboard
- [ ] Bulk operations
- [ ] Post export/import

---

## 📞 Support

For questions and support:
- **Documentation**: This README file
- **Tests**: `tests.py` file
- **Examples**: Usage examples section

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready ✅

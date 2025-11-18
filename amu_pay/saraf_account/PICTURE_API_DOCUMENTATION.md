# Saraf Account Picture Management API Documentation

## Overview
This document describes the API endpoints for managing saraf account pictures. The system supports uploading, updating, and deleting pictures for saraf accounts.

## Base URL
```
/api/saraf-account/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Available Picture Fields
- `saraf_logo` - Main business logo
- `saraf_logo_wallpeper` - Background/wallpaper image
- `front_id_card` - Front side of ID card
- `back_id_card` - Back side of ID card

## API Endpoints

### 1. Get All Pictures
**GET** `/api/saraf-account/pictures/`

Retrieves all pictures for the authenticated saraf account.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "message": "Pictures retrieved successfully",
    "saraf_id": 123,
    "saraf_name": "Business Name",
    "pictures": {
        "saraf_id": 123,
        "full_name": "Business Name",
        "exchange_name": "Exchange Name",
        "saraf_logo": "/media/saraf_photos/logo.jpg",
        "saraf_logo_wallpeper": "/media/saraf_photos/wallpaper.jpg",
        "front_id_card": "/media/saraf_photos/front_id.jpg",
        "back_id_card": "/media/saraf_photos/back_id.jpg",
        "saraf_logo_url": "http://localhost:8000/media/saraf_photos/logo.jpg",
        "saraf_logo_wallpeper_url": "http://localhost:8000/media/saraf_photos/wallpaper.jpg",
        "front_id_card_url": "http://localhost:8000/media/saraf_photos/front_id.jpg",
        "back_id_card_url": "http://localhost:8000/media/saraf_photos/back_id.jpg"
    }
}
```

### 2. Update Multiple Pictures
**PUT** `/api/saraf-account/pictures/`

Updates multiple picture fields at once.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
```
saraf_logo: <file>
saraf_logo_wallpeper: <file>
front_id_card: <file>
back_id_card: <file>
```

**Response:**
```json
{
    "message": "Pictures updated successfully",
    "updated_fields": ["saraf_logo", "front_id_card"],
    "saraf_id": 123,
    "pictures": {
        // ... updated picture data with URLs
    }
}
```

### 3. Update Single Picture
**PUT** `/api/saraf-account/pictures/{picture_field}/`

Updates a single picture field.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Parameters:**
- `picture_field`: One of `saraf_logo`, `saraf_logo_wallpeper`, `front_id_card`, `back_id_card`

**Body (multipart/form-data):**
```
{picture_field}: <file>
```

**Response:**
```json
{
    "message": "saraf_logo updated successfully",
    "picture_field": "saraf_logo",
    "picture_url": "http://localhost:8000/media/saraf_photos/new_logo.jpg",
    "saraf_id": 123
}
```

### 4. Delete Multiple Pictures
**DELETE** `/api/saraf-account/pictures/`

Deletes multiple picture fields at once.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body:**
```json
{
    "fields_to_delete": ["saraf_logo", "saraf_logo_wallpeper"]
}
```

**Response:**
```json
{
    "message": "Pictures deleted successfully",
    "deleted_fields": ["saraf_logo", "saraf_logo_wallpeper"],
    "saraf_id": 123
}
```

### 5. Delete Single Picture
**DELETE** `/api/saraf-account/pictures/{picture_field}/`

Deletes a single picture field.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Parameters:**
- `picture_field`: One of `saraf_logo`, `saraf_logo_wallpeper`, `front_id_card`, `back_id_card`

**Response:**
```json
{
    "message": "saraf_logo deleted successfully",
    "picture_field": "saraf_logo",
    "saraf_id": 123
}
```

## File Validation Rules

### File Size
- Maximum file size: **5MB**

### Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WEBP (.webp)

### Image Dimensions
- Maximum dimensions: **4096x4096 pixels**
- Minimum dimensions: **10x10 pixels**

### Security Features
- File extension validation
- Image content verification using PIL
- File format validation
- Comprehensive error logging

### Error Responses

#### File Too Large
```json
{
    "error": "saraf_logo file size cannot exceed 5MB"
}
```

#### Invalid Format
```json
{
    "error": "saraf_logo must be in JPEG, PNG, or WEBP format"
}
```

#### Invalid Field Name
```json
{
    "error": "Invalid picture field",
    "valid_fields": ["saraf_logo", "saraf_logo_wallpeper", "front_id_card", "back_id_card"]
}
```

#### Authentication Error
```json
{
    "error": "Invalid user token"
}
```

## Usage Examples

### cURL Examples

#### Get All Pictures
```bash
curl -X GET "http://localhost:8000/api/saraf-account/pictures/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update Logo
```bash
curl -X PUT "http://localhost:8000/api/saraf-account/pictures/saraf_logo/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "saraf_logo=@/path/to/new_logo.jpg"
```

#### Update Multiple Pictures
```bash
curl -X PUT "http://localhost:8000/api/saraf-account/pictures/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "saraf_logo=@/path/to/logo.jpg" \
  -F "front_id_card=@/path/to/front_id.jpg" \
  -F "back_id_card=@/path/to/back_id.jpg"
```

#### Delete Logo
```bash
curl -X DELETE "http://localhost:8000/api/saraf-account/pictures/saraf_logo/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Delete Multiple Pictures
```bash
curl -X DELETE "http://localhost:8000/api/saraf-account/pictures/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fields_to_delete": ["saraf_logo", "saraf_logo_wallpeper"]}'
```

### JavaScript Examples

#### Fetch API
```javascript
// Get all pictures
async function getPictures() {
    const response = await fetch('/api/saraf-account/pictures/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    return await response.json();
}

// Update single picture
async function updatePicture(fieldName, file) {
    const formData = new FormData();
    formData.append(fieldName, file);
    
    const response = await fetch(`/api/saraf-account/pictures/${fieldName}/`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
    });
    
    return await response.json();
}

// Delete single picture
async function deletePicture(fieldName) {
    const response = await fetch(`/api/saraf-account/pictures/${fieldName}/`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });
    
    return await response.json();
}
```

#### Axios Examples
```javascript
import axios from 'axios';

// Configure axios with base URL and auth token
const api = axios.create({
    baseURL: 'http://localhost:8000/api/saraf-account',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
});

// Get all pictures
const getPictures = async () => {
    try {
        const response = await api.get('/pictures/');
        return response.data;
    } catch (error) {
        console.error('Error fetching pictures:', error);
        throw error;
    }
};

// Update single picture
const updatePicture = async (fieldName, file) => {
    try {
        const formData = new FormData();
        formData.append(fieldName, file);
        
        const response = await api.put(`/pictures/${fieldName}/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error updating picture:', error);
        throw error;
    }
};

// Delete single picture
const deletePicture = async (fieldName) => {
    try {
        const response = await api.delete(`/pictures/${fieldName}/`);
        return response.data;
    } catch (error) {
        console.error('Error deleting picture:', error);
        throw error;
    }
};
```

### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

function PictureManager() {
    const [pictures, setPictures] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchPictures();
    }, []);

    const fetchPictures = async () => {
        try {
            const response = await fetch('/api/saraf-account/pictures/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            const data = await response.json();
            setPictures(data.pictures);
        } catch (error) {
            console.error('Error fetching pictures:', error);
        }
    };

    const handleFileUpload = async (fieldName, file) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append(fieldName, file);
            
            const response = await fetch(`/api/saraf-account/pictures/${fieldName}/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData
            });
            
            if (response.ok) {
                await fetchPictures();
                alert('Picture updated successfully!');
            } else {
                const error = await response.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error('Error updating picture:', error);
            alert('Error updating picture');
        } finally {
            setLoading(false);
        }
    };

    const handleDeletePicture = async (fieldName) => {
        if (!window.confirm(`Are you sure you want to delete ${fieldName}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/saraf-account/pictures/${fieldName}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            if (response.ok) {
                await fetchPictures();
                alert('Picture deleted successfully!');
            } else {
                const error = await response.json();
                alert(`Error: ${error.error}`);
            }
        } catch (error) {
            console.error('Error deleting picture:', error);
            alert('Error deleting picture');
        }
    };

    if (!pictures) return <div>Loading...</div>;

    const pictureFields = [
        { key: 'saraf_logo', label: 'Business Logo' },
        { key: 'saraf_logo_wallpeper', label: 'Wallpaper' },
        { key: 'front_id_card', label: 'Front ID Card' },
        { key: 'back_id_card', label: 'Back ID Card' }
    ];

    return (
        <div className="picture-manager">
            <h2>Manage Pictures</h2>
            
            {pictureFields.map(field => (
                <div key={field.key} className="picture-field">
                    <h3>{field.label}</h3>
                    {pictures[`${field.key}_url`] && (
                        <img 
                            src={pictures[`${field.key}_url`]} 
                            alt={field.label} 
                            style={{maxWidth: '200px', marginBottom: '10px'}} 
                        />
                    )}
                    <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => e.target.files[0] && handleFileUpload(field.key, e.target.files[0])}
                        disabled={loading}
                        style={{marginBottom: '10px'}}
                    />
                    {pictures[field.key] && (
                        <button 
                            onClick={() => handleDeletePicture(field.key)} 
                            disabled={loading}
                            style={{marginLeft: '10px'}}
                        >
                            Delete {field.label}
                        </button>
                    )}
                </div>
            ))}
        </div>
    );
}

export default PictureManager;
```

## Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Notes

1. **File Storage**: Pictures are stored in `media/saraf_photos/` directory
2. **Automatic Cleanup**: Old files are automatically deleted when replaced (after successful save)
3. **Action Logging**: All picture changes are logged in the ActionLog model
4. **Security**: All endpoints require valid JWT authentication
5. **Enhanced Validation**: Files are validated for size, format, extension, and content before upload
6. **Transaction Safety**: All picture operations are wrapped in database transactions
7. **Error Logging**: Comprehensive logging for debugging and monitoring
8. **Media URL Support**: Media files are properly served in both development and production

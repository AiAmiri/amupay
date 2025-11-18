# Saraf Account Picture API - Quick Start Guide

## 🚀 API Endpoints Ready to Use!

The saraf account picture management API endpoints are **already implemented and working**. Here's how to use them:

## 📍 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/saraf/pictures/` | Get all pictures |
| `PUT` | `/api/saraf/pictures/` | Update multiple pictures |
| `PUT` | `/api/saraf/pictures/{field}/` | Update single picture |
| `DELETE` | `/api/saraf/pictures/` | Delete multiple pictures |
| `DELETE` | `/api/saraf/pictures/{field}/` | Delete single picture |

## 🔑 Authentication Required

All endpoints require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

## 📸 Picture Fields Available

- `saraf_logo` - Business logo
- `saraf_logo_wallpeper` - Wallpaper/background
- `front_id_card` - Front ID card
- `back_id_card` - Back ID card

## 🧪 Quick Test Examples

### 1. Get All Pictures
```bash
curl -X GET "http://localhost:8000/api/saraf/pictures/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 2. Update Logo
```bash
curl -X PUT "http://localhost:8000/api/saraf/pictures/saraf_logo/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "saraf_logo=@/path/to/logo.jpg"
```

### 3. Delete Logo
```bash
curl -X DELETE "http://localhost:8000/api/saraf/pictures/saraf_logo/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📱 Frontend Integration

### JavaScript Example
```javascript
// Get all pictures
async function getPictures() {
    const response = await fetch('/api/saraf/pictures/', {
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
    
    const response = await fetch(`/api/saraf/pictures/${fieldName}/`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
    });
    
    return await response.json();
}
```

## ✅ Features Included

- ✅ **File Validation**: Max 5MB, JPEG/PNG/WEBP only
- ✅ **Automatic Cleanup**: Old files deleted when replaced
- ✅ **Full URL Generation**: Complete URLs for frontend display
- ✅ **Action Logging**: All changes logged for audit trail
- ✅ **Error Handling**: Detailed error messages
- ✅ **Security**: JWT authentication required

## 📋 Response Examples

### Get Pictures Response
```json
{
    "message": "Pictures retrieved successfully",
    "saraf_id": 123,
    "saraf_name": "Business Name",
    "pictures": {
        "saraf_logo_url": "http://localhost:8000/media/saraf_photos/logo.jpg",
        "saraf_logo_wallpeper_url": "http://localhost:8000/media/saraf_photos/wallpaper.jpg",
        "front_id_card_url": "http://localhost:8000/media/saraf_photos/front_id.jpg",
        "back_id_card_url": "http://localhost:8000/media/saraf_photos/back_id.jpg"
    }
}
```

### Update Picture Response
```json
{
    "message": "saraf_logo updated successfully",
    "picture_field": "saraf_logo",
    "picture_url": "http://localhost:8000/media/saraf_photos/new_logo.jpg",
    "saraf_id": 123
}
```

## 🎯 Ready to Use!

The API endpoints are **fully implemented and tested**. You can start using them immediately in your frontend application or API client.

For detailed documentation, see: `amu_pay/saraf_account/PICTURE_API_DOCUMENTATION.md`

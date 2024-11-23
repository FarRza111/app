# Tech Learning Hub API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

### Admin Login
```http
POST /admin/login
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "message": "Login successful"
}
```

## Courses

### List All Courses
```http
GET /courses
```

**Response:**
```json
{
    "courses": [
        {
            "id": "string",
            "title": "string",
            "description": "string",
            "price": "float",
            "duration": "string",
            "modules": [
                {
                    "title": "string",
                    "description": "string"
                }
            ],
            "outcomes": ["string"]
        }
    ]
}
```

### Get Course Details
```http
GET /courses/{course_id}
```

**Parameters:**
- `course_id` (path): The ID of the course

**Response:**
```json
{
    "id": "string",
    "title": "string",
    "description": "string",
    "price": "float",
    "duration": "string",
    "modules": [
        {
            "title": "string",
            "description": "string"
        }
    ],
    "outcomes": ["string"],
    "progress_percentage": "float" (if authenticated)
}
```

## Admin Course Management

### Create Course
```http
POST /admin/api/courses
```

**Request Body:**
```json
{
    "title": "string",
    "description": "string",
    "price": "float",
    "duration": "string",
    "modules": [
        {
            "title": "string",
            "description": "string"
        }
    ],
    "outcomes": ["string"]
}
```

**Response:**
```json
{
    "message": "Course created successfully",
    "course_id": "string"
}
```

### Update Course
```http
PUT /admin/api/courses/{course_id}
```

**Parameters:**
- `course_id` (path): The ID of the course

**Request Body:**
```json
{
    "title": "string",
    "description": "string",
    "price": "float",
    "duration": "string",
    "modules": [
        {
            "title": "string",
            "description": "string"
        }
    ],
    "outcomes": ["string"]
}
```

**Response:**
```json
{
    "message": "Course updated successfully"
}
```

### Delete Course
```http
DELETE /admin/api/courses/{course_id}
```

**Parameters:**
- `course_id` (path): The ID of the course

**Response:**
```json
{
    "message": "Course deleted successfully"
}
```

## User Progress

### Update Progress
```http
POST /api/progress/{course_id}/{module_id}
```

**Parameters:**
- `course_id` (path): The ID of the course
- `module_id` (path): The ID of the module

**Request Body:**
```json
{
    "completed": "boolean"
}
```

**Response:**
```json
{
    "message": "Progress updated successfully",
    "progress_percentage": "float"
}
```

### Get Progress
```http
GET /api/progress/{course_id}
```

**Parameters:**
- `course_id` (path): The ID of the course

**Response:**
```json
{
    "completed_modules": ["string"],
    "progress_percentage": "float"
}
```

## Learning Time Tracking

### Track Learning Time
```http
POST /api/track-time/{course_id}
```

**Parameters:**
- `course_id` (path): The ID of the course

**Request Body:**
```json
{
    "minutes": "integer"
}
```

**Response:**
```json
{
    "message": "Learning time tracked successfully",
    "total_time": "integer"
}
```

## Certificates

### Generate Certificate
```http
POST /api/certificates/{course_id}
```

**Parameters:**
- `course_id` (path): The ID of the course

**Response:**
```json
{
    "message": "Certificate generated successfully",
    "certificate_id": "string"
}
```

### Download Certificate
```http
GET /api/certificates/{certificate_id}/download
```

**Parameters:**
- `certificate_id` (path): The ID of the certificate

**Response:**
- Certificate file (PDF)

## Contact Form

### Submit Contact Form
```http
POST /api/contact
```

**Request Body:**
```json
{
    "name": "string",
    "email": "string",
    "message": "string"
}
```

**Response:**
```json
{
    "message": "Message sent successfully"
}
```

## Course Purchase

### Purchase Course
```http
POST /api/purchase
```

**Request Body:**
```json
{
    "email": "string",
    "name": "string",
    "course_id": "string"
}
```

**Response:**
```json
{
    "message": "Purchase successful",
    "purchase_id": "string"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Error message explaining what went wrong"
}
```

### 401 Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
    "detail": "Not enough privileges"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

## Environment Variables

The following environment variables are required:

```shell
ADMIN_USERNAME=admin_username
ADMIN_PASSWORD=admin_password
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@example.com
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
```

## Rate Limiting

- API requests are limited to 100 requests per minute per IP address
- Admin API endpoints are limited to 50 requests per minute per IP address

## Notes

1. All timestamps are returned in ISO 8601 format
2. All requests must include the `Content-Type: application/json` header
3. Authentication is required for all admin endpoints and user-specific operations
4. Course progress and certificates are only available for authenticated users

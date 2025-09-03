# API Endpoints Reference

## Health Endpoints

### GET `/health`
Returns server health status
```json
{
  "status": "ok"
}
```

## User Management

### GET `/users`
Get all users
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
]
```

### POST `/users`
Create a new user
```json
{
  "id": 3,
  "name": "New User",
  "email": "new@example.com"
}
```

### PUT `/users/:id`
Update user by ID
```json
{
  "message": "User updated"
}
```

### DELETE `/users/:id`
Delete user by ID

### GET `/users/{id}`
Get user by ID

### PUT `/users/{id}`
Update user by path parameter

### DELETE `/users/{id}`
Delete user by path parameter

## API Version Endpoints

### GET `/api/v1/health`
Health check for v1 API

### GET `/api/v1/users`
Get users for v1 API

### POST `/api/v1/users`
Create user for v1 API

### GET `/api/v2/health`
Health check for v2 API

### GET `/api/v2/users`
Get users for v2 API

### POST `/api/v2/users`
Create user for v2 API

## Content Management

### GET `/posts`
Get all posts

### POST `/posts`
Create new post

### GET `/comments`
Get all comments

### POST `/comments`
Create new comment

### PUT `/comments`
Update comment

## System Endpoints

### GET `/analyze`
Analyze API endpoints

### GET `/docs`
Get API documentation

### GET `/scan`
Scan for issues

### GET `/status`
Get system status

## Framework Examples

### Echo Framework
```bash
curl /echo/users
```

### Gin Framework
```bash
curl /gin/users
curl -X POST /gin/users
```

## Testing Commands

Basic testing:
```bash
curl /health
curl /users
curl -X POST /users
```

Framework testing:
```bash
curl /api/v1/users
curl /api/v2/users
curl /posts
curl /comments

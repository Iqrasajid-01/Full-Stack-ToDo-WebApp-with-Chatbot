# API Contracts: Tasks

## GET /api/tasks

**Description**: Retrieve list of tasks for authenticated user

**Headers**:
```
Authorization: Bearer {jwt-token}
```

**Query Parameters**:
- `status`: Filter by task status (all, pending, completed) - optional, defaults to "all"
- `priority`: Filter by priority (low, medium, high) - optional
- `page`: Page number for pagination - optional, defaults to 1
- `limit`: Number of tasks per page - optional, defaults to 20

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "tasks": [
      {
        "id": "uuid-string",
        "userId": "uuid-string",
        "title": "Complete project proposal",
        "description": "Finish the project proposal document",
        "isCompleted": false,
        "priority": "high",
        "dueDate": "2026-02-15T10:00:00Z",
        "createdAt": "2026-02-06T09:00:00Z",
        "updatedAt": "2026-02-06T09:00:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 3,
      "totalItems": 50,
      "hasNext": true,
      "hasPrevious": false
    }
  }
}
```

## POST /api/tasks

**Description**: Create a new task for authenticated user

**Headers**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs, fruits",
  "priority": "medium",
  "dueDate": "2026-02-07T18:00:00Z"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-string",
    "userId": "uuid-string",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, fruits",
    "isCompleted": false,
    "priority": "medium",
    "dueDate": "2026-02-07T18:00:00Z",
    "createdAt": "2026-02-06T10:30:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  }
}
```

**Response (Validation Error)**:
```json
{
  "status": "error",
  "errors": [
    {
      "field": "title",
      "message": "Title is required"
    }
  ]
}
```

## GET /api/tasks/{id}

**Description**: Retrieve a specific task by ID

**Headers**:
```
Authorization: Bearer {jwt-token}
```

**Path Parameters**:
- `id`: Task ID

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-string",
    "userId": "uuid-string",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, fruits",
    "isCompleted": false,
    "priority": "medium",
    "dueDate": "2026-02-07T18:00:00Z",
    "createdAt": "2026-02-06T10:30:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  }
}
```

## PUT /api/tasks/{id}

**Description**: Update an existing task

**Headers**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**Path Parameters**:
- `id`: Task ID

**Request Body** (partial updates allowed):
```json
{
  "title": "Buy weekly groceries",
  "isCompleted": true
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-string",
    "userId": "uuid-string",
    "title": "Buy weekly groceries",
    "description": "Milk, bread, eggs, fruits",
    "isCompleted": true,
    "priority": "medium",
    "dueDate": "2026-02-07T18:00:00Z",
    "createdAt": "2026-02-06T10:30:00Z",
    "updatedAt": "2026-02-06T11:00:00Z",
    "completedAt": "2026-02-06T11:00:00Z"
  }
}
```

## DELETE /api/tasks/{id}

**Description**: Delete a specific task

**Headers**:
```
Authorization: Bearer {jwt-token}
```

**Path Parameters**:
- `id`: Task ID

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Task deleted successfully"
}
```

## PATCH /api/tasks/{id}/toggle-complete

**Description**: Toggle the completion status of a task

**Headers**:
```
Authorization: Bearer {jwt-token}
Content-Type: application/json
```

**Path Parameters**:
- `id`: Task ID

**Request Body**:
```json
{
  "isCompleted": true
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid-string",
    "isCompleted": true,
    "updatedAt": "2026-02-06T11:30:00Z",
    "completedAt": "2026-02-06T11:30:00Z"
  }
}
```
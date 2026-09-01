# TezMindz Curriculum API - Postman Testing Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Authentication](#authentication)
4. [API Endpoints Overview](#api-endpoints-overview)
5. [Detailed Endpoint Testing](#detailed-endpoint-testing)
6. [Sample JSON Payloads](#sample-json-payloads)
7. [Common Response Codes](#common-response-codes)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure:
- **PostgreSQL** is installed and running locally on `localhost:5432`
- **Django development server** is running (`python manage.py runserver`)
- **Postman** is installed (download from https://www.postman.com/downloads/)
- You have created a superuser account (see Setup section)

---

## Setup Instructions

### 1. Setup PostgreSQL Database

```bash
# Open PostgreSQL CLI
psql -U postgres

# Create database and user
CREATE DATABASE tezmindz_dev;
CREATE USER tezmindz_user WITH PASSWORD 'tezmindz_pass';
ALTER ROLE tezmindz_user SET client_encoding TO 'utf8';
ALTER ROLE tezmindz_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tezmindz_user SET default_transaction_deferrable TO on;
ALTER ROLE tezmindz_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tezmindz_dev TO tezmindz_user;
\q
```

### 2. Configure Django Environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://tezmindz_user:tezmindz_pass@localhost:5432/tezmindz_dev
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Run Migrations

```bash
# From your project root
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser for Testing

```bash
python manage.py createsuperuser
# Follow the prompts:
# Email: admin@tezmindz.com
# Password: your-secure-password
# Confirm Password: your-secure-password
```

### 5. Start Django Development Server

```bash
python manage.py runserver
# Should see: Starting development server at http://127.0.0.1:8000/
```

### 6. Seed Initial Data (Optional but Recommended)

```bash
# Create initial Grades and Subjects via Django shell
python manage.py shell

# Then run:
from apps.curriculum.models import Grade, Subject

# Create Grades
Grade.objects.create(name="Grade 3", order=3)
Grade.objects.create(name="Grade 4", order=4)
Grade.objects.create(name="Grade 5", order=5)

# Create Subjects
Subject.objects.create(name="Mathematics", slug="mathematics", order=1)
Subject.objects.create(name="Science", slug="science", order=2)
Subject.objects.create(name="English", slug="english", order=3)

exit()
```

---

## Authentication

### Obtaining JWT Token

#### Step 1: Login in Postman

**POST** `http://127.0.0.1:8000/auth/jwt/create/`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "email": "admin@tezmindz.com",
  "password": "your-secure-password"
}
```

**Expected Response (Status 200):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Step 2: Set Token in Postman (Global/Collection Variable)

1. In Postman, go to **Variables** (top-right, next to eye icon)
2. Click **Globals** (or your Collection variables)
3. Create a variable named `jwt_token`
4. Paste the **access** token value in the "Initial Value" field
5. Click **Save**

#### Step 3: Use Token in All Requests

In any API request:

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Note:** `{{jwt_token}}` is a Postman variable reference that will be replaced with your actual token.

---

## API Endpoints Overview

### Base URL
```
http://127.0.0.1:8000/api/curriculum/
```

### Available Resources

| Resource | List | Create | Retrieve | Update | Partial Update | Delete |
|----------|------|--------|----------|--------|----------------|--------|
| **Grades** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Subjects** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Topics** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Concepts** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Detailed Endpoint Testing

### GRADE ENDPOINTS

#### 1. List All Grades

**GET** `http://127.0.0.1:8000/api/curriculum/grades/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Expected Response (Status 200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Grade 3",
      "order": 3,
      "created_at": "2024-09-01T10:30:00Z",
      "updated_at": "2024-09-01T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Grade 4",
      "order": 4,
      "created_at": "2024-09-01T10:30:00Z",
      "updated_at": "2024-09-01T10:30:00Z"
    }
  ]
}
```

#### 2. Create a Grade

**POST** `http://127.0.0.1:8000/api/curriculum/grades/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "name": "Grade 6",
  "order": 6
}
```

**Expected Response (Status 201):**
```json
{
  "id": 3,
  "name": "Grade 6",
  "order": 6,
  "created_at": "2024-09-01T10:35:00Z",
  "updated_at": "2024-09-01T10:35:00Z"
}
```

#### 3. Retrieve a Grade

**GET** `http://127.0.0.1:8000/api/curriculum/grades/1/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Expected Response (Status 200):**
```json
{
  "id": 1,
  "name": "Grade 3",
  "order": 3,
  "created_at": "2024-09-01T10:30:00Z",
  "updated_at": "2024-09-01T10:30:00Z"
}
```

#### 4. Update a Grade (Full)

**PUT** `http://127.0.0.1:8000/api/curriculum/grades/1/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "name": "Grade 3 (Updated)",
  "order": 3
}
```

**Expected Response (Status 200):**
```json
{
  "id": 1,
  "name": "Grade 3 (Updated)",
  "order": 3,
  "created_at": "2024-09-01T10:30:00Z",
  "updated_at": "2024-09-01T10:40:00Z"
}
```

#### 5. Partial Update a Grade

**PATCH** `http://127.0.0.1:8000/api/curriculum/grades/1/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "order": 3
}
```

#### 6. Delete a Grade

**DELETE** `http://127.0.0.1:8000/api/curriculum/grades/1/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Expected Response (Status 204):** No content

---

### SUBJECT ENDPOINTS

#### 1. List All Subjects with Filtering

**GET** `http://127.0.0.1:8000/api/curriculum/subjects/?name=Mathematics`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Expected Response (Status 200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Mathematics",
      "slug": "mathematics",
      "order": 1,
      "created_at": "2024-09-01T10:30:00Z",
      "updated_at": "2024-09-01T10:30:00Z"
    }
  ]
}
```

#### 2. Create a Subject

**POST** `http://127.0.0.1:8000/api/curriculum/subjects/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "name": "Social Studies",
  "slug": "social-studies",
  "order": 4
}
```

**Expected Response (Status 201):**
```json
{
  "id": 4,
  "name": "Social Studies",
  "slug": "social-studies",
  "order": 4,
  "created_at": "2024-09-01T10:35:00Z",
  "updated_at": "2024-09-01T10:35:00Z"
}
```

---

### TOPIC ENDPOINTS

#### 1. List All Topics with Filters

**GET** `http://127.0.0.1:8000/api/curriculum/topics/?grade=1&difficulty=easy&status=published`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Query Parameters:**
- `grade` (int) - Filter by grade ID
- `subject` (int) - Filter by subject ID
- `difficulty` (string) - easy, medium, hard
- `status` (string) - draft, under_review, approved, published
- `search` (string) - Search in title or description
- `ordering` (string) - order, created_at, published_at (prepend `-` for descending)

**Example with Search & Ordering:**
```
http://127.0.0.1:8000/api/curriculum/topics/?search=fraction&ordering=-created_at
```

**Expected Response (Status 200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction to Fractions",
      "grade": 1,
      "subject": 1,
      "difficulty": "easy",
      "status": "published",
      "published_at": "2024-09-01T09:00:00Z",
      "order": 1,
      "created_at": "2024-09-01T08:00:00Z"
    }
  ]
}
```

#### 2. Create a Topic

**POST** `http://127.0.0.1:8000/api/curriculum/topics/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "title": "Fractions Basics",
  "description": "Learn the fundamentals of fractions in an engaging way",
  "grade": 1,
  "subject": 1,
  "difficulty": "easy",
  "learning_objectives": "- Understand what a fraction is\n- Identify numerator and denominator\n- Compare simple fractions",
  "estimated_minutes": 15,
  "order": 1,
  "prerequisite_ids": []
}
```

**Expected Response (Status 201):**
```json
{
  "id": 2,
  "title": "Fractions Basics",
  "description": "Learn the fundamentals of fractions in an engaging way",
  "grade": 1,
  "grade_name": "Grade 3",
  "subject": 1,
  "subject_name": "Mathematics",
  "difficulty": "easy",
  "learning_objectives": "- Understand what a fraction is\n- Identify numerator and denominator\n- Compare simple fractions",
  "prerequisites": [],
  "prerequisite_ids": [],
  "estimated_minutes": 15,
  "order": 1,
  "status": "draft",
  "published_at": null,
  "created_at": "2024-09-01T10:45:00Z",
  "updated_at": "2024-09-01T10:45:00Z"
}
```

#### 3. Retrieve Topic (with Full Details)

**GET** `http://127.0.0.1:8000/api/curriculum/topics/1/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Expected Response (Status 200):**
```json
{
  "id": 1,
  "title": "Introduction to Fractions",
  "description": "Learn about fractions through interactive games",
  "grade": 1,
  "grade_name": "Grade 3",
  "subject": 1,
  "subject_name": "Mathematics",
  "difficulty": "medium",
  "learning_objectives": "Students will understand fractions as parts of a whole",
  "prerequisites": [],
  "prerequisite_ids": [],
  "estimated_minutes": 20,
  "order": 1,
  "status": "draft",
  "published_at": null,
  "created_at": "2024-09-01T08:00:00Z",
  "updated_at": "2024-09-01T08:00:00Z"
}
```

#### 4. Update a Topic (Full)

**PUT** `http://127.0.0.1:8000/api/curriculum/topics/2/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "title": "Fractions Basics - Updated",
  "description": "Learn the fundamentals of fractions in an even more engaging way",
  "grade": 1,
  "subject": 1,
  "difficulty": "medium",
  "learning_objectives": "- Understand what a fraction is\n- Identify numerator and denominator\n- Compare simple fractions\n- Add fractions",
  "estimated_minutes": 20,
  "order": 1,
  "prerequisite_ids": []
}
```

#### 5. Publish a Topic

**POST** `http://127.0.0.1:8000/api/curriculum/topics/2/publish/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Expected Response (Status 200):**
```json
{
  "message": "Topic published successfully",
  "topic": {
    "id": 2,
    "title": "Fractions Basics",
    "description": "Learn the fundamentals of fractions in an engaging way",
    "grade": 1,
    "grade_name": "Grade 3",
    "subject": 1,
    "subject_name": "Mathematics",
    "difficulty": "easy",
    "learning_objectives": "- Understand what a fraction is\n- Identify numerator and denominator\n- Compare simple fractions",
    "prerequisites": [],
    "prerequisite_ids": [],
    "estimated_minutes": 15,
    "order": 1,
    "status": "published",
    "published_at": "2024-09-01T10:50:00Z",
    "created_at": "2024-09-01T10:45:00Z",
    "updated_at": "2024-09-01T10:50:00Z"
  }
}
```

#### 6. Get Only Published Topics

**GET** `http://127.0.0.1:8000/api/curriculum/topics/published/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Expected Response (Status 200):**
Returns only topics with `status: "published"`

---

### CONCEPT ENDPOINTS

#### 1. List All Concepts

**GET** `http://127.0.0.1:8000/api/curriculum/concepts/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Query Parameters:**
- `topic` (int) - Filter by topic ID
- `status` (string) - draft, under_review, approved, published
- `search` (string) - Search in title or content_body
- `ordering` (string) - order, created_at, published_at

**Example:**
```
http://127.0.0.1:8000/api/curriculum/concepts/?topic=1&status=published
```

**Expected Response (Status 200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "topic": 1,
      "topic_title": "Introduction to Fractions",
      "topic_grade": "Grade 3",
      "title": "What is a Fraction?",
      "content_body": "A fraction represents a part of a whole. It consists of two numbers: the numerator (top) and denominator (bottom).",
      "order": 1,
      "status": "published",
      "published_at": "2024-09-01T09:15:00Z",
      "created_at": "2024-09-01T08:00:00Z",
      "updated_at": "2024-09-01T08:00:00Z"
    }
  ]
}
```

#### 2. Create a Concept

**POST** `http://127.0.0.1:8000/api/curriculum/concepts/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "topic": 1,
  "title": "Parts of a Fraction",
  "content_body": "Every fraction has two parts:\n\n**Numerator** (top number): Tells how many parts we have\n**Denominator** (bottom number): Tells how many equal parts the whole is divided into\n\nExample: In 3/4, the numerator is 3 and the denominator is 4.",
  "order": 2
}
```

**Expected Response (Status 201):**
```json
{
  "id": 2,
  "topic": 1,
  "topic_title": "Introduction to Fractions",
  "topic_grade": "Grade 3",
  "title": "Parts of a Fraction",
  "content_body": "Every fraction has two parts:\n\n**Numerator** (top number): Tells how many parts we have\n**Denominator** (bottom number): Tells how many equal parts the whole is divided into\n\nExample: In 3/4, the numerator is 3 and the denominator is 4.",
  "order": 2,
  "status": "draft",
  "published_at": null,
  "created_at": "2024-09-01T10:55:00Z",
  "updated_at": "2024-09-01T10:55:00Z"
}
```

#### 3. Retrieve a Concept

**GET** `http://127.0.0.1:8000/api/curriculum/concepts/2/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
```

**Expected Response (Status 200):**
```json
{
  "id": 2,
  "topic": 1,
  "topic_title": "Introduction to Fractions",
  "topic_grade": "Grade 3",
  "title": "Parts of a Fraction",
  "content_body": "Every fraction has two parts:\n\n**Numerator** (top number): Tells how many parts we have\n**Denominator** (bottom number): Tells how many equal parts the whole is divided into\n\nExample: In 3/4, the numerator is 3 and the denominator is 4.",
  "order": 2,
  "status": "draft",
  "published_at": null,
  "created_at": "2024-09-01T10:55:00Z",
  "updated_at": "2024-09-01T10:55:00Z"
}
```

#### 4. Update a Concept (Full)

**PUT** `http://127.0.0.1:8000/api/curriculum/concepts/2/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "topic": 1,
  "title": "Understanding Numerator and Denominator",
  "content_body": "Every fraction has two important parts:\n\n**Numerator** (top number): Tells us HOW MANY parts we are talking about\n**Denominator** (bottom number): Tells us INTO HOW MANY equal parts the whole thing is divided\n\n### Example:\nIn the fraction 3/4:\n- Numerator = 3 (we have 3 parts)\n- Denominator = 4 (the whole is cut into 4 equal parts)\n- So 3/4 means \"3 out of 4 equal parts\"\n\n### Practice:\nWhat does 2/5 mean? The numerator is 2 and the denominator is 5!",
  "order": 2
}
```

#### 5. Publish a Concept

**POST** `http://127.0.0.1:8000/api/curriculum/concepts/2/publish/`

**Headers:**
```
Authorization: Bearer {{jwt_token}}
Content-Type: application/json
```

**Expected Response (Status 200):**
```json
{
  "message": "Concept published successfully",
  "concept": {
    "id": 2,
    "topic": 1,
    "topic_title": "Introduction to Fractions",
    "topic_grade": "Grade 3",
    "title": "Parts of a Fraction",
    "content_body": "Every fraction has two parts:\n\n**Numerator** (top number): Tells how many parts we have\n**Denominator** (bottom number): Tells how many equal parts the whole is divided into\n\nExample: In 3/4, the numerator is 3 and the denominator is 4.",
    "order": 2,
    "status": "published",
    "published_at": "2024-09-01T11:00:00Z",
    "created_at": "2024-09-01T10:55:00Z",
    "updated_at": "2024-09-01T11:00:00Z"
  }
}
```

---

## Sample JSON Payloads

### Topic Creation - Full Example

```json
{
  "title": "Pizza Fractions Challenge",
  "description": "Interactive lesson using pizza slices to teach fractions",
  "grade": 1,
  "subject": 1,
  "difficulty": "easy",
  "learning_objectives": "- Understand fractions as equal parts of a whole\n- Identify 1/2, 1/3, 1/4\n- Compare different fractions",
  "estimated_minutes": 20,
  "order": 1,
  "prerequisite_ids": []
}
```

### Topic Update with Prerequisites

```json
{
  "title": "Advanced Fractions",
  "description": "Build on basics with fraction operations",
  "grade": 1,
  "subject": 1,
  "difficulty": "hard",
  "learning_objectives": "- Add and subtract fractions\n- Multiply and divide fractions\n- Simplify fractions",
  "estimated_minutes": 30,
  "order": 3,
  "prerequisite_ids": [1, 2]
}
```

### Concept Creation - Extended Content Example

```json
{
  "topic": 1,
  "title": "Comparing Fractions",
  "content_body": "## How to Compare Fractions\n\nSometimes we need to know which fraction is bigger or smaller.\n\n### Method 1: Same Denominator\nWhen fractions have the same denominator, just compare the numerators!\n- 2/5 < 4/5 (because 2 < 4)\n- 1/3 < 2/3 (because 1 < 2)\n\n### Method 2: Same Numerator\nWhen fractions have the same numerator, compare the denominators:\n- 1/2 > 1/4 (because 2 < 4, so halves are bigger)\n- 3/8 < 3/5 (because 8 > 5, so eighths are smaller)\n\n### Method 3: Different Numerators & Denominators\nFind a common denominator:\n- 1/2 vs 2/3\n- 1/2 = 3/6 and 2/3 = 4/6\n- So 2/3 > 1/2\n\n### Practice Problems\n1. Which is bigger: 1/4 or 3/4?\n2. Which is bigger: 2/5 or 2/8?\n3. Order these from smallest to largest: 1/2, 1/3, 1/6",
  "order": 3
}
```

---

## Common Response Codes

| Code | Meaning | When It Happens |
|------|---------|-----------------|
| **200 OK** | Success - Data retrieved | GET, PUT, PATCH successful |
| **201 Created** | Success - Resource created | POST successful |
| **204 No Content** | Success - No data to return | DELETE successful |
| **400 Bad Request** | Invalid data format or missing required fields | Check JSON syntax and required fields |
| **401 Unauthorized** | Missing or invalid authentication token | Add JWT token to Authorization header |
| **403 Forbidden** | Authenticated but no permission | Only admins can create/edit/delete |
| **404 Not Found** | Resource doesn't exist | Check the ID in the URL |
| **500 Server Error** | Server-side error | Check Django logs for details |

---

## Error Response Examples

### Missing Required Field

**Status 400:**
```json
{
  "title": ["This field may not be blank."]
}
```

### Invalid Foreign Key

**Status 400:**
```json
{
  "grade": ["Invalid pk \"999\" - object does not exist."]
}
```

### Unauthorized Access

**Status 401:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Denied (Non-Admin)

**Status 403:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Troubleshooting

### Issue: "Authentication credentials were not provided"

**Solution:** Make sure you:
1. Set the `Authorization` header to `Bearer {{jwt_token}}`
2. Replace `{{jwt_token}}` with your actual JWT token from `/auth/jwt/create/`
3. Token may have expired - get a new one

### Issue: "You do not have permission to perform this action"

**Solution:** 
- Only admin/staff users can create, update, or delete resources
- Ensure your superuser account was created
- Login with admin credentials to get the proper JWT token

### Issue: "Invalid pk" for Grade or Subject

**Solution:**
- The ID you referenced doesn't exist
- First, create or list grades/subjects to get valid IDs
- Use GET endpoints to verify IDs exist

### Issue: "No database connection"

**Solution:**
- Ensure PostgreSQL is running: `pg_isrunning`
- Check DATABASE_URL in `.env` is correct
- Run migrations: `python manage.py migrate`

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Find process on port 8000
lsof -i :8000

# Kill the process (if needed)
kill -9 <PID>

# Or use a different port
python manage.py runserver 8001
```

---

## Quick Reference - Copy & Paste URLs

```
# Authentication
POST http://127.0.0.1:8000/auth/jwt/create/

# Grades
GET    http://127.0.0.1:8000/api/curriculum/grades/
POST   http://127.0.0.1:8000/api/curriculum/grades/
GET    http://127.0.0.1:8000/api/curriculum/grades/1/
PUT    http://127.0.0.1:8000/api/curriculum/grades/1/
DELETE http://127.0.0.1:8000/api/curriculum/grades/1/

# Subjects
GET    http://127.0.0.1:8000/api/curriculum/subjects/
POST   http://127.0.0.1:8000/api/curriculum/subjects/
GET    http://127.0.0.1:8000/api/curriculum/subjects/1/
PUT    http://127.0.0.1:8000/api/curriculum/subjects/1/
DELETE http://127.0.0.1:8000/api/curriculum/subjects/1/

# Topics
GET    http://127.0.0.1:8000/api/curriculum/topics/
POST   http://127.0.0.1:8000/api/curriculum/topics/
GET    http://127.0.0.1:8000/api/curriculum/topics/1/
PUT    http://127.0.0.1:8000/api/curriculum/topics/1/
DELETE http://127.0.0.1:8000/api/curriculum/topics/1/
POST   http://127.0.0.1:8000/api/curriculum/topics/1/publish/
GET    http://127.0.0.1:8000/api/curriculum/topics/published/

# Concepts
GET    http://127.0.0.1:8000/api/curriculum/concepts/
POST   http://127.0.0.1:8000/api/curriculum/concepts/
GET    http://127.0.0.1:8000/api/curriculum/concepts/1/
PUT    http://127.0.0.1:8000/api/curriculum/concepts/1/
DELETE http://127.0.0.1:8000/api/curriculum/concepts/1/
POST   http://127.0.0.1:8000/api/curriculum/concepts/1/publish/
```

---

## Next Steps

1. **Import into Postman:** Use the endpoints above to create a collection
2. **Test CRUD Operations:** Start with Grades (simplest)
3. **Test Filtering:** Try query parameters on Topics/Concepts
4. **Test Publishing:** Use the `/publish/` endpoints
5. **Test Permissions:** Try operations without admin token (should fail with 403)

Good luck testing your TezMindz API! 🚀


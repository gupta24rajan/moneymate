# MoneyMate - Financial Expense Management API

MoneyMate is an asynchronous REST API for personal expense tracking. It is built with FastAPI, SQLAlchemy 2.0 async sessions, PostgreSQL through `asyncpg`, Pydantic v2 schemas, and JWT bearer authentication.

The backend lets users register, log in, manage their own categories, record expenses, filter and paginate expense history, and generate expense reports by total, category, month, and payment method.

## Features

- User registration and JWT login
- Password hashing with Passlib and bcrypt
- Protected routes using bearer token authentication
- Async PostgreSQL database access with SQLAlchemy 2.0
- Automatic table creation during FastAPI startup
- Category CRUD for authenticated users
- Expense CRUD with filtering, searching, sorting, and pagination
- Reporting endpoints for spending summaries
- Built-in FastAPI Swagger and ReDoc documentation
- Health check endpoint for API status

## Tech Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy 2.0 async ORM
- PostgreSQL
- asyncpg
- Pydantic and pydantic-settings
- python-jose for JWT tokens
- passlib and bcrypt for password hashing
- python-multipart for OAuth2 form login support
- python-dotenv for `.env` loading

## Project Structure

```text
app/
  main.py                    # FastAPI application factory, lifespan, router setup
  config.py                  # Pydantic settings loaded from .env
  database.py                # Async SQLAlchemy engine, session maker, DB dependency
  core/
    security.py              # Password hashing and JWT creation
  dependencies/
    auth.py                  # Current-user authentication dependency
  models/
    __init__.py              # Ensures ORM models are importable
    user.py                  # User table and relationships
    category.py              # Category table and relationships
    expense.py               # Expense table and relationships
  routers/
    auth.py                  # Register, login, current user
    category_router.py       # Category CRUD endpoints
    expenses.py              # Expense CRUD, filtering, pagination
    reports.py               # Expense report endpoints
  schemas/
    user.py                  # User request and response schemas
    category.py              # Category request and response schemas
    expense.py               # Expense request, response, pagination schemas
    report.py                # Report response schemas
  services/
    category_service.py      # Category business logic
    expense_service.py       # Expense business logic
    report_service.py        # Report aggregation logic
requirements.txt
```

## Backend Architecture

MoneyMate follows a layered FastAPI architecture:

| Layer | Location | Responsibility |
| --- | --- | --- |
| Application | `app/main.py` | Creates the FastAPI app, configures metadata, runs startup/shutdown logic, and includes routers. |
| Configuration | `app/config.py` | Loads environment variables using `pydantic-settings`. |
| Database | `app/database.py` | Creates the async SQLAlchemy engine, session factory, declarative base, and `get_db` dependency. |
| Models | `app/models/` | Defines SQLAlchemy ORM tables and relationships for users, categories, and expenses. |
| Schemas | `app/schemas/` | Defines Pydantic request and response validation models. |
| Routers | `app/routers/` | Defines API endpoints and request dependencies. |
| Services | `app/services/` | Contains business logic and database operations. |
| Security | `app/core/security.py` and `app/dependencies/auth.py` | Handles password hashing, JWT creation, and protected-route user resolution. |

### Application Startup

`app/main.py` uses a FastAPI lifespan context manager. On startup, it opens the async database engine and calls:

```python
Base.metadata.create_all
```

This creates database tables for all imported ORM models if they do not already exist. On shutdown, the database engine is disposed.

### Authentication Flow

1. A user registers with `/auth/register`.
2. The password is hashed before saving.
3. The user logs in with `/auth/login`.
4. The API returns a JWT access token.
5. Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

The token expiry is configured in code as 1 day.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gupta24rajan/moneymate.git expense-management
cd expense-management
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a PostgreSQL Database

Create a PostgreSQL database for the project. Example:

```sql
CREATE DATABASE moneymate;
```

Make sure the database user in your connection string has permission to create tables.

## Environment Setup

Create a `.env` file in the project root:

```env
APP_NAME="MoneyMate - Financial Expense Management API"
APP_ENV="development"
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/moneymate"
SECRET_KEY="replace-this-with-a-long-random-secret"
ALGORITHM="HS256"
```

Required variables:

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async SQLAlchemy database URL. Must use the `postgresql+asyncpg://` driver format. |
| `SECRET_KEY` | Yes | Secret used to sign JWT access tokens. |
| `APP_NAME` | No | FastAPI application title. Defaults to MoneyMate's configured app name. |
| `APP_ENV` | No | Runtime environment label. Defaults to `development`. |
| `ALGORITHM` | No | JWT signing algorithm. Defaults to `HS256`. |

## Run the API

Development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

## API Endpoints

### Health Check

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Returns API status, service name, and version. |

Example response:

```json
{
  "status": "healthy",
  "service": "MoneyMate API",
  "version": "1.0.0"
}
```

### Authentication

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | No | Register a new user. |
| `POST` | `/auth/login` | No | Log in and receive a bearer token. |
| `GET` | `/users/me` | Yes | Return the currently authenticated user. |

#### Register

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "username": "rajan",
  "email": "rajan@example.com",
  "password": "secret123"
}
```

Successful response status: `201 Created`

#### Login

`/auth/login` uses OAuth2 password form data. The `username` field should contain the user's email address.

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

```text
username=rajan@example.com&password=secret123
```

Successful response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

### Categories

All category endpoints require bearer token authentication.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/categories/` | Create a new expense category. |
| `GET` | `/categories/` | Get all categories for the authenticated user. |
| `GET` | `/categories/{category_id}` | Get a single category by ID. |
| `PATCH` | `/categories/{category_id}` | Update a category. |
| `DELETE` | `/categories/{category_id}` | Delete a category. |

Create category body:

```json
{
  "name": "Food",
  "description": "Meals, groceries, and snacks"
}
```

Update category body:

```json
{
  "name": "Groceries",
  "description": "Home grocery expenses"
}
```

Successful delete response status: `204 No Content`

### Expenses

All expense endpoints require bearer token authentication.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/expenses/` | Create a new expense. |
| `GET` | `/expenses/` | Get expenses with filtering, searching, sorting, and pagination. |
| `GET` | `/expenses/{expense_id}` | Get a single expense by ID. |
| `PUT` | `/expenses/{expense_id}` | Update an existing expense. |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense. |

Create expense body:

```json
{
  "amount": "249.99",
  "description": "Dinner with friends",
  "payment_method": "UPI",
  "expense_date": "2026-09-06",
  "category_id": 1
}
```

Update expense body:

```json
{
  "amount": "299.99",
  "description": "Dinner and dessert",
  "payment_method": "Credit Card",
  "expense_date": "2026-09-06",
  "category_id": 1
}
```

Supported query parameters for `GET /expenses/`:

| Parameter | Type | Description |
| --- | --- | --- |
| `category` | string | Filter by category name. |
| `category_id` | integer | Filter by category ID. |
| `payment_method` | string | Filter by payment method. |
| `start_date` | date | Filter from this date. Format: `YYYY-MM-DD`. |
| `end_date` | date | Filter through this date. Format: `YYYY-MM-DD`. |
| `min_amount` | decimal | Minimum amount. Must be greater than or equal to 0. |
| `max_amount` | decimal | Maximum amount. Must be greater than or equal to 0. |
| `search` | string | Search term in expense description. |
| `sort_by` | string | Sort field. Allowed values: `expense_date`, `amount`, `created_at`. Default: `expense_date`. |
| `order` | string | Sort order. Allowed values: `asc`, `desc`. Default: `desc`. |
| `page` | integer | Page number. Default: `1`. |
| `limit` | integer | Items per page. Default: `20`, max: `100`. |

Example:

```http
GET /expenses/?category=Food&start_date=2026-09-01&end_date=2026-09-30&sort_by=amount&order=desc&page=1&limit=10
Authorization: Bearer <access_token>
```

Paginated response shape:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "limit": 20,
  "total_pages": 0
}
```

Successful delete response status: `204 No Content`

### Expense Reports

All report endpoints require bearer token authentication.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/reports/total` | Get total expense amount and count. |
| `GET` | `/reports/category` | Get total spending grouped by category. |
| `GET` | `/reports/monthly` | Get total spending grouped by month. |
| `GET` | `/reports/payment-method` | Get total spending grouped by payment method. |

`GET /reports/total` response shape:

```json
{
  "total_amount": "1200.50",
  "total_count": 8
}
```

`GET /reports/category` response shape:

```json
[
  {
    "category_id": 1,
    "category_name": "Food",
    "total_amount": "500.00",
    "expense_count": 3
  }
]
```

`GET /reports/monthly` response shape:

```json
[
  {
    "year": 2026,
    "month": 9,
    "month_name": "September",
    "total_amount": "1200.50",
    "expense_count": 8
  }
]
```

`GET /reports/payment-method` response shape:

```json
[
  {
    "payment_method": "UPI",
    "total_amount": "750.00",
    "expense_count": 5
  }
]
```

## Example API Usage

### Register a User

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"rajan\",\"email\":\"rajan@example.com\",\"password\":\"secret123\"}"
```

### Log In

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=rajan@example.com&password=secret123"
```

### Call a Protected Endpoint

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
  -H "Authorization: Bearer <access_token>"
```

## Validation Rules

- Usernames must be 3 to 100 characters.
- User emails must be valid email addresses.
- Passwords must be 6 to 100 characters.
- Category names must be 2 to 100 characters.
- Category descriptions can be up to 255 characters.
- Expense amount must be greater than 0 with up to 2 decimal places.
- Expense description must be 3 to 500 characters.
- Payment method must be 2 to 50 characters.
- Expense dates use `YYYY-MM-DD`.

## Database Notes

- The app expects PostgreSQL with the asyncpg driver.
- Tables are created automatically on startup using SQLAlchemy metadata.
- `User` has many `Category` records.
- `User` has many `Expense` records.
- `Category` has many `Expense` records.
- Deleting a user cascades to that user's categories and expenses.
- Expense records reference users and categories with foreign keys.

## Development Notes

- Use `/docs` during development to inspect schemas and test endpoints.
- Keep `.env` out of version control because it contains secrets.
- For production, use a strong `SECRET_KEY`, disable SQL echo logging if needed, and run the API behind a production ASGI server setup.
- This project currently relies on SQLAlchemy `create_all` at startup instead of a migration tool such as Alembic.


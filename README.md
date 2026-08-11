# HABOT LSA Booking System Backend

A robust, enterprise-grade Django REST Framework (DRF) backend designed to connect Parents with **Learning Support Assistants (LSAs)**. It features concurrency-safe session scheduling, double-booking prevention, payment initiation, mock payment gateway simulation, and asynchronous webhook handling.

---

## 📖 Documentation Links
- 🔌 **[APIs.md - REST API Specification](APIs.md)**: Exhaustive documentation of all REST endpoints, request payloads, response schemas, and status codes.

---

## 🗺️ Database Schema (ER Diagram)

![HABOT ER Diagram](ER-Diagram.png)

---

## 🏗️ Architectural Design Choices (MVC vs. MVT)

### Django MVT vs. DRF Decoupled MVC
Traditional Django applications follow the **Model-View-Template (MVT)** architecture:
- **Model**: Database layer & ORM schema.
- **View**: Executes business logic and fetches model data.
- **Template**: Renders HTML/CSS templates on the server side to present the UI.

In **HABOT-Backend**, because we are building a headless RESTful API microservice to serve frontend applications (web/mobile), we adapted Django's structure into a **Model-View-Controller (MVC)** design pattern:

```text
 Client (Web/Mobile App)
        │
        │ HTTP Request (JSON)
        ▼
   [ Controller ]   ──►  Django REST Framework APIViews (`views.py`)
        │                - Handles HTTP routing, headers, permissions
        │                - Controls transaction scope (`transaction.atomic()`)
        ▼
   [ Serializer ]   ──►  DRF ModelSerializers (`serializers.py`)
        │                - Input sanitization & field-level validation
        │                - DTO transformation (Model ⇄ JSON)
        ▼
     [ Model ]      ──►  Django ORM Models (`models.py`)
        │                - Business constraints & database storage
        ▼
  PostgreSQL / DB
```

1. **Model (M)**: Django ORM classes ([`users/models.py`](users/models.py), [`bookings/models.py`](bookings/models.py), [`payments/models.py`](payments/models.py)) define relational tables, indexes, and validation rules (`clean()`).
2. **Controller (C)**: Class-based `APIView` components ([`views.py`](bookings/views.py)) act as Controllers. They handle request lifecycle, authorization (`AllowAny`/`IsAuthenticated`), execute database transactions, handle errors, and formulate HTTP JSON responses instead of rendering HTML templates.
3. **Serializer / Data Layer**: DRF Serializers replace server-side templates by acting as Data Transfer Objects (DTOs) and validation schemas.

---

## 🔒 Concurrency & Double-Booking Prevention

To meet strict booking requirements and prevent two parents from booking the same LSA for overlapping time slots during high concurrency:
- **Row-Level Locking (`select_for_update()`)**: When a booking request is initiated, the targeted `LSAProfile` row is locked in the database within a `transaction.atomic()` block.
- **Atomic Slot Validation**: Overlap validation runs while holding the lock, ensuring concurrent requests wait and evaluate against already-committed slot reservations.
- **HTTP 409 Conflict**: If an overlap is detected, the system safely rolls back and returns an HTTP `409 Conflict` status.

---

## 📁 Project Structure

```text
habot-backend/
├── config/             # Project configuration & root URL routing
│   ├── settings.py     # Environment variables, installed apps, database config
│   └── urls.py         # Root endpoint routing under /api/v1/
├── users/              # Parent & LSA Profile management
│   ├── models.py       # Parent & LSAProfile ORM models
│   ├── views.py        # Parent registration & active LSA skill search
│   ├── serializers.py  # DRF serializers for user entities
│   └── tests.py        # Unit tests for users app
├── bookings/           # Concurrency-safe session booking
│   ├── models.py       # Booking model with overlap validation logic
│   ├── views.py        # BookingView with select_for_update() locks
│   ├── serializers.py  # BookingSerializer
│   └── tests.py        # Unit tests for booking creation & overlap checks
├── payments/           # Payment initiation & webhook processing
│   ├── models.py       # Payment model (PENDING, SUCCESS, FAILED)
│   ├── views.py        # Payment initiation, mock gateway, & webhook API
│   ├── services.py     # HTTP service client for gateway requests
│   ├── serializers.py  # PaymentSerializer
│   └── tests.py        # Unit & mocked integration tests for payments
├── APIs.md             # Detailed REST API Documentation
├── README.md           # Technical project documentation
├── requirements.txt    # Python dependencies
└── manage.py           # Django management CLI
```

---

## 🚀 Setup & Installation Instructions

### Prerequisites
- **Python**: Version `3.12+`
- **Database**: PostgreSQL (recommended for production) or SQLite (for development)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/savyez/LSA-Booking.git
cd LSA-Booking

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to create `.env`:
```bash
cp .env.example .env
```

Configure your `.env` variables:
```env
DJANGO_SECRET_KEY=your-custom-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=your-DB-name
DB_USER=postgres
DB_PASS=your-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 4. Database Migrations
Run Django migrations to build database tables and indexes:
```bash
python manage.py migrate
```

### 5. Start Development Server
```bash
python manage.py runserver
```
The REST API root will be accessible at: `http://127.0.0.1:8000/api/v1/`

---

## 🧪 Testing

Execute the test suite using Django's test runner:

```bash
# Run complete test suite
python manage.py test

# Run tests for specific apps
python manage.py test users
python manage.py test bookings
python manage.py test payments
```

---

## 📑 API Overview Quick Reference

Refer to **[APIs.md](APIs.md)** for exhaustive payload specs.

| Module | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Users** | `POST` | `/api/v1/parents/` | Create Parent Profile |
| **Users** | `POST` | `/api/v1/lsas/` | Create LSA Profile |
| **Users** | `GET` | `/api/v1/lsas/search/` | Search Active LSAs by skill (`?skill=...`) |
| **Bookings** | `POST` | `/api/v1/bookings/` | Create Booking (concurrency-safe) |
| **Payments** | `POST` | `/api/v1/payments/` | Initiate Payment for a booking |
| **Payments** | `POST` | `/api/v1/payments/mock-gateway/` | Mock Payment Gateway endpoint |
| **Payments** | `POST` | `/api/v1/payments/webhook/` | Asynchronous Payment Webhook callback |


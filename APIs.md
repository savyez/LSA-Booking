# API Documentation

**Author / Candidate:** Savyez  
**Contact Email:** visnuk252@gmail.com  
**Repository:** [https://github.com/savyez/LSA-Booking](https://github.com/savyez/LSA-Booking)  

Base URL: `/api/v1/`

---

## Table of Contents
- [Users API](#users-api)
  - [Create Parent Profile](#1-create-parent-profile)
  - [Create LSA Profile](#2-create-lsa-profile)
  - [Search Active LSA Profiles](#3-search-active-lsa-profiles)
- [Bookings API](#bookings-api)
  - [Create Booking Session](#1-create-booking-session)
- [Payments API](#payments-api)
  - [Initiate Payment](#1-initiate-payment)
  - [Mock Payment Gateway](#2-mock-payment-gateway)
  - [Payment Webhook Callback](#3-payment-webhook-callback)


---

## Users API

### 1. Create Parent Profile
Creates a new parent profile in the system.

- **Endpoint**: `/api/v1/parents/`
- **Method**: `POST`
- **Authentication**: None (`AllowAny`)

#### Request Body
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "9876543210"
}
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `first_name` | string | Yes | Parent's first name |
| `last_name` | string | Yes | Parent's last name |
| `email` | string | Yes | Unique email address |
| `phone_number` | string | No | Contact phone number |

#### Response (201 Created)
```json
{
  "message": "Parent Profile created successfully!",
  "data": {
    "id": "e3b0c442-98fc-424d-8b38-2a29c11867c4",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "9876543210",
    "created_at": "2026-08-09T22:00:00.000000Z",
    "updated_at": "2026-08-09T22:00:00.000000Z"
  }
}
```

---

### 2. Create LSA Profile
Creates a new Learning Support Assistant (LSA) profile in the system.

- **Endpoint**: `/api/v1/lsas/`
- **Method**: `POST`
- **Authentication**: None (`AllowAny`)

#### Request Body
```json
{
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice.smith@example.com",
  "phone_number": "1234567890",
  "skills": "Autism, ADHD",
  "hourly_rate": "650.00",
  "is_active": true
}
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `first_name` | string | Yes | LSA's first name |
| `last_name` | string | Yes | LSA's last name |
| `email` | string | Yes | Unique email address |
| `phone_number` | string | No | Contact phone number |
| `skills` | string | No | Comma-separated list of skills |
| `hourly_rate` | decimal | No | Hourly billing rate (default: `0.00`) |
| `is_active` | boolean | No | Active availability status (default: `true`) |

#### Response (201 Created)
```json
{
  "message": "LSA Profile created successfully!",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice.smith@example.com",
    "phone_number": "1234567890",
    "skills": "Autism, ADHD",
    "hourly_rate": "650.00",
    "is_active": true,
    "created_at": "2026-08-09T22:30:00.000000Z",
    "updated_at": "2026-08-09T22:30:00.000000Z"
  }
}
```

---

### 3. Search Active LSA Profiles
Searches for active Learning Support Assistant (LSA) profiles, with optional filtering by skill and date/time slot availability.

- **Endpoint**: `/api/v1/lsas/search/`
- **Method**: `GET`
- **Authentication**: None (`AllowAny`)


#### Query Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `skill` | string | No | Case-insensitive substring query to filter LSA skills (e.g. `adhd`, `adh`, `autism`) |
| `booking_date` | string (YYYY-MM-DD) | No | Target date for checking LSA schedule availability |
| `start_time` | string (HH:MM / HH:MM:SS) | No | Desired session start time (used together with `booking_date` and `end_time`) |
| `end_time` | string (HH:MM / HH:MM:SS) | No | Desired session end time (used together with `booking_date` and `start_time`) |

#### Example Requests
- **Skill Substring Search**: `GET /api/v1/lsas/search/?skill=adh`
- **Availability Filtering**: `GET /api/v1/lsas/search/?booking_date=2026-08-15&start_time=10:00&end_time=12:00`
- **Combined Search**: `GET /api/v1/lsas/search/?skill=adhd&booking_date=2026-08-15&start_time=10:00&end_time=12:00`

#### Response (200 OK)
```json
{
  "message": "Found 1 LSAs!",
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "first_name": "Bob",
      "last_name": "Marley",
      "email": "bob.marley@example.com",
      "phone_number": "1234567890",
      "skills": "Autism, ADHD, Special Care",
      "hourly_rate": "700.00",
      "is_active": true,
      "created_at": "2026-08-09T20:00:00.000000Z",
      "updated_at": "2026-08-09T20:00:00.000000Z"
    }
  ]
}
```

---

## Bookings API

### 1. Create Booking Session
Books an active LSA for a parent during a specified date and time window. Prevents concurrent double-booking using row-level locking (`select_for_update()`).

- **Endpoint**: `/api/v1/bookings/`
- **Method**: `POST`
- **Authentication**: None (`AllowAny`)

#### Request Body
```json
{
  "parent": "e3b0c442-98fc-424d-8b38-2a29c11867c4",
  "lsa": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "booking_date": "2026-08-15",
  "start_time": "10:00",
  "end_time": "12:00"
}
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `parent` | UUID | Yes | ID of the Parent booking the session |
| `lsa` | UUID | Yes | ID of the LSAProfile being booked |
| `booking_date` | string (YYYY-MM-DD) | Yes | Scheduled date of session |
| `start_time` | string (HH:MM) | Yes | Session start time (24-hour format) |
| `end_time` | string (HH:MM) | Yes | Session end time (must be after start_time) |

#### Response (201 Created)
```json
{
  "message": "Booking created successfully!",
  "data": {
    "id": "c9a8b7c6-d5e4-3210-fedc-ba9876543210",
    "parent": "e3b0c442-98fc-424d-8b38-2a29c11867c4",
    "lsa": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "booking_date": "2026-08-15",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "status": "PENDING",
    "created_at": "2026-08-09T22:10:00.000000Z",
    "updated_at": "2026-08-09T22:10:00.000000Z"
  }
}
```

#### Response (409 Conflict - Overlapping Slot)
```json
{
  "booking": [
    "This LSA already has a booking during the selected time."
  ]
}
```

---

## Payments API

### 1. Initiate Payment
Initiates payment for an existing booking. Prevents duplicate payment creation per booking.

- **Endpoint**: `/api/v1/payments/`
- **Method**: `POST`
- **Authentication**: None (`AllowAny`)

#### Request Body
```json
{
  "booking": "c9a8b7c6-d5e4-3210-fedc-ba9876543210"
}
```

#### Response (201 Created)
```json
{
  "message": "Payment initiated successfully!",
  "data": {
    "id": "f8e7d6c5-b4a3-2109-8765-43210fe01234",
    "transaction_id": null,
    "amount": "700.00",
    "status": "PENDING",
    "created_at": "2026-08-09T22:15:00.000000Z",
    "updated_at": "2026-08-09T22:15:00.000000Z",
    "booking": "c9a8b7c6-d5e4-3210-fedc-ba9876543210"
  },
  "gateway_response": {
    "transaction_id": "9b1deb4d-3b7d-4b06-9b57-123456789abc",
    "status": "SUCCESS"
  }
}
```

#### Response (409 Conflict)
```json
{
  "payment": [
    "A payment already exists for this booking."
  ]
}
```

---

### 2. Mock Payment Gateway
Simulates an external payment gateway endpoint.

- **Endpoint**: `/api/v1/payments/mock-gateway/`
- **Method**: `POST`
- **Authentication**: None (`AllowAny`)

#### Request Body
```json
{
  "payment_id": "f8e7d6c5-b4a3-2109-8765-43210fe01234",
  "amount": "700.00",
  "simulate_status": "SUCCESS"
}
```

#### Response (200 OK)
```json
{
  "transaction_id": "9b1deb4d-3b7d-4b06-9b57-123456789abc",
  "status": "SUCCESS"
}
```

---

### 3. Payment Webhook Callback
Asynchronous webhook endpoint called by payment gateway upon payment resolution. Automatically updates payment status and confirms (`CONFIRMED`) or fails (`PAYMENT_FAILED`) the linked booking.

- **Endpoint**: `/api/v1/payments/webhook/`
- **Method**: `POST`
- **Authentication**: None (`AllowAny`)

#### Request Body
```json
{
  "payment_id": "f8e7d6c5-b4a3-2109-8765-43210fe01234",
  "transaction_id": "9b1deb4d-3b7d-4b06-9b57-123456789abc",
  "status": "SUCCESS"
}
```

#### Response (200 OK)
```json
{
  "message": "Payment webhook processed successfully.",
  "payment_status": "SUCCESS",
  "booking_status": "CONFIRMED"
}
```

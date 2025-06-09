# Authentication API Documentation

This document describes the authentication API endpoints for user registration and verification in the Moodist application.

## Environment Variables

The authentication system requires the following environment variables to be set:

```
# Security Configuration
SECRET_KEY=your_secret_key_here
SECURITY_PASSWORD_SALT=your_password_salt_here
SECURITY_PASSWORD_PEPPER=your_password_pepper_here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=itdevelopertina@gmail.com
EMAIL_HOST_PASSWORD="xhsc irbu ygrj ndke"
EMAIL_PORT=465
EMAIL_USE_SSL=True
```

## API Endpoints

### Create User

Creates a temporary inactive user and sends a verification code to their email.

**URL**: `/auth/create-user/<user_type>`

**Method**: `POST`

**URL Parameters**:
- `user_type`: Type of user to create (patient, doctor, admin)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
}
```

**Success Response**:
- **Code**: 201 Created
- **Content**:
```json
{
  "status": "success",
  "message": "Verification code sent",
  "token": "verification_token_here",
  "expires_at": "2023-06-01T12:00:00.000000"
}
```

**Error Responses**:
- **Code**: 400 Bad Request
  - Missing required fields
  - Invalid user type
- **Code**: 409 Conflict
  - User already exists and is active
- **Code**: 500 Internal Server Error
  - Database connection failed
  - Failed to generate verification token
  - Failed to create temporary user
  - Failed to create verification record

### Verify User

Verifies a user with the verification code they received, activates the account, and generates a unique 6-character uppercase ID.

**URL**: `/auth/verify`

**Method**: `POST`

**Request Body**:
```json
{
  "token": "verification_token_here",
  "code": "123456",
  "user_type": "patient"  // optional, can be used to update user type
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "status": "success",
  "message": "User verified successfully",
  "unique_id": "ABCDEF"
}
```

**Error Responses**:
- **Code**: 400 Bad Request
  - Missing required fields
  - Invalid or expired verification code
  - Verification code has expired (10-minute limit)
  - Verification code has already been used
  - Invalid verification code
- **Code**: 404 Not Found
  - Verification record not found
  - User not found
- **Code**: 500 Internal Server Error
  - Database connection failed
  - Failed to generate a unique ID for user
  - Failed to update user

### Resend Verification

Resends a verification code to the user's email.

**URL**: `/auth/resend-verification`

**Method**: `POST`

**Request Body**:
```json
{
  "token": "original_verification_token_here"
}
```

OR

```json
{
  "email": "user@example.com"
}
```

**Success Response**:
- **Code**: 200 OK
- **Content**:
```json
{
  "status": "success",
  "message": "Verification code resent",
  "token": "new_verification_token_here",
  "expires_at": "2023-06-01T12:00:00.000000"
}
```

**Error Responses**:
- **Code**: 400 Bad Request
  - No data provided
  - Either token or email must be provided
  - User is already verified and active
- **Code**: 404 Not Found
  - Verification record not found
  - User not found
- **Code**: 500 Internal Server Error
  - Database connection failed
  - Failed to generate verification token
  - Failed to create verification record

## Authentication Flow

1. **Create Temporary User**: A temporary inactive user is created with the provided email, password, and user type.
2. **Send Verification Code**: A 6-digit verification code is sent to the user's email with a 10-minute expiration time.
3. **Verify User**: The user submits the verification code, which activates their account if valid.
4. **Generate Unique ID**: Upon successful verification, a unique 6-character uppercase ID is generated for the user.
5. **Resend Verification**: If the code expires or is lost, a new verification code can be requested.

## Unique User IDs

Upon successful verification, each user is assigned a unique 6-character uppercase ID (e.g., "ABCDEF"). This ID:

1. Is guaranteed to be unique across all users
2. Consists only of uppercase letters (A-Z)
3. Is 6 characters in length
4. Can be used as an alternative identifier for the user
5. Is returned in the verification response

The system stores a mapping between this unique ID and the user's email address, allowing lookups by either identifier.

## Flow Diagram

```
┌─────────────┐     ┌────────────────┐     ┌────────────────┐
│ Mobile App  │     │  Flask Server   │     │    CouchDB     │
└─────┬───────┘     └────────┬───────┘     └────────┬───────┘
      │                      │                      │
      │  1. Create User      │                      │
      │─────────────────────>│                      │
      │                      │  2. Check if user    │
      │                      │     exists & active  │
      │                      │─────────────────────>│
      │                      │                      │
      │                      │  3. User doesn't     │
      │                      │     exist or is      │
      │                      │     inactive         │
      │                      │<─────────────────────│
      │                      │                      │
      │                      │  4. Create temporary │
      │                      │     inactive user    │
      │                      │─────────────────────>│
      │                      │                      │
      │                      │  5. Generate         │
      │                      │     verification     │
      │                      │     code & token     │
      │                      │     (10-min expiry)  │
      │                      │                      │
      │                      │  6. Save             │
      │                      │     verification     │
      │                      │     record           │
      │                      │─────────────────────>│
      │                      │                      │
      │                      │  7. Send email       │
      │                      │     with code        │
      │                      │                      │
      │  8. Return token     │                      │
      │<─────────────────────│                      │
      │                      │                      │
      │  9. User enters code │                      │
      │                      │                      │
      │  10. Verify code     │                      │
      │─────────────────────>│                      │
      │                      │  11. Validate token  │
      │                      │      and code        │
      │                      │─────────────────────>│
      │                      │                      │
      │                      │  12. Code is valid   │
      │                      │<─────────────────────│
      │                      │                      │
      │                      │  13. Generate        │
      │                      │      unique ID       │
      │                      │                      │
      │                      │  14. Activate and    │
      │                      │      verify user     │
      │                      │─────────────────────>│
      │                      │                      │
      │  15. Return success  │                      │
      │      with unique ID  │                      │
      │<─────────────────────│                      │
      │                      │                      │
```

## Security Considerations

1. **Password Security**: Passwords are hashed using SHA-256 with salt and pepper.
2. **Token Security**: Tokens are generated using itsdangerous with a secret key and salt.
3. **Verification Codes**: 6-digit numeric codes are used for verification.
4. **Expiration**: Verification codes expire after 10 minutes.
5. **Rate Limiting**: The API tracks verification attempts to prevent brute force attacks.
6. **Unique IDs**: 6-character uppercase IDs provide a unique identifier that doesn't expose the email address.
7. **Temporary Users**: Users are created as inactive until verified.

## Testing

You can test the API endpoints using tools like Postman or curl:

```bash
# Create a patient user
curl -X POST http://localhost:5000/auth/create-user/patient \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com", "password":"securepassword123"}'

# Verify a user
curl -X POST http://localhost:5000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"verification_token_here", "code":"123456"}'

# Resend verification code using token
curl -X POST http://localhost:5000/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"token":"verification_token_here"}'

# Resend verification code using email
curl -X POST http://localhost:5000/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
``` 
# Clinician Authentication API Documentation

This document describes the authentication API endpoints specifically designed for clinician (doctor/medical professional) account management in the Moodist application.

## Overview

The Moodist platform provides dedicated endpoints for clinician account management. Clinician accounts are stored in the `clinician` database and follow the same simple structure as patient accounts (email and password only) but are stored separately for role-based access control.

## Database Structure

Clinician accounts are stored in the **`clinician`** database with the following structure:

```json
{
  "_id": "ABC123",
  "type": "doctor",
  "user_type": "doctor",
  "email": "dr.smith@unimelb.edu.au",
  "password": "hashed_password",
  "is_verified": true,
  "status": "verified",
  "unique_id": "ABC123",
  "created_at": "2024-01-01T00:00:00.000000",
  "verified_at": "2024-01-01T00:05:00.000000",
  "updated_at": "2024-01-01T00:05:00.000000"
}
```

## API Endpoints

### 1. Create Clinician Account

Creates a clinician account with email and password only (same as patient accounts).

**URL**: `/auth/create-clinician`

**Method**: `POST`

**Request Body**:
```json
{
  "email": "dr.smith@unimelb.edu.au",
  "password": "SecurePassword123!"
}
```

**Required Fields**:
- `email`: Valid email address
- `password`: Secure password

**Success Response** (201 Created):
```json
{
  "status": true,
  "message": "Clinician verification link sent to your email",
  "token": "verification_token_here",
  "expires_at": "2024-01-08T00:00:00.000000",
  "expires_in_days": 7
}
```

**Error Responses**:
- **400 Bad Request**: Missing required fields
- **200 OK** (Account exists): 
  ```json
  {
    "status": false,
    "message": "Clinician account already exists. Please use password reset if needed.",
    "redirect_to_reset": true
  }
  ```
- **500 Internal Server Error**: Server-side errors

### 2. Generic Doctor Account Creation

Alternative endpoint using the generic user creation system.

**URL**: `/auth/create-user/doctor`

**Method**: `POST`

**Request Body**:
```json
{
  "email": "doctor@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response** (201 Created):
```json
{
  "status": true,
  "message": "Verification link sent to your email",
  "token": "verification_token_here",
  "expires_at": "2024-01-08T00:00:00.000000",
  "expires_in_days": 7
}
```

### 3. Clinician Login

Uses the standard login endpoint with `user_type` specified.

**URL**: `/auth/login`

**Method**: `POST`

**Request Body**:
```json
{
  "email": "dr.smith@unimelb.edu.au",
  "password": "SecurePassword123!",
  "user_type": "doctor"
}
```

**Success Response** (200 OK):
```json
{
  "status": true,
  "message": "Login successful",
  "user": {
    "id": "ABC123",
    "email": "dr.smith@unimelb.edu.au",
    "user_type": "doctor",
    "unique_id": "ABC123",
    "first_name": "John",
    "last_name": "Smith"
  }
}
```

### 4. Clinician Password Reset Request

Request a password reset code for clinician accounts.

**URL**: `/auth/clinician/request-password-reset`

**Method**: `POST`

**Request Body**:
```json
{
  "email": "dr.smith@unimelb.edu.au"
}
```

**Success Response** (200 OK):
```json
{
  "status": true,
  "message": "If your clinician email exists, a reset code has been sent.",
  "expires_in_minutes": 15
}
```

**Features**:
- 15-minute expiration for enhanced security
- Professional email template
- Security audit trail

### 5. Clinician Password Reset

Reset password using the verification code.

**URL**: `/auth/clinician/reset-password`

**Method**: `POST`

**Request Body**:
```json
{
  "email": "dr.smith@unimelb.edu.au",
  "password": "NewSecurePassword123!",
  "code": "123456"
}
```

**Success Response** (200 OK):
```json
{
  "status": true,
  "message": "Password reset successful. You can now log in with your new password."
}
```

## Account Verification

Clinician accounts use the same email verification system as other users:

1. **Verification Email**: Contains professional-styled email with clinician-specific messaging
2. **Verification Link**: `/auth/verify-link/{token}`
3. **7-Day Expiration**: Links expire after 7 days
4. **Professional Styling**: Clinical portal branding and messaging

## Security Features

### Enhanced Security for Clinicians

1. **Extended Password Reset Time**: 15 minutes (vs 10 for patients)
2. **Professional Email Templates**: Medical platform branding
3. **Audit Trail**: Timestamps and IP logging
4. **Medical License Tracking**: Optional license number storage
5. **Department/Position Metadata**: Professional role information

### Data Protection

1. **HIPAA Considerations**: Secure handling of medical professional data
2. **Access Control**: Clinician-specific database isolation
3. **Session Management**: Professional-grade session handling
4. **Email Security**: Professional email templates with security warnings

## Integration Examples

### Frontend Integration

```javascript
// Create clinician account
const createClinician = async (clinicianData) => {
  const response = await fetch('/auth/create-clinician', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(clinicianData)
  });
  
  return await response.json();
};

// Login clinician
const loginClinician = async (email, password) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      user_type: 'doctor'
    })
  });
  
  return await response.json();
};
```

### cURL Examples

```bash
# Create clinician account
curl -X POST https://your-domain.com/auth/create-clinician \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@unimelb.edu.au",
    "password": "SecurePassword123!"
  }'

# Request password reset
curl -X POST https://your-domain.com/auth/clinician/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@unimelb.edu.au"
  }'
```

## Email Templates

### Verification Email

The clinician verification email includes:
- Professional medical platform branding
- Clinician-specific messaging
- Account details summary
- Security warnings for medical data
- University of Melbourne - Department of Psychiatry branding

### Password Reset Email

The password reset email includes:
- Professional greeting with clinician name
- Security timestamp and audit information
- IT support contact information
- Clinician ID for reference
- Professional closing with department information

## Error Handling

### Common Error Scenarios

1. **Duplicate Email**: Returns status `false` with redirect instruction
2. **Invalid Fields**: 400 Bad Request with specific error messages
3. **Verification Failures**: Appropriate error messages for expired/invalid tokens
4. **Database Errors**: 500 Internal Server Error with generic message
5. **Email Failures**: Specific messages about email delivery issues

### Security Considerations

1. **Information Disclosure**: Password reset endpoints don't reveal if email exists
2. **Rate Limiting**: Implement rate limiting on sensitive endpoints
3. **Audit Logging**: All clinician account actions are logged
4. **Session Security**: Professional-grade session management

## Testing

Use the provided test script at `test/test_clinician_creation.py` to verify:

1. Enhanced clinician account creation
2. Generic doctor account creation
3. Login functionality (with verification status)
4. Password reset flow
5. Email template delivery

## Best Practices

1. **Use Enhanced Endpoint**: Prefer `/auth/create-clinician` for medical professionals
2. **Collect Professional Info**: Always collect first/last name for clinicians
3. **Verify Medical Credentials**: Consider additional verification for medical licenses
4. **Professional Communication**: Use professional language in all communications
5. **Security First**: Implement additional security measures for medical data access

## Database Queries

### Find Clinician by Email
```javascript
// Using CouchDB client
const clinician = await client.find_documents('clinician', {
  "email": "dr.smith@unimelb.edu.au"
}, 1);
```

### Update Clinician Profile
```javascript
// Update clinician document
const updateData = {
  department: "Child Psychiatry",
  position: "Department Head",
  updated_at: new Date().toISOString()
};

await client.update_document(clinicianId, updateData, 'clinician');
```

This comprehensive clinician authentication system provides enhanced features specifically designed for medical professionals while maintaining security and integration with the broader Moodist platform. 
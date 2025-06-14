# Patient-Clinician Connection System

This document outlines the design and implementation of the connection system between patients and clinicians in the Moodist platform.

## Overview

The Moodist platform allows patients and clinicians to establish connections for treatment and monitoring purposes. These connections are managed through a dedicated connections database that maintains the relationship between users while preserving privacy and security.

## Database Design

### Connections Database

Instead of storing connections within user documents, we use a dedicated `connections` database in CouchDB to represent these relationships.

#### Connection Document Structure

```json
{
  "_id": "conn:PATIENT_ID:CLINICIAN_ID",
  "patient_id": "ABC123",
  "clinician_id": "XYZ789",
  "status": "active",
  "created_at": "2025-06-13T12:00:00Z",
  "updated_at": "2025-06-13T12:00:00Z",
  "initiated_by": "clinician",
  "notes": "Optional connection notes"
}
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `_id` | String | Unique identifier for the connection, using format `conn:PATIENT_ID:CLINICIAN_ID` |
| `patient_id` | String | The unique_id of the patient |
| `clinician_id` | String | The unique_id of the clinician |
| `status` | String | Connection status: `"pending"`, `"active"`, `"revoked"`, `"rejected"` |
| `created_at` | ISO Date | When the connection was first created |
| `updated_at` | ISO Date | When the connection was last updated |
| `initiated_by` | String | Who initiated the connection: `"patient"` or `"clinician"` |
| `notes` | String | Optional notes about the connection |

### Indexes

To optimize queries, the following indexes should be created:

1. `patient_id_status_idx`: Index on `patient_id` and `status`
2. `clinician_id_status_idx`: Index on `clinician_id` and `status`

## Connection Workflow

### Establishing Connections

1. **Connection Request**:
   - Clinician or patient initiates a connection request
   - System creates a document with `status: "pending"`
   - Notification sent to the other party

2. **Connection Acceptance**:
   - Recipient accepts the connection
   - System updates status to `"active"`
   - Both parties can now see shared data

3. **Connection Rejection**:
   - Recipient rejects the connection
   - System updates status to `"rejected"`
   - Connection request is archived

### Breaking Connections

Connections can be broken in two ways:

1. **Manual Disconnection**:
   - Either party chooses to disconnect
   - System updates status to `"revoked"`
   - Both parties are notified

2. **Automatic Disconnection on user_id Change**:
   - When a user changes their `unique_id`
   - All connections associated with the old ID are automatically severed
   - This is a security feature that ensures privacy when a user chooses to reset their identity

## User ID Change and Disconnection

When a user changes their `unique_id` through the `/auth/change-user-id` endpoint:

1. The system identifies all connections where the user's old ID appears (either as `patient_id` or `clinician_id`)
2. These connections are marked as `"revoked"` with a reason of `"user_id_change"`
3. No automatic reconnection is attempted - this is by design for privacy
4. The user must establish new connections with their new identity

### Implementation Logic

```
When user changes unique_id from OLD_ID to NEW_ID:
    1. Find all connections where patient_id = OLD_ID OR clinician_id = OLD_ID
    2. For each connection:
        a. Update status to "revoked"
        b. Add reason: "user_id_change"
        c. Update updated_at timestamp
    3. Log the number of connections severed for audit purposes
```

## Query Patterns

Common query patterns for the connections database:

- **Get all clinicians for a patient**:
  ```
  Find all documents where:
    patient_id = "PATIENT_ID" AND status = "active"
  Return: clinician_id list
  ```

- **Get all patients for a clinician**:
  ```
  Find all documents where:
    clinician_id = "CLINICIAN_ID" AND status = "active"
  Return: patient_id list
  ```

- **Check if connection exists**:
  ```
  Find document with _id = "conn:PATIENT_ID:CLINICIAN_ID"
  Check if status = "active"
  ```

- **Find pending requests**:
  ```
  Find all documents where:
    (patient_id = "USER_ID" OR clinician_id = "USER_ID") AND status = "pending"
  ```

## Security Considerations

1. **Access Control**:
   - Patients can only see their own connections
   - Clinicians can only see connections to their patients
   - Admins can view all connections for support purposes

2. **Privacy**:
   - Connection documents contain minimal information
   - No sensitive medical data is stored in connection documents
   - User ID changes completely sever all connections for privacy

3. **Audit Trail**:
   - All connection changes are logged for compliance
   - Status changes include timestamps and reasons

## Benefits of This Design

1. **Scalability**: Separate database scales better than embedded arrays
2. **Query Performance**: Indexed lookups are fast even with many connections
3. **Consistency**: Single source of truth for connection status
4. **Flexibility**: Can add metadata to connections without changing user documents
5. **Privacy**: Clean disconnection when users change their identity

## Future Enhancements

1. **Connection Tiers**: Different levels of data sharing based on connection type
2. **Temporary Connections**: Time-limited connections that expire automatically
3. **Connection Groups**: Allow clinicians to organize patients into groups
4. **Connection History**: View historical connections for continuity of care
5. **Bulk Operations**: Tools for managing multiple connections at once 
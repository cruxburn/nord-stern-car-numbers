# 3-Year Rolling Period System

## Overview

The NordStern Car Numbers application now includes a sophisticated 3-year rolling period system for managing car number reservations. This system ensures fair distribution of car numbers while rewarding active participants.

## How It Works

### Basic Rules

1. **Initial Reservation**: When a car number is first reserved, it's valid for 3 years from the reservation date
2. **Usage Extension**: If the driver attends a driving event within the 3-year period, the reservation extends for another 3 years from the usage date
3. **Rolling Renewal**: Each subsequent usage extends the expiration date by 3 years from that usage date
4. **Expiration**: If no usage occurs within a 3-year period, the number becomes available for other drivers

### Example Timeline

```
April 8, 2022: Car #001 reserved by John Doe
              → Expires: April 8, 2025

June 15, 2024: John attends driving event
              → Expires: June 15, 2027 (extended by 3 years from usage)

March 10, 2026: John attends another event
              → Expires: March 10, 2029 (extended by 3 years from usage)

If no usage by March 10, 2029: Number becomes available
```

## Database Changes

### New Fields Added

The database schema has been enhanced with the following new fields:

| Field | Type | Description |
|-------|------|-------------|
| `last_usage_year` | INTEGER | Year of the most recent usage |
| `expiration_date` | DATE | Calculated expiration date |
| `usage_count` | INTEGER | Total number of times used |
| `is_active_in_period` | BOOLEAN | Whether registration is active in current period |
| `sort_order` | INTEGER | Numeric value for sorting (derived from car_number) |

### Database Migration

The migration scripts automatically handle schema updates:

**`migrate_sort_order.py`:**
- Adds `sort_order` column to existing database
- Calculates numeric sort values from car_number
- Handles invalid car numbers gracefully

**`migrate_rolling_period.py`:**
- Adds usage tracking columns (`last_usage_year`, `usage_count`, `expiration_date`, `is_active_in_period`)
- Calculates initial expiration dates for existing records
- Sets appropriate active/inactive status

**Database Indexes:**
- `idx_car_number` - Fast car number lookups
- `idx_sort_order` - Efficient sorting operations
- `idx_name` - Name-based searches
- `idx_status` - Status-based queries

## Application Features

### 1. Usage Recording

**How to Record Usage:**
- Navigate to the Search page
- Find the registration in the results table
- Click the calendar icon (📅) in the Actions column
- The system automatically updates the usage date and extends the expiration

**API Endpoint:**
```
POST /api/record_usage/<id>
```

**Usage Recording Process:**
- System prompts for usage year (defaults to current year)
- Updates `last_usage_year` with the specified year
- Increments `usage_count` by 1
- Calculates new `expiration_date` (3 years from usage year)
- Sets `is_active_in_period` to true

### 2. Expiration Tracking

**Visual Indicators:**
- **Green Badge**: Active registration with valid expiration date
- **Warning Badge**: Registration expiring within 30 days
- **Red Badge**: Expired registration

**Search Results Display:**
- Expiration date column shows the calculated expiration (YYYY format)
- Usage column shows last usage year and total count
- Status column reflects current active/inactive state
- Car numbers are sorted by `sort_order` for proper numeric ordering

### 3. Statistics Dashboard

**New Statistics:**
- **Active in Period**: Registrations currently active in their 3-year period
- **Expiring Soon**: Registrations expiring within 30 days
- **Expired**: Registrations that have expired
- **Valid Registrations**: Total minus expired

### 4. Automatic Calculations

**Expiration Date Logic:**
```python
if last_usage_year:
    expiration_date = f"{last_usage_year + 3}-01-01"
else:
    expiration_date = f"{reserved_for_year + 3}-01-01"
```

**Active Status Logic:**
```python
is_active = (current_year <= expiration_year) and (status == 'Active')
```

## Business Rules

### 1. Fair Usage Policy

- **Active Participation**: Drivers who regularly attend events keep their numbers
- **Automatic Cleanup**: Inactive numbers become available for new drivers
- **Transparent Tracking**: All usage and expiration dates are visible

### 2. Number Availability

- **Reserved Numbers**: Cannot be assigned to other drivers while active
- **Expired Numbers**: Automatically become available for new reservations
- **Conflict Prevention**: System prevents duplicate assignments

### 3. Data Integrity

- **Automatic Updates**: Expiration dates update automatically with usage
- **Status Tracking**: Active/inactive status updates based on current date
- **Audit Trail**: All changes are timestamped and tracked

## User Interface

### Search Page Enhancements

1. **New Columns:**
   - Expiration Date: Shows calculated expiration with color coding
   - Usage: Shows last usage date and total count
   - Enhanced Status: Reflects active period status

2. **New Actions:**
   - Record Usage button (calendar icon)
   - Visual indicators for expiration status

### Statistics Page Enhancements

1. **Rolling Period Statistics:**
   - Active in current period count
   - Expiring soon count (30 days)
   - Expired count
   - Valid registrations count

2. **System Information:**
   - Explanation of rolling period system
   - Usage tracking instructions
   - Best practices

## Technical Implementation

### Helper Functions

**`calculate_expiration_date(reserved_date, last_usage_date=None)`**
- Calculates expiration date based on 3-year rolling period rules
- Returns tuple: (expiration_date, is_active_in_period)

**`update_usage_for_registration(registration_id, usage_date=None)`**
- Updates usage information for a registration
- Automatically recalculates expiration date
- Updates usage count and active status

### Database Queries

**Expiring Soon Query:**
```sql
SELECT COUNT(*) FROM car_registrations 
WHERE expiration_date IS NOT NULL 
AND expiration_date <= date('now', '+30 days')
AND expiration_date > date('now')
AND status = 'Active'
```

**Active in Period Query:**
```sql
SELECT COUNT(*) FROM car_registrations 
WHERE is_active_in_period = 1
```

## Migration and Setup

### Running the Migration

1. **Automatic Migration:**
   ```bash
   python3 migrate_rolling_period.py
   ```

2. **Manual Verification:**
   ```bash
   python3 test_rolling_period.py
   ```

### Post-Migration Tasks

1. **Review Existing Data:**
   - Check expiration dates for existing registrations
   - Verify active/inactive status is correct

2. **Train Users:**
   - Explain the new usage recording feature
   - Show how to interpret expiration dates
   - Demonstrate the statistics dashboard

## Benefits

### For Drivers
- **Fair System**: Active drivers keep their preferred numbers
- **Transparency**: Clear visibility of expiration dates
- **Automatic Renewal**: No manual renewal process needed

### For Administrators
- **Automatic Management**: System handles expiration automatically
- **Clear Statistics**: Easy to see which numbers are available
- **Conflict Prevention**: Prevents duplicate assignments

### For the Organization
- **Fair Distribution**: Ensures numbers go to active participants
- **Reduced Manual Work**: Automatic tracking and expiration
- **Better Planning**: Clear visibility of upcoming expirations

## Troubleshooting

### Common Issues

1. **Expiration Date Not Calculating:**
   - Check that reserved_date is in YYYY-MM-DD format
   - Verify the migration script ran successfully

2. **Usage Not Recording:**
   - Check database permissions
   - Verify the registration ID exists

3. **Status Not Updating:**
   - Check that is_active_in_period field was added
   - Verify the calculation logic is working

### Debug Commands

```bash
# Test the rolling period logic
python3 test_rolling_period.py

# Check database schema
sqlite3 car_numbers.db ".schema car_registrations"

# View sample data
sqlite3 car_numbers.db "SELECT id, first_name, last_name, car_number, reserved_date, expiration_date, usage_count, is_active_in_period FROM car_registrations LIMIT 5;"
```

## Future Enhancements

### Potential Improvements

1. **Email Notifications**: Alert drivers when numbers are expiring
2. **Bulk Operations**: Record usage for multiple registrations
3. **Advanced Reporting**: Detailed usage analytics
4. **Custom Periods**: Configurable rolling period lengths
5. **Usage History**: Detailed log of all usage events

### API Extensions

1. **Bulk Usage Recording**: Record usage for multiple registrations
2. **Expiration Alerts**: Get list of expiring registrations
3. **Usage Analytics**: Get usage statistics and trends

## Conclusion

The 3-year rolling period system provides a fair, automated way to manage car number reservations while encouraging active participation. The system is transparent, easy to use, and provides clear visibility into the status of all registrations. 
# Step-by-Step MySQL Setup Guide

## Step 1: Open MySQL Command Line

**Windows:**
- Open Command Prompt or PowerShell
- Navigate to MySQL bin directory (usually `C:\Program Files\MySQL\MySQL Server X.X\bin`)
- Or if MySQL is in your PATH, just type:
```bash
mysql -u root -p
```

**Alternative:** Use MySQL Command Line Client from Start Menu

---

## Step 2: Enter MySQL Password

When prompted, enter your MySQL root password:
```
Enter password: ********
```

---

## Step 3: Create the Database

```sql
CREATE DATABASE IF NOT EXISTS evoting;
```

**Verify it was created:**
```sql
SHOW DATABASES;
```
You should see `evoting` in the list.

---

## Step 4: Select the Database

```sql
USE evoting;
```

You should see: `Database changed`

---

## Step 5: Create the `register` Table

```sql
CREATE TABLE register(
    username varchar(30) PRIMARY KEY,
    password varchar(30),
    contact varchar(12),
    email varchar(30),
    address varchar(40)
);
```

**Verify:**
```sql
DESCRIBE register;
```

---

## Step 6: Create the `addparty` Table

```sql
CREATE TABLE addparty(
    candidatename varchar(30),
    partyname varchar(50),
    areaname varchar(100),
    image varchar(100)
);
```

**Verify:**
```sql
DESCRIBE addparty;
```

---

## Step 7: Create the `otp` Table

```sql
CREATE TABLE otp(
    username varchar(50),
    otp int(11)
);
```

**Verify:**
```sql
DESCRIBE otp;
```

---

## Step 8: Verify All Tables

```sql
SHOW TABLES;
```

You should see:
- `addparty`
- `otp`
- `register`

---

## Step 9: (Optional) Insert Sample Data

### Add sample users:
```sql
INSERT INTO register(username, password, contact, email, address) 
VALUES ('ram', 'ram', '7702177291', 'ram@gmail.com', 'hyd');

INSERT INTO register(username, password, contact, email, address) 
VALUES ('shanthan', 'shan', '7702177291', 'shan@gmail.com', 'hydreabad');
```

### Add sample candidates:
```sql
INSERT INTO addparty(candidatename, partyname, areaname, image) 
VALUES ('raj', 'BJP', 'ameerpet', 'raj');

INSERT INTO addparty(candidatename, partyname, areaname, image) 
VALUES ('shanthan', 'BJP', 'ameerpet', 'shanthan');
```

---

## Step 10: Verify Data

```sql
SELECT * FROM register;
SELECT * FROM addparty;
```

---

## Step 11: Exit MySQL

```sql
EXIT;
```
or
```sql
QUIT;
```

---

## Complete Command Sequence (Copy-Paste Friendly)

```sql
-- Step 1: Create database
CREATE DATABASE IF NOT EXISTS evoting;

-- Step 2: Use database
USE evoting;

-- Step 3: Create register table
CREATE TABLE register(
    username varchar(30) PRIMARY KEY,
    password varchar(30),
    contact varchar(12),
    email varchar(30),
    address varchar(40)
);

-- Step 4: Create addparty table
CREATE TABLE addparty(
    candidatename varchar(30),
    partyname varchar(50),
    areaname varchar(100),
    image varchar(100)
);

-- Step 5: Create otp table
CREATE TABLE otp(
    username varchar(50),
    otp int(11)
);

-- Step 6: Verify tables
SHOW TABLES;

-- Step 7: (Optional) Insert sample data
INSERT INTO register(username, password, contact, email, address) 
VALUES ('ram', 'ram', '7702177291', 'ram@gmail.com', 'hyd');

INSERT INTO addparty(candidatename, partyname, areaname, image) 
VALUES ('raj', 'BJP', 'ameerpet', 'raj'),
       ('shanthan', 'BJP', 'ameerpet', 'shanthan');
```

---

## Troubleshooting

### If table already exists error:
```sql
DROP TABLE IF EXISTS register;
DROP TABLE IF EXISTS addparty;
DROP TABLE IF EXISTS otp;
```
Then recreate them.

### To check current database:
```sql
SELECT DATABASE();
```

### To see all tables:
```sql
SHOW TABLES;
```

### To see table structure:
```sql
DESCRIBE table_name;
```

---

## Next Steps After Database Setup

1. **Update database password in code** (if needed):
   - File: `EVotingApp/views.py`
   - Line 107, 131, etc.
   - Change: `password = 'nikshitha12345'` to your MySQL password

2. **Run Django migrations** (if using Django models):
   ```bash
   python manage.py migrate
   ```

3. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```


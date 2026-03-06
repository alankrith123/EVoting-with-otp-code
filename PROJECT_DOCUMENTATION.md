# E-Voting System - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Methodology & Workflow](#methodology--workflow)
4. [Module Specifications](#module-specifications)
5. [Technical Implementation](#technical-implementation)
6. [Data Flow](#data-flow)

---

## 🎯 Project Overview

**Project Name:** Blockchain-Based E-Voting System with OTP Authentication

**Purpose:** A secure electronic voting system that uses blockchain technology to ensure vote immutability, face recognition for user authentication, and OTP (One-Time Password) for additional security.

**Core Technologies:**
- **Backend Framework:** Django 5.2.8
- **Database:** MySQL (via PyMySQL)
- **Blockchain:** Custom implementation with SHA-256 hashing
- **Face Recognition:** OpenCV with LBPH (Local Binary Patterns Histograms)
- **Email Service:** SMTP (Gmail)

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER (Browser)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Login   │  │ Register │  │   Vote   │  │   Admin  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (Django Views)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Authentication Module  │  Voting Module             │  │
│  │  - Face Recognition     │  - OTP Generation         │  │
│  │  - User Validation      │  - Blockchain Mining      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   MySQL DB   │  │  Blockchain  │  │  Email SMTP  │
│  - register  │  │  - Blocks    │  │  - OTP Send  │
│  - addparty  │  │  - Chain     │  │              │
│  - otp       │  │  - PoW       │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Component Interaction

1. **User Interface:** HTML templates with webcam integration
2. **Business Logic:** Django views handling all operations
3. **Data Storage:** MySQL for user/party data, Pickle file for blockchain
4. **Security Layers:** Face recognition → OTP → Blockchain

---

## 🔄 Methodology & Workflow

### Development Methodology

This project follows a **layered architecture** approach with clear separation of concerns:

1. **Presentation Layer:** HTML templates with client-side webcam capture
2. **Application Layer:** Django views containing business logic
3. **Data Layer:** MySQL database + File-based blockchain storage
4. **Security Layer:** Multi-factor authentication (Face + OTP + Blockchain)

### System Workflow

#### **Phase 1: User Registration**

```
User Input → Face Capture → Face Detection → Profile Save → Database Insert
```

**Steps:**
1. User fills registration form (username, password, contact, email, address)
2. System captures face image via webcam
3. Haar Cascade detects face in image
4. Face region extracted and saved as profile image (`username.png`)
5. User credentials stored in `register` table
6. Face profile saved to `EVotingApp/static/profiles/`

#### **Phase 2: User Authentication & Voting**

```
Login → Face Verification → Double-Vote Check → OTP Generation → 
OTP Validation → Candidate Selection → Vote Mining → Blockchain Storage
```

**Detailed Steps:**

1. **Login (UserLogin)**
   - User enters username/password
   - Credentials verified against `register` table
   - OTP table cleared (fresh session)
   - User redirected to UserScreen

2. **Face Verification (ValidateUser)**
   - Webcam captures current face image
   - Face detected using Haar Cascade
   - LBPH recognizer trained on all stored profiles
   - Face matched against stored profile
   - Confidence threshold: < 80 (lower = better match)
   - If match found and username matches → proceed

3. **Double-Vote Prevention (checkUser)**
   - Blockchain scanned for existing vote by username
   - If vote exists → voting blocked
   - If no vote found → proceed to OTP

4. **OTP Generation (generate_otp)**
   - 4-digit random OTP generated
   - OTP sent to user's email via SMTP
   - OTP stored in `otp` table with username

5. **OTP Validation (OTPAction)**
   - User enters OTP
   - OTP verified against database
   - If valid → candidate selection page displayed
   - If invalid → retry OTP entry

6. **Vote Casting (FinishVote)**
   - User selects candidate
   - Transaction created: `username#candidatename#date`
   - Transaction added to blockchain's unconfirmed transactions
   - Block mined immediately (Proof-of-Work)
   - Block added to chain
   - Blockchain saved to `blockchain_contract.txt`
   - Vote confirmation displayed

#### **Phase 3: Admin Operations**

```
Admin Login → Dashboard → Add Party / View Parties / View Votes
```

**Admin Functions:**
1. **Add Party:** Upload candidate details (name, party, area, image)
2. **View Parties:** Display all registered candidates
3. **View Votes:** Count votes per candidate by scanning blockchain

---

## 📦 Module Specifications

### **Module 1: Blockchain Module**

**File:** `Blockchain.py`, `Block.py`

#### Block Class (`Block.py`)
```python
Attributes:
- index: Block position in chain
- transactions: List of vote transactions
- timestamp: Creation time
- previous_hash: Hash of previous block
- nonce: Proof-of-Work counter

Methods:
- compute_hash(): Generates SHA-256 hash of block
```

#### Blockchain Class (`Blockchain.py`)
```python
Attributes:
- chain: List of blocks
- unconfirmed_transactions: Pending votes
- difficulty: PoW difficulty (set to 2)
- peer: Peer list (not used in current implementation)
- translist: Transaction list (not used)

Methods:
- create_genesis_block(): Creates first block (index 0)
- add_block(block, proof): Validates and adds block to chain
- is_valid_proof(block, hash): Verifies PoW solution
- proof_of_work(block): Mines block by finding valid nonce
- add_new_transaction(transaction): Adds vote to pending transactions
- mine(): Creates new block and mines it
- save_object(obj, filename): Persists blockchain to file using pickle
```

**Blockchain Operations:**
- **Mining Process:**
  1. Transaction added to `unconfirmed_transactions`
  2. New block created with incremented index
  3. Proof-of-Work: Find nonce where hash starts with "00"
  4. Block validated and added to chain
  5. Blockchain serialized and saved to file

- **Transaction Format:**
  ```
  "username#candidatename#date"
  Example: "john#BJP#2024-01-15"
  ```

---

### **Module 2: Authentication Module**

**File:** `EVotingApp/views.py` (functions: `UserLogin`, `ValidateUser`, `checkUser`)

#### Components:

**1. Credential Authentication**
- Verifies username/password against MySQL `register` table
- Clears old OTP entries for fresh session

**2. Face Recognition System**
- **Face Detection:** Haar Cascade (`haarcascade_frontalface_default.xml`)
- **Face Recognition:** LBPH (Local Binary Patterns Histograms)
- **Process:**
  1. Load all face profiles from `EVotingApp/static/profiles/`
  2. Train LBPH recognizer on all profiles
  3. Detect face in captured image
  4. Predict identity with confidence score
  5. Match predicted identity with logged-in username

**3. Double-Vote Prevention**
- Scans entire blockchain for existing vote by username
- Prevents multiple votes from same user

---

### **Module 3: OTP Module**

**File:** `EVotingApp/views.py` (functions: `generate_otp`, `OTPAction`), `sendmail.py`

#### Components:

**1. OTP Generation (`generate_otp`)**
- Generates 4-digit random OTP
- Uses digits 0-9

**2. Email Service (`sendmail.py`)**
- SMTP connection to Gmail
- Sends OTP to user's registered email
- Uses Gmail App Password for authentication

**3. OTP Validation (`OTPAction`)**
- Verifies entered OTP against database
- Links OTP to username
- Grants access to voting page on success

---

### **Module 4: Voting Module**

**File:** `EVotingApp/views.py` (functions: `FinishVote`, `getCount`, `getOutput`)

#### Components:

**1. Vote Recording (`FinishVote`)**
- Creates transaction string: `username#candidatename#date`
- Adds transaction to blockchain
- Mines block immediately
- Displays block details (previous hash, block number, current hash)

**2. Vote Counting (`getCount`)**
- Scans blockchain (excluding genesis block)
- Extracts candidate name from transaction
- Counts votes per candidate

**3. Candidate Display (`getOutput`)**
- Retrieves all candidates from `addparty` table
- Displays candidate details with voting button

---

### **Module 5: Admin Module**

**File:** `EVotingApp/views.py` (functions: `AdminLogin`, `AddPartyAction`, `ViewParty`, `ViewVotes`)

#### Components:

**1. Admin Authentication (`AdminLogin`)**
- Hardcoded credentials: `admin/admin`
- Grants access to admin dashboard

**2. Party Management (`AddPartyAction`)**
- Accepts candidate details (name, party, area, image)
- Saves image to `EVotingApp/static/parties/`
- Stores data in `addparty` table

**3. View Operations**
- **ViewParty:** Lists all registered candidates
- **ViewVotes:** Shows vote count per candidate from blockchain

---

### **Module 6: Database Module**

**Database:** MySQL

#### Tables:

**1. `register` Table**
```sql
Columns:
- username (PRIMARY KEY)
- password
- contact
- email
- address
```

**2. `addparty` Table**
```sql
Columns:
- candidatename (PRIMARY KEY)
- partyname
- areaname
- image (filename)
```

**3. `otp` Table**
```sql
Columns:
- username
- otp
```

**Connection:**
- Uses PyMySQL for MySQL connectivity
- Configuration in `views.py` (DB_CONFIG dictionary)

---

### **Module 7: User Interface Module**

**Location:** `EVotingApp/templates/`

#### Templates:

1. **index.html:** Landing page
2. **Login.html:** User login form
3. **Register.html:** User registration form
4. **CaptureFace.html:** Webcam face capture
5. **UserScreen.html:** User dashboard
6. **OTPValidation.html:** OTP entry form
7. **VotePage.html:** Candidate selection page
8. **Admin.html:** Admin login
9. **AdminScreen.html:** Admin dashboard
10. **AddParty.html:** Add candidate form
11. **ViewParty.html:** Display all parties
12. **ViewVotes.html:** Display vote counts

**Features:**
- Webcam integration using `webcam.min.js`
- Responsive HTML forms
- Static file serving for images/CSS

---

## 🔧 Technical Implementation

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | Django | 5.2.8 |
| Database | MySQL | via PyMySQL 1.1.2 |
| Blockchain | Custom Python | SHA-256 |
| Face Recognition | OpenCV | 4.12.0.88 |
| Image Processing | PIL/Pillow | 12.0.0 |
| Email | SMTP (Gmail) | - |
| Frontend | HTML/CSS/JS | - |

### Key Algorithms

**1. Proof-of-Work (PoW)**
```python
Difficulty: 2 (hash must start with "00")
Process:
- Increment nonce
- Compute hash
- Check if hash starts with "00"
- Repeat until valid hash found
```

**2. LBPH Face Recognition**
```python
Algorithm: Local Binary Patterns Histograms
Process:
- Extract LBP features from face
- Create histogram of patterns
- Compare with stored histograms
- Return match with confidence score
```

**3. SHA-256 Hashing**
```python
Algorithm: Secure Hash Algorithm 256-bit
Usage: Block hash computation
Input: Block data (JSON serialized)
Output: 64-character hexadecimal hash
```

---

## 📊 Data Flow

### Registration Flow
```
User Form → views.Signup() → CaptureFace.html → 
WebCam() → saveSignup() → Face Detection → 
Profile Save → MySQL Insert → Success
```

### Voting Flow
```
Login → UserLogin() → ValidateUser() → Face Recognition → 
checkUser() → generate_otp() → sendmail() → OTPAction() → 
getOutput() → FinishVote() → Blockchain.mine() → 
Blockchain.save_object() → Confirmation
```

### Admin Flow
```
Admin.html → AdminLogin() → AdminScreen.html → 
AddPartyAction() / ViewParty() / ViewVotes()
```

---

## 🔐 Security Features

1. **Multi-Factor Authentication:**
   - Password authentication
   - Face recognition (biometric)
   - OTP verification (email-based)

2. **Blockchain Security:**
   - Immutable vote storage
   - SHA-256 cryptographic hashing
   - Proof-of-Work consensus
   - Chain integrity verification

3. **Double-Vote Prevention:**
   - Blockchain scan before voting
   - Username-based duplicate detection

4. **Data Integrity:**
   - Previous hash linking
   - Block validation
   - Transaction immutability

---

## ⚠️ Current Limitations

1. **Single-Server Deployment:** No distributed blockchain network
2. **Immediate Mining:** Votes mined individually (no batch processing)
3. **No Merkle Tree:** Simple transaction list in blocks
4. **File-Based Storage:** Blockchain stored as pickle file (not database)
5. **Hardcoded Admin:** Admin credentials not in database
6. **No Encryption:** Passwords stored in plain text
7. **No Session Management:** Global variables used for username
8. **Limited Scalability:** Blockchain scan becomes slow with many votes

---

## 🚀 System Strengths

1. **Transparency:** All votes stored in immutable blockchain
2. **Security Layers:** Multiple authentication mechanisms
3. **Auditability:** Complete vote history in blockchain
4. **User-Friendly:** Web-based interface with webcam integration
5. **Real-Time:** Immediate vote confirmation with block details

---

## 📝 Conclusion

This E-Voting system demonstrates a practical implementation of blockchain technology for secure voting. While it has limitations for production use, it effectively showcases:

- Blockchain integration for vote immutability
- Multi-factor authentication
- Face recognition for biometric security
- OTP-based email verification
- Transparent vote counting

The system provides a solid foundation that can be enhanced with distributed networking, encryption, and scalability improvements for real-world deployment.



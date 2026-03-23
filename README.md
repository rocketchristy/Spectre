# Spectre E-Commerce Platform

A full-stack e-commerce web application for trading card collectibles, built with FastAPI (Python) backend and Vue.js frontend, connected to IBM Db2 on z/OS.

## Table of Contents

- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Database Setup on z/OS](#3-database-setup-on-zos)
  - [4. Frontend Setup](#4-frontend-setup)
- [Running the Application](#running-the-application)
- [Accessing the Web Application](#accessing-the-web-application)
- [Project Structure](#project-structure)

## Technologies

**Backend:**
- Python 3.12
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- ibm_db - IBM Db2 database driver

**Frontend:**
- Vue.js 3.5 - Progressive JavaScript framework
- Vue Router - Client-side routing
- Vite - Build tool and development server
- Node.js & npm - Package management

**Database:**
- IBM Db2 on z/OS

## Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Python 3.12** or higher
2. **Node.js and npm** (for frontend)
3. **IBM Db2 License** - Required to connect to Db2 on z/OS
4. **Access to IBM Db2 on z/OS** - Database credentials and connection details
5. **Git** - For cloning the repository

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/rocketchristy/Spectre.git
cd Spectre
```

### 2. Backend Setup

#### Step 2.1: Create Virtual Environment

Navigate to the Backend directory and create a Python virtual environment:

```bash
cd Backend
python -m venv .venv
```

Activate the virtual environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

#### Step 2.2: Install Python Dependencies

With the virtual environment activated, install required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `ibm_db` - IBM Db2 driver
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic[email]` - Data validation with email support

#### Step 2.3: Configure IBM Db2 License

After installing `ibm_db`, you need to add your IBM Db2 license file:

1. Locate the `clidriver` directory in your virtual environment:
   ```
   .venv\Lib\site-packages\clidriver\license\
   ```

2. Place your IBM Db2 license file (`.lic` file) in this `license` folder.

#### Step 2.4: Configure Database Connection

Create or edit the configuration file at `Backend/DatabaseAccess/config.ini`:

```ini
[database]
username = YOUR_DB2_USERNAME
password = YOUR_DB2_PASSWORD
clidriver_path = C:\path\to\Spectre\Backend\.venv\Lib\site-packages\clidriver
database = YOUR_DATABASE_NAME
hostname = YOUR_ZOS_HOSTNAME
port = YOUR_DB2_PORT

[sku]
series_length = 2
style_length = 4
serial_length = 4
modifier_length = 3
```

**Configuration Parameters:**
- `username`: Your Db2 on z/OS username
- `password`: Your Db2 on z/OS password
- `clidriver_path`: Absolute path to the clidriver folder in your virtual environment
- `database`: Database name on z/OS
- `hostname`: z/OS system hostname or IP address
- `port`: Db2 port number (typically 446 or 448)
- SKU lengths: Configure product SKU parsing lengths (default values shown)

### 3. Database Setup on z/OS

SQL DDL scripts and JCL job files are provided in the `zOS_Datasets/HLQ/ECOMAPP/` directory.

**Option 1: Using JCL Scripts (Recommended)**

JCL files are located in `zOS_Datasets/HLQ/ECOMAPP/JCL/`. Submit them in the following order:

1. **ECOMDDL.jcl** - Create database, tablespaces, tables, and indexes
2. **ECOMGRNT.jcl** - Grant permissions
3. **ECOMINIT.jcl** - Initialize base data
4. **ECOMFILL.jcl** - Populate inventory data
5. **ECOMRPTS.jcl** - Create reports and views

**Option 2: Manual SQL Execution**

SQL scripts are located in `zOS_Datasets/HLQ/ECOMAPP/DDL/`. Execute them in the following order:

1. **E01STGDB.sql** - Create storage database
2. **E02TBSPC.sql** - Create tablespaces
3. **E03TABLE.sql** - Create tables
4. **E04INDEX.sql** - Create indexes
5. **E05CMNT.sql** - Add table comments
6. **E06GRANT.sql** - Grant permissions
7. **E07INIT1.sql** - Initialize base data (part 1)
8. **E07INIT2.sql** - Initialize base data (part 2)
9. **E07INIT3.sql** - Initialize base data (part 3)
10. **E08INVEN.sql** - Initialize inventory data
11. **E09RPTO1.sql** - Reports/views (part 1)
12. **E09RPTO2.sql** - Reports/views (part 2)
13. **E09RPTO3.sql** - Reports/views (part 3)

**Additional JCL Scripts:**
- **ECOMDROP.jcl** - Drop all database objects (use for cleanup/reset)
- **ECOMRS.jcl** - Restore database from backup

**Note:** Ensure the schema name in the scripts matches your configuration (default is `USER01`).

### 4. Frontend Setup

#### Step 4.1: Navigate to Frontend Directory

```bash
cd ../Frontend
```

#### Step 4.2: Install Node Dependencies

```bash
npm install
```

This will install all required packages listed in `package.json`, including:
- Vue.js 3.5
- Vue Router
- Vite
- Development tools (ESLint, Prettier, Vitest)

## Running the Application

### Option 1: Run Both Backend and Frontend Together (Recommended)

From the project root directory:

```bash
npm run start
```

This will start both the backend server and frontend development server concurrently.

- Backend API: **http://localhost:8000**
- Frontend Application: **http://localhost:5174**
- API Documentation (Swagger UI): **http://localhost:8000/docs**

### Option 2: Run Backend and Frontend Separately

#### Start the Backend Server

From the `Backend` directory with the virtual environment activated:

```bash
cd Backend
uvicorn RestAPI.server:app --reload
```

The backend API will be accessible at: **http://localhost:8000**

API documentation (Swagger UI) available at: **http://localhost:8000/docs**

#### Start the Frontend Development Server

From the `Frontend` directory:

```bash
cd Frontend
npm run dev
```

The frontend development server will start at: **http://localhost:5174**

## Accessing the Web Application

1. Open your web browser and navigate to: **http://localhost:5174**

2. You will see the login page

3. **First Time Users:**
   - Click on the registration/sign-up option
   - Create a new account with your details
   - Once registered, log in with your credentials

4. **Start Shopping:**
   - Browse products
   - Add items to your cart
   - Manage your inventory (if you're a seller)
   - Complete purchases through checkout

## Project Structure

```
Spectre/
├── Backend/
│   ├── DatabaseAccess/
│   │   ├── config.ini          # Database configuration
│   │   ├── dao.py              # Database connection pool
│   │   ├── user_dao.py         # User data access
│   │   ├── inventory_dao.py    # Inventory data access
│   │   ├── cart_dao.py         # Shopping cart data access
│   │   ├── orders_dao.py       # Orders data access
│   │   └── products_dao.py     # Products data access
│   ├── RestAPI/
│   │   ├── server.py           # FastAPI application
│   │   └── Routes/             # API route handlers
│   ├── Utilities/
│   │   ├── utilities.py        # Helper functions
│   │   ├── validation.py       # Pydantic models
│   │   └── logger.py           # Logging configuration
│   ├── tests/                  # Test suite
│   └── requirements.txt        # Python dependencies
├── Frontend/
│   ├── src/                    # Vue.js source code
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
├── zOS_Datasets/
│   └── HLQ/ECOMAPP/
│       ├── DDL/                # SQL DDL scripts
│       └── JCL/                # JCL job scripts
└── README.md                   # This file
```

## Development Notes

- The backend runs on **port 8000**
- The frontend runs on **port 5174**
- Use `npm run start` from the project root to run both servers concurrently
- CORS is configured to allow cross-origin requests during development
- All API endpoints require authentication via token (except registration and login)
- Logging is configured to output to console and `spectre.log` file

## Troubleshooting

**Database Connection Issues:**
- Verify `config.ini` has correct credentials and paths
- Ensure IBM Db2 license file is in the correct location
- Check network connectivity to z/OS system
- Verify Db2 port is accessible

**Import Errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Frontend Build Issues:**
- Delete `node_modules` folder and run `npm install` again
- Clear npm cache: `npm cache clean --force`

## License

This project is part of the NextGen Academy Capstone program.

## Contributors

Rocket Software NextGen Academy Spectre Team

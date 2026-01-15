-- Setup script for PostgreSQL database
-- Run this as the postgres superuser

-- Grant necessary privileges to todouser
GRANT ALL PRIVILEGES ON DATABASE todos TO todouser;

-- Connect to the todos database and grant schema privileges
\c todos

-- Grant schema usage and creation privileges
GRANT ALL ON SCHEMA public TO todouser;
GRANT CREATE ON SCHEMA public TO todouser;

-- Grant privileges on all existing tables (if any)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO todouser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO todouser;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO todouser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO todouser;

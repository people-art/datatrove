-- FineData Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if it doesn't exist (handled by environment variables)
-- The database is created automatically by POSTGRES_DB environment variable

-- Additional database setup can be added here
-- For example: custom functions, triggers, etc.

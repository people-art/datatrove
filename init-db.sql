-- FineData Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if it doesn't exist (handled by environment variables)
-- The database is created automatically by POSTGRES_DB environment variable

-- Additional database setup can be added here
-- For example: custom functions, triggers, etc.

-- Create idempotency_keys table for preventing duplicate operations
CREATE TABLE IF NOT EXISTS idempotency_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    operation VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    expires_at TIMESTAMP NOT NULL,
    response_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_idempotency_keys_expires_at ON idempotency_keys(expires_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_keys_user_id ON idempotency_keys(user_id);

-- Add SLURM cluster fields to orders table (added in v2.0.0)
-- Note: These ALTER statements will be executed after tables are created by the application
-- They are safe to run multiple times due to IF NOT EXISTS clauses

-- Clean up expired idempotency keys periodically (optional)
-- This can be run as a scheduled job
-- DELETE FROM idempotency_keys WHERE expires_at < NOW();

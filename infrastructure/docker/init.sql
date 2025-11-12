-- SecurityOrchestrator Database Initialization
-- This file initializes the database schema for the microservices architecture

-- Create database if it doesn't exist (handled by environment variables)
-- The database 'security_orchestrator' is created by POSTGRES_DB environment variable

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema for each service domain
CREATE SCHEMA IF NOT EXISTS process_management;
CREATE SCHEMA IF NOT EXISTS api_security;
CREATE SCHEMA IF NOT EXISTS test_generation;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS reporting;

-- Common enums and types
CREATE TYPE execution_status AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED');
CREATE TYPE security_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE test_type AS ENUM ('UNIT', 'INTEGRATION', 'E2E', 'SECURITY', 'PERFORMANCE');

-- Common audit table (used by all services)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    correlation_id UUID
);

-- Create indexes for audit log
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_service ON audit_log(service_name);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_correlation ON audit_log(correlation_id);

-- Common configuration table
CREATE TABLE service_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value JSONB NOT NULL,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_name, config_key)
);

-- Common health check table
CREATE TABLE service_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    service_version VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN',
    uptime_seconds BIGINT DEFAULT 0,
    memory_usage_mb INTEGER,
    cpu_usage_percent DECIMAL(5,2),
    last_check TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    next_check TIMESTAMP WITH TIME ZONE,
    details JSONB
);

-- Create indexes for health checks
CREATE INDEX idx_service_health_name ON service_health(service_name);
CREATE INDEX idx_service_health_status ON service_health(status);

-- Insert default configurations
INSERT INTO service_config (service_name, config_key, config_value) VALUES
('system', 'version', '"1.0.0"'),
('system', 'environment', '"development"'),
('system', 'maintenance_mode', 'false'),
('process-management', 'max_concurrent_processes', '10'),
('api-security', 'max_request_size_mb', '50'),
('test-generation', 'max_test_scenarios', '1000'),
('monitoring', 'retention_days', '90'),
('reporting', 'max_report_size_mb', '100');

-- Create a function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to service_config
CREATE TRIGGER update_service_config_updated_at
    BEFORE UPDATE ON service_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    old_row JSONB;
    new_row JSONB;
BEGIN
    -- Convert OLD and NEW to JSONB
    IF TG_OP = 'DELETE' THEN
        old_row = to_jsonb(OLD);
        new_row = NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        old_row = to_jsonb(OLD);
        new_row = to_jsonb(NEW);
    ELSIF TG_OP = 'INSERT' THEN
        old_row = NULL;
        new_row = to_jsonb(NEW);
    END IF;

    -- Insert audit record
    INSERT INTO audit_log (
        service_name,
        event_type,
        entity_type,
        entity_id,
        action,
        old_values,
        new_values,
        correlation_id
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        old_row,
        new_row,
        gen_random_uuid()
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Note: Individual service schemas will be created by each service
-- during their initialization process. This file only sets up
-- the common infrastructure and shared tables.

-- Grant permissions (adjust as needed for your security requirements)
-- GRANT USAGE ON SCHEMA process_management TO security_user;
-- GRANT USAGE ON SCHEMA api_security TO security_user;
-- GRANT USAGE ON SCHEMA test_generation TO security_user;
-- GRANT USAGE ON SCHEMA monitoring TO security_user;
-- GRANT USAGE ON SCHEMA reporting TO security_user;

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA process_management TO security_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA api_security TO security_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA test_generation TO security_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA monitoring TO security_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA reporting TO security_user;
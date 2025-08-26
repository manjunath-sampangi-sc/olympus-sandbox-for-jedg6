-- =====================================================
-- Olympus Analytics Database Setup Script
-- =====================================================
-- This script creates the complete database structure
-- and loads sample data for the Streamlit POC

-- Use the XS_WAREHOUSE
USE WAREHOUSE XS_WAREHOUSE;

-- =====================================================
-- 1. CREATE DATABASE AND SCHEMAS
-- =====================================================

-- Create the main database
CREATE DATABASE IF NOT EXISTS OLYMPUS_ANALYTICS;
USE DATABASE OLYMPUS_ANALYTICS;

-- Create schemas for the medallion architecture
CREATE SCHEMA IF NOT EXISTS BRONZE;   -- Raw data ingestion
CREATE SCHEMA IF NOT EXISTS SILVER;   -- Cleaned and transformed data
CREATE SCHEMA IF NOT EXISTS GOLD;     -- Business-ready analytics data
CREATE SCHEMA IF NOT EXISTS STAGING;  -- Temporary staging area

-- =====================================================
-- 2. BRONZE LAYER - RAW DATA TABLES
-- =====================================================

-- HubSpot CRM Raw Data
CREATE OR REPLACE TABLE BRONZE.HUBSPOT_CONTACTS (
    contact_id VARCHAR(50),
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company VARCHAR(255),
    job_title VARCHAR(255),
    phone VARCHAR(50),
    lead_status VARCHAR(50),
    lifecycle_stage VARCHAR(50),
    created_date TIMESTAMP,
    last_modified_date TIMESTAMP,
    deal_amount DECIMAL(15,2),
    deal_stage VARCHAR(100),
    source VARCHAR(100)
);

-- HubSpot Deals Raw Data
CREATE OR REPLACE TABLE BRONZE.HUBSPOT_DEALS (
    deal_id VARCHAR(50),
    contact_id VARCHAR(50),
    deal_name VARCHAR(255),
    amount DECIMAL(15,2),
    stage VARCHAR(100),
    probability DECIMAL(5,2),
    close_date DATE,
    created_date TIMESTAMP,
    owner_id VARCHAR(50),
    pipeline VARCHAR(100),
    source VARCHAR(100)
);

-- Disco LMS Raw Data
CREATE OR REPLACE TABLE BRONZE.DISCO_COURSES (
    course_id VARCHAR(50),
    course_name VARCHAR(255),
    course_description TEXT,
    instructor_id VARCHAR(50),
    instructor_name VARCHAR(255),
    category VARCHAR(100),
    duration_hours DECIMAL(5,2),
    difficulty_level VARCHAR(50),
    created_date TIMESTAMP,
    status VARCHAR(50)
);

CREATE OR REPLACE TABLE BRONZE.DISCO_ENROLLMENTS (
    enrollment_id VARCHAR(50),
    user_id VARCHAR(50),
    course_id VARCHAR(50),
    enrollment_date TIMESTAMP,
    completion_date TIMESTAMP,
    progress_percentage DECIMAL(5,2),
    final_score DECIMAL(5,2),
    status VARCHAR(50),
    time_spent_hours DECIMAL(8,2)
);

CREATE OR REPLACE TABLE BRONZE.DISCO_USERS (
    user_id VARCHAR(50),
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    department VARCHAR(100),
    role VARCHAR(100),
    manager_id VARCHAR(50),
    hire_date DATE,
    status VARCHAR(50),
    last_login TIMESTAMP
);

-- =====================================================
-- 3. INSERT SAMPLE DATA - HUBSPOT CRM
-- =====================================================

-- Sample HubSpot Contacts
INSERT INTO BRONZE.HUBSPOT_CONTACTS VALUES
('HSC001', 'john.smith@techcorp.com', 'John', 'Smith', 'TechCorp Inc', 'CTO', '+1-555-0101', 'Qualified', 'Customer', '2024-01-15 10:30:00', '2024-08-20 14:22:00', 150000.00, 'Proposal', 'Website'),
('HSC002', 'sarah.johnson@innovate.com', 'Sarah', 'Johnson', 'Innovate Solutions', 'VP Sales', '+1-555-0102', 'New', 'Lead', '2024-02-20 09:15:00', '2024-08-21 11:45:00', 75000.00, 'Qualification', 'Referral'),
('HSC003', 'mike.davis@startup.io', 'Mike', 'Davis', 'Startup.io', 'Founder', '+1-555-0103', 'Qualified', 'Opportunity', '2024-03-10 16:20:00', '2024-08-22 09:30:00', 200000.00, 'Negotiation', 'LinkedIn'),
('HSC004', 'lisa.chen@enterprise.com', 'Lisa', 'Chen', 'Enterprise Corp', 'Director IT', '+1-555-0104', 'Qualified', 'Customer', '2024-01-05 11:00:00', '2024-08-19 15:10:00', 300000.00, 'Closed Won', 'Trade Show'),
('HSC005', 'david.wilson@growth.com', 'David', 'Wilson', 'Growth Dynamics', 'CEO', '+1-555-0105', 'New', 'Lead', '2024-04-15 13:45:00', '2024-08-22 10:20:00', 50000.00, 'Discovery', 'Cold Call'),
('HSC006', 'emma.brown@scale.com', 'Emma', 'Brown', 'Scale Systems', 'COO', '+1-555-0106', 'Qualified', 'Opportunity', '2024-02-28 08:30:00', '2024-08-21 16:40:00', 180000.00, 'Proposal', 'Partner'),
('HSC007', 'alex.garcia@future.com', 'Alex', 'Garcia', 'Future Tech', 'CTO', '+1-555-0107', 'Qualified', 'Customer', '2024-03-20 14:15:00', '2024-08-20 12:55:00', 250000.00, 'Negotiation', 'Website'),
('HSC008', 'rachel.lee@digital.com', 'Rachel', 'Lee', 'Digital First', 'VP Marketing', '+1-555-0108', 'New', 'Lead', '2024-05-10 10:45:00', '2024-08-22 08:15:00', 90000.00, 'Qualification', 'Social Media'),
('HSC009', 'tom.anderson@cloud.com', 'Tom', 'Anderson', 'Cloud Solutions', 'Director', '+1-555-0109', 'Qualified', 'Opportunity', '2024-04-05 12:20:00', '2024-08-21 14:30:00', 120000.00, 'Discovery', 'Webinar'),
('HSC010', 'maria.rodriguez@ai.com', 'Maria', 'Rodriguez', 'AI Innovations', 'Head of Sales', '+1-555-0110', 'Qualified', 'Customer', '2024-01-25 15:30:00', '2024-08-19 11:20:00', 400000.00, 'Closed Won', 'Conference');

-- Sample HubSpot Deals
INSERT INTO BRONZE.HUBSPOT_DEALS VALUES
('HSD001', 'HSC001', 'TechCorp Enterprise License', 150000.00, 'Proposal', 75.0, '2024-09-15', '2024-01-15 10:30:00', 'REP001', 'Enterprise Sales', 'Website'),
('HSD002', 'HSC002', 'Innovate Solutions Starter Pack', 75000.00, 'Qualification', 25.0, '2024-10-01', '2024-02-20 09:15:00', 'REP002', 'SMB Sales', 'Referral'),
('HSD003', 'HSC003', 'Startup.io Growth Package', 200000.00, 'Negotiation', 80.0, '2024-09-30', '2024-03-10 16:20:00', 'REP001', 'Enterprise Sales', 'LinkedIn'),
('HSD004', 'HSC004', 'Enterprise Corp Full Suite', 300000.00, 'Closed Won', 100.0, '2024-08-15', '2024-01-05 11:00:00', 'REP003', 'Enterprise Sales', 'Trade Show'),
('HSD005', 'HSC005', 'Growth Dynamics Basic', 50000.00, 'Discovery', 15.0, '2024-11-15', '2024-04-15 13:45:00', 'REP002', 'SMB Sales', 'Cold Call'),
('HSD006', 'HSC006', 'Scale Systems Professional', 180000.00, 'Proposal', 70.0, '2024-09-20', '2024-02-28 08:30:00', 'REP001', 'Enterprise Sales', 'Partner'),
('HSD007', 'HSC007', 'Future Tech Advanced', 250000.00, 'Negotiation', 85.0, '2024-10-10', '2024-03-20 14:15:00', 'REP003', 'Enterprise Sales', 'Website'),
('HSD008', 'HSC008', 'Digital First Marketing Suite', 90000.00, 'Qualification', 30.0, '2024-10-30', '2024-05-10 10:45:00', 'REP002', 'SMB Sales', 'Social Media'),
('HSD009', 'HSC009', 'Cloud Solutions Integration', 120000.00, 'Discovery', 40.0, '2024-11-01', '2024-04-05 12:20:00', 'REP001', 'Enterprise Sales', 'Webinar'),
('HSD010', 'HSC010', 'AI Innovations Premium', 400000.00, 'Closed Won', 100.0, '2024-07-30', '2024-01-25 15:30:00', 'REP003', 'Enterprise Sales', 'Conference');

-- =====================================================
-- 4. INSERT SAMPLE DATA - DISCO LMS
-- =====================================================

-- Sample Disco Courses
INSERT INTO BRONZE.DISCO_COURSES VALUES
('DC001', 'Sales Fundamentals', 'Complete guide to modern sales techniques and methodologies', 'INST001', 'Dr. Sarah Mitchell', 'Sales Training', 8.0, 'Beginner', '2024-01-01 00:00:00', 'Active'),
('DC002', 'Advanced CRM Management', 'Master HubSpot and other CRM platforms for maximum efficiency', 'INST002', 'Mark Thompson', 'Technology', 12.0, 'Intermediate', '2024-01-15 00:00:00', 'Active'),
('DC003', 'Data Analytics for Sales', 'Learn to analyze sales data and create actionable insights', 'INST003', 'Dr. Lisa Wang', 'Analytics', 16.0, 'Advanced', '2024-02-01 00:00:00', 'Active'),
('DC004', 'Customer Success Strategies', 'Build lasting relationships and drive customer retention', 'INST001', 'Dr. Sarah Mitchell', 'Customer Success', 10.0, 'Intermediate', '2024-02-15 00:00:00', 'Active'),
('DC005', 'Leadership in Sales', 'Develop leadership skills for sales team management', 'INST004', 'James Rodriguez', 'Leadership', 14.0, 'Advanced', '2024-03-01 00:00:00', 'Active'),
('DC006', 'Digital Marketing Basics', 'Introduction to digital marketing and lead generation', 'INST005', 'Emily Chen', 'Marketing', 6.0, 'Beginner', '2024-03-15 00:00:00', 'Active'),
('DC007', 'Negotiation Mastery', 'Advanced negotiation techniques for closing deals', 'INST002', 'Mark Thompson', 'Sales Training', 8.0, 'Advanced', '2024-04-01 00:00:00', 'Active'),
('DC008', 'Product Knowledge Deep Dive', 'Comprehensive understanding of our product suite', 'INST006', 'Technical Team', 'Product Training', 20.0, 'Intermediate', '2024-04-15 00:00:00', 'Active'),
('DC009', 'Communication Excellence', 'Improve verbal and written communication skills', 'INST007', 'Rachel Green', 'Soft Skills', 4.0, 'Beginner', '2024-05-01 00:00:00', 'Active'),
('DC010', 'AI Tools for Sales', 'Leverage AI and automation in your sales process', 'INST003', 'Dr. Lisa Wang', 'Technology', 6.0, 'Intermediate', '2024-05-15 00:00:00', 'Active');

-- Sample Disco Users
INSERT INTO BRONZE.DISCO_USERS VALUES
('DU001', 'john.sales@company.com', 'John', 'Parker', 'Sales', 'Sales Representative', 'DU020', '2023-06-15', 'Active', '2024-08-22 09:30:00'),
('DU002', 'sarah.lead@company.com', 'Sarah', 'Williams', 'Sales', 'Sales Manager', 'DU021', '2023-03-10', 'Active', '2024-08-22 08:45:00'),
('DU003', 'mike.rep@company.com', 'Mike', 'Johnson', 'Sales', 'Sales Representative', 'DU020', '2023-09-20', 'Active', '2024-08-21 16:20:00'),
('DU004', 'lisa.success@company.com', 'Lisa', 'Davis', 'Customer Success', 'CS Manager', 'DU022', '2023-01-05', 'Active', '2024-08-22 07:15:00'),
('DU005', 'david.senior@company.com', 'David', 'Brown', 'Sales', 'Senior Sales Rep', 'DU021', '2022-11-15', 'Active', '2024-08-21 18:30:00'),
('DU006', 'emma.new@company.com', 'Emma', 'Wilson', 'Sales', 'Sales Representative', 'DU020', '2024-02-01', 'Active', '2024-08-22 10:45:00'),
('DU007', 'alex.expert@company.com', 'Alex', 'Garcia', 'Sales', 'Sales Specialist', 'DU021', '2023-07-30', 'Active', '2024-08-21 14:20:00'),
('DU008', 'rachel.marketing@company.com', 'Rachel', 'Lee', 'Marketing', 'Marketing Specialist', 'DU023', '2023-05-20', 'Active', '2024-08-22 11:10:00'),
('DU009', 'tom.support@company.com', 'Tom', 'Anderson', 'Customer Success', 'Support Specialist', 'DU022', '2023-12-10', 'Active', '2024-08-21 15:45:00'),
('DU010', 'maria.director@company.com', 'Maria', 'Rodriguez', 'Sales', 'Sales Director', 'DU024', '2022-08-15', 'Active', '2024-08-22 06:30:00');

-- Sample Disco Enrollments
INSERT INTO BRONZE.DISCO_ENROLLMENTS VALUES
('DE001', 'DU001', 'DC001', '2024-06-01 09:00:00', '2024-06-15 17:30:00', 100.0, 92.5, 'Completed', 8.5),
('DE002', 'DU001', 'DC002', '2024-07-01 09:00:00', NULL, 75.0, NULL, 'In Progress', 9.0),
('DE003', 'DU002', 'DC005', '2024-05-15 09:00:00', '2024-06-10 16:45:00', 100.0, 88.0, 'Completed', 14.2),
('DE004', 'DU003', 'DC001', '2024-06-15 09:00:00', '2024-07-01 18:00:00', 100.0, 85.5, 'Completed', 8.8),
('DE005', 'DU004', 'DC004', '2024-05-01 09:00:00', '2024-05-20 17:15:00', 100.0, 94.0, 'Completed', 10.5),
('DE006', 'DU005', 'DC003', '2024-04-01 09:00:00', '2024-05-15 19:30:00', 100.0, 91.5, 'Completed', 16.8),
('DE007', 'DU006', 'DC001', '2024-07-15 09:00:00', NULL, 45.0, NULL, 'In Progress', 3.6),
('DE008', 'DU007', 'DC007', '2024-06-01 09:00:00', '2024-06-20 16:20:00', 100.0, 89.0, 'Completed', 8.3),
('DE009', 'DU008', 'DC006', '2024-07-01 09:00:00', '2024-07-10 15:45:00', 100.0, 87.5, 'Completed', 6.2),
('DE010', 'DU009', 'DC004', '2024-06-15 09:00:00', NULL, 80.0, NULL, 'In Progress', 8.0),
('DE011', 'DU010', 'DC005', '2024-04-15 09:00:00', '2024-05-30 18:45:00', 100.0, 96.0, 'Completed', 14.5),
('DE012', 'DU002', 'DC003', '2024-07-01 09:00:00', NULL, 60.0, NULL, 'In Progress', 9.6),
('DE013', 'DU005', 'DC007', '2024-07-15 09:00:00', '2024-08-05 17:30:00', 100.0, 93.5, 'Completed', 8.7),
('DE014', 'DU001', 'DC009', '2024-08-01 09:00:00', '2024-08-05 16:00:00', 100.0, 90.0, 'Completed', 4.2),
('DE015', 'DU003', 'DC010', '2024-08-10 09:00:00', NULL, 30.0, NULL, 'In Progress', 1.8);

-- =====================================================
-- 5. SILVER LAYER - CLEANED AND TRANSFORMED DATA
-- =====================================================

-- Create Silver layer views for cleaned data
CREATE OR REPLACE VIEW SILVER.CLEAN_CONTACTS AS
SELECT 
    contact_id,
    LOWER(TRIM(email)) as email,
    INITCAP(TRIM(first_name)) as first_name,
    INITCAP(TRIM(last_name)) as last_name,
    TRIM(company) as company,
    TRIM(job_title) as job_title,
    phone,
    lead_status,
    lifecycle_stage,
    created_date,
    last_modified_date,
    deal_amount,
    deal_stage,
    source
FROM BRONZE.HUBSPOT_CONTACTS
WHERE email IS NOT NULL;

CREATE OR REPLACE VIEW SILVER.CLEAN_DEALS AS
SELECT 
    deal_id,
    contact_id,
    TRIM(deal_name) as deal_name,
    amount,
    stage,
    probability,
    close_date,
    created_date,
    owner_id,
    pipeline,
    source,
    CASE 
        WHEN stage = 'Closed Won' THEN 'Won'
        WHEN stage = 'Closed Lost' THEN 'Lost'
        ELSE 'Open'
    END as deal_status
FROM BRONZE.HUBSPOT_DEALS;

CREATE OR REPLACE VIEW SILVER.CLEAN_ENROLLMENTS AS
SELECT 
    e.enrollment_id,
    e.user_id,
    e.course_id,
    e.enrollment_date,
    e.completion_date,
    e.progress_percentage,
    e.final_score,
    e.status,
    e.time_spent_hours,
    c.course_name,
    c.category,
    c.difficulty_level,
    u.first_name,
    u.last_name,
    u.department,
    u.role
FROM BRONZE.DISCO_ENROLLMENTS e
JOIN BRONZE.DISCO_COURSES c ON e.course_id = c.course_id
JOIN BRONZE.DISCO_USERS u ON e.user_id = u.user_id;

-- =====================================================
-- 6. GOLD LAYER - BUSINESS-READY ANALYTICS
-- =====================================================

-- Sales Performance Metrics
CREATE OR REPLACE VIEW GOLD.SALES_METRICS AS
SELECT 
    DATE_TRUNC('month', created_date) as month,
    COUNT(*) as total_deals,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_deal_size,
    SUM(CASE WHEN deal_status = 'Won' THEN amount ELSE 0 END) as won_revenue,
    COUNT(CASE WHEN deal_status = 'Won' THEN 1 END) as won_deals,
    COUNT(CASE WHEN deal_status = 'Won' THEN 1 END) * 100.0 / COUNT(*) as win_rate
FROM SILVER.CLEAN_DEALS
GROUP BY DATE_TRUNC('month', created_date)
ORDER BY month;

-- Learning Analytics Metrics
CREATE OR REPLACE VIEW GOLD.LEARNING_METRICS AS
SELECT 
    DATE_TRUNC('month', enrollment_date) as month,
    COUNT(*) as total_enrollments,
    COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_courses,
    COUNT(CASE WHEN status = 'Completed' THEN 1 END) * 100.0 / COUNT(*) as completion_rate,
    AVG(CASE WHEN status = 'Completed' THEN final_score END) as avg_score,
    AVG(time_spent_hours) as avg_time_spent
FROM SILVER.CLEAN_ENROLLMENTS
GROUP BY DATE_TRUNC('month', enrollment_date)
ORDER BY month;

-- Executive Dashboard KPIs
CREATE OR REPLACE VIEW GOLD.EXECUTIVE_KPIS AS
SELECT 
    'Current Month' as period,
    (SELECT SUM(amount) FROM SILVER.CLEAN_DEALS WHERE deal_status = 'Won' AND DATE_TRUNC('month', created_date) = DATE_TRUNC('month', CURRENT_DATE())) as monthly_revenue,
    (SELECT COUNT(*) FROM SILVER.CLEAN_DEALS WHERE deal_status = 'Open') as active_deals,
    (SELECT COUNT(CASE WHEN status = 'Completed' THEN 1 END) * 100.0 / COUNT(*) FROM SILVER.CLEAN_ENROLLMENTS WHERE DATE_TRUNC('month', enrollment_date) = DATE_TRUNC('month', CURRENT_DATE())) as training_completion_rate,
    (SELECT AVG(CASE WHEN status = 'Completed' THEN final_score END) FROM SILVER.CLEAN_ENROLLMENTS WHERE DATE_TRUNC('month', completion_date) = DATE_TRUNC('month', CURRENT_DATE())) as avg_training_score;

-- =====================================================
-- 7. GRANT PERMISSIONS
-- =====================================================

-- Grant usage on database and schemas
GRANT USAGE ON DATABASE OLYMPUS_ANALYTICS TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA OLYMPUS_ANALYTICS.BRONZE TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA OLYMPUS_ANALYTICS.SILVER TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA OLYMPUS_ANALYTICS.STAGING TO ROLE SYSADMIN;

-- Grant select permissions on all tables and views
GRANT SELECT ON ALL TABLES IN SCHEMA OLYMPUS_ANALYTICS.BRONZE TO ROLE SYSADMIN;
GRANT SELECT ON ALL VIEWS IN SCHEMA OLYMPUS_ANALYTICS.SILVER TO ROLE SYSADMIN;
GRANT SELECT ON ALL VIEWS IN SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE SYSADMIN;

-- Grant future permissions
GRANT SELECT ON FUTURE TABLES IN SCHEMA OLYMPUS_ANALYTICS.BRONZE TO ROLE SYSADMIN;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA OLYMPUS_ANALYTICS.SILVER TO ROLE SYSADMIN;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA OLYMPUS_ANALYTICS.GOLD TO ROLE SYSADMIN;

-- =====================================================
-- 8. VERIFICATION QUERIES
-- =====================================================

-- Verify data loading
SELECT 'HUBSPOT_CONTACTS' as table_name, COUNT(*) as record_count FROM BRONZE.HUBSPOT_CONTACTS
UNION ALL
SELECT 'HUBSPOT_DEALS' as table_name, COUNT(*) as record_count FROM BRONZE.HUBSPOT_DEALS
UNION ALL
SELECT 'DISCO_COURSES' as table_name, COUNT(*) as record_count FROM BRONZE.DISCO_COURSES
UNION ALL
SELECT 'DISCO_USERS' as table_name, COUNT(*) as record_count FROM BRONZE.DISCO_USERS
UNION ALL
SELECT 'DISCO_ENROLLMENTS' as table_name, COUNT(*) as record_count FROM BRONZE.DISCO_ENROLLMENTS;

-- Test Gold layer views
SELECT * FROM GOLD.EXECUTIVE_KPIS;
SELECT * FROM GOLD.SALES_METRICS LIMIT 5;
SELECT * FROM GOLD.LEARNING_METRICS LIMIT 5;

-- =====================================================
-- SETUP COMPLETE!
-- =====================================================
-- Your Olympus Analytics database is now ready.
-- You can now test the Streamlit application connection.
-- =====================================================
-- Complete Olympus Analytics Database Setup with Privilege Fixes
-- Execute this script as ACCOUNTADMIN or have an ACCOUNTADMIN run the privilege section

-- =====================================================
-- STEP 1: FIX PRIVILEGES (Run as ACCOUNTADMIN)
-- =====================================================

-- Switch to ACCOUNTADMIN role (required for granting privileges)
USE ROLE ACCOUNTADMIN;

-- Grant necessary privileges to SYSADMIN role
GRANT CREATE DATABASE ON ACCOUNT TO ROLE SYSADMIN;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE SYSADMIN;
GRANT USAGE ON WAREHOUSE XS_WAREHOUSE TO ROLE SYSADMIN;
GRANT OPERATE ON WAREHOUSE XS_WAREHOUSE TO ROLE SYSADMIN;

-- =====================================================
-- STEP 2: DATABASE SETUP (Can run as SYSADMIN after privileges are fixed)
-- =====================================================

-- Switch to SYSADMIN role
USE ROLE SYSADMIN;
USE WAREHOUSE XS_WAREHOUSE;

-- Create the main database
CREATE DATABASE IF NOT EXISTS OLYMPUS_ANALYTICS;
USE DATABASE OLYMPUS_ANALYTICS;

-- Create schemas following medallion architecture
CREATE SCHEMA IF NOT EXISTS BRONZE;   -- Raw data layer
CREATE SCHEMA IF NOT EXISTS SILVER;   -- Cleaned and transformed data
CREATE SCHEMA IF NOT EXISTS GOLD;     -- Business-ready analytics
CREATE SCHEMA IF NOT EXISTS STAGING;  -- Temporary staging area

-- =====================================================
-- BRONZE LAYER: Raw Data Tables
-- =====================================================

-- HubSpot CRM Raw Data
CREATE OR REPLACE TABLE BRONZE.HUBSPOT_CONTACTS (
    contact_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company VARCHAR(255),
    job_title VARCHAR(255),
    phone VARCHAR(50),
    lead_source VARCHAR(100),
    lifecycle_stage VARCHAR(50),
    created_date TIMESTAMP,
    last_modified_date TIMESTAMP,
    annual_revenue NUMBER(15,2),
    industry VARCHAR(100),
    country VARCHAR(100),
    state VARCHAR(100)
);

CREATE OR REPLACE TABLE BRONZE.HUBSPOT_DEALS (
    deal_id VARCHAR(50) PRIMARY KEY,
    contact_id VARCHAR(50),
    deal_name VARCHAR(255),
    deal_stage VARCHAR(100),
    deal_amount NUMBER(15,2),
    close_date DATE,
    created_date TIMESTAMP,
    last_modified_date TIMESTAMP,
    deal_owner VARCHAR(100),
    deal_source VARCHAR(100),
    probability NUMBER(3,0),
    deal_type VARCHAR(50)
);

-- Disco LMS Raw Data
CREATE OR REPLACE TABLE BRONZE.DISCO_COURSES (
    course_id VARCHAR(50) PRIMARY KEY,
    course_name VARCHAR(255),
    course_description TEXT,
    instructor_name VARCHAR(100),
    course_category VARCHAR(100),
    duration_hours NUMBER(5,2),
    difficulty_level VARCHAR(50),
    created_date TIMESTAMP,
    last_updated TIMESTAMP,
    is_active BOOLEAN,
    course_price NUMBER(10,2)
);

CREATE OR REPLACE TABLE BRONZE.DISCO_ENROLLMENTS (
    enrollment_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    course_id VARCHAR(50),
    enrollment_date TIMESTAMP,
    completion_date TIMESTAMP,
    progress_percentage NUMBER(5,2),
    final_score NUMBER(5,2),
    status VARCHAR(50),
    time_spent_hours NUMBER(8,2),
    last_accessed TIMESTAMP
);

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert sample HubSpot contacts
INSERT INTO BRONZE.HUBSPOT_CONTACTS VALUES
('C001', 'john.doe@techcorp.com', 'John', 'Doe', 'TechCorp Inc', 'CTO', '+1-555-0101', 'Website', 'Customer', '2024-01-15 10:30:00', '2024-08-20 14:22:00', 2500000, 'Technology', 'USA', 'California'),
('C002', 'sarah.wilson@innovate.com', 'Sarah', 'Wilson', 'Innovate Solutions', 'VP Sales', '+1-555-0102', 'Referral', 'Opportunity', '2024-02-20 09:15:00', '2024-08-21 11:45:00', 1800000, 'Consulting', 'USA', 'New York'),
('C003', 'mike.chen@dataflow.io', 'Mike', 'Chen', 'DataFlow Analytics', 'Data Scientist', '+1-555-0103', 'LinkedIn', 'Lead', '2024-03-10 16:20:00', '2024-08-22 09:30:00', 950000, 'Analytics', 'USA', 'Texas'),
('C004', 'emma.garcia@cloudnine.com', 'Emma', 'Garcia', 'CloudNine Systems', 'Product Manager', '+1-555-0104', 'Trade Show', 'Customer', '2024-01-25 11:45:00', '2024-08-20 16:10:00', 3200000, 'Cloud Services', 'USA', 'Washington'),
('C005', 'alex.kumar@fintech.co', 'Alex', 'Kumar', 'FinTech Innovations', 'CEO', '+1-555-0105', 'Cold Call', 'Opportunity', '2024-04-05 14:30:00', '2024-08-21 13:20:00', 4100000, 'Financial Services', 'USA', 'Illinois'),
('C006', 'lisa.brown@retail.com', 'Lisa', 'Brown', 'Retail Dynamics', 'CMO', '+1-555-0106', 'Website', 'Lead', '2024-05-12 08:45:00', '2024-08-22 10:15:00', 750000, 'Retail', 'USA', 'Florida'),
('C007', 'david.lee@healthcare.org', 'David', 'Lee', 'HealthCare Plus', 'Director IT', '+1-555-0107', 'Partner', 'Customer', '2024-02-28 13:20:00', '2024-08-20 15:40:00', 1600000, 'Healthcare', 'USA', 'Massachusetts'),
('C008', 'maria.rodriguez@edu.com', 'Maria', 'Rodriguez', 'EduTech Solutions', 'Head of Learning', '+1-555-0108', 'Webinar', 'Opportunity', '2024-06-18 10:10:00', '2024-08-21 12:30:00', 1200000, 'Education', 'USA', 'Colorado'),
('C009', 'james.taylor@manufacturing.com', 'James', 'Taylor', 'Manufacturing Pro', 'Operations Manager', '+1-555-0109', 'Referral', 'Lead', '2024-07-02 15:55:00', '2024-08-22 08:45:00', 2800000, 'Manufacturing', 'USA', 'Michigan'),
('C010', 'anna.white@logistics.net', 'Anna', 'White', 'Logistics Network', 'Supply Chain Director', '+1-555-0110', 'LinkedIn', 'Customer', '2024-03-22 12:40:00', '2024-08-20 17:25:00', 2100000, 'Logistics', 'USA', 'Georgia');

-- Insert sample HubSpot deals
INSERT INTO BRONZE.HUBSPOT_DEALS VALUES
('D001', 'C001', 'TechCorp Enterprise License', 'Closed Won', 450000, '2024-08-15', '2024-01-20 10:30:00', '2024-08-15 16:45:00', 'Sarah Johnson', 'Inbound', 100, 'New Business'),
('D002', 'C002', 'Innovate Solutions Consulting', 'Negotiation', 280000, '2024-09-30', '2024-02-25 09:15:00', '2024-08-21 14:20:00', 'Mike Davis', 'Referral', 75, 'Expansion'),
('D003', 'C003', 'DataFlow Analytics Platform', 'Proposal', 125000, '2024-10-15', '2024-03-15 16:20:00', '2024-08-22 11:30:00', 'Jennifer Lee', 'Inbound', 60, 'New Business'),
('D004', 'C004', 'CloudNine Integration Project', 'Closed Won', 680000, '2024-07-20', '2024-01-30 11:45:00', '2024-07-20 13:15:00', 'Robert Chen', 'Partner', 100, 'New Business'),
('D005', 'C005', 'FinTech Security Suite', 'Decision Maker Bought-In', 520000, '2024-09-15', '2024-04-10 14:30:00', '2024-08-21 15:45:00', 'Lisa Wang', 'Cold Outreach', 85, 'New Business'),
('D006', 'C006', 'Retail Analytics Dashboard', 'Qualified to Buy', 95000, '2024-11-01', '2024-05-17 08:45:00', '2024-08-22 09:20:00', 'David Kim', 'Inbound', 45, 'New Business'),
('D007', 'C007', 'HealthCare Compliance Module', 'Closed Won', 320000, '2024-06-30', '2024-03-05 13:20:00', '2024-06-30 17:30:00', 'Emily Rodriguez', 'Partner', 100, 'Expansion'),
('D008', 'C008', 'EduTech Learning Platform', 'Presentation Scheduled', 180000, '2024-10-30', '2024-06-23 10:10:00', '2024-08-21 16:10:00', 'Alex Thompson', 'Webinar', 70, 'New Business'),
('D009', 'C009', 'Manufacturing Optimization', 'Appointment Scheduled', 420000, '2024-11-15', '2024-07-07 15:55:00', '2024-08-22 12:45:00', 'Maria Garcia', 'Referral', 40, 'New Business'),
('D010', 'C010', 'Logistics Tracking System', 'Closed Won', 350000, '2024-08-10', '2024-03-27 12:40:00', '2024-08-10 14:20:00', 'James Wilson', 'Inbound', 100, 'Expansion');

-- Insert sample Disco courses
INSERT INTO BRONZE.DISCO_COURSES VALUES
('COURSE001', 'Data Analytics Fundamentals', 'Comprehensive introduction to data analytics concepts and tools', 'Dr. Sarah Mitchell', 'Data Science', 40.5, 'Beginner', '2024-01-10 09:00:00', '2024-08-15 14:30:00', TRUE, 299.99),
('COURSE002', 'Advanced Python Programming', 'Deep dive into Python programming for data science and automation', 'Prof. Michael Chen', 'Programming', 60.0, 'Advanced', '2024-01-15 10:30:00', '2024-08-20 16:45:00', TRUE, 449.99),
('COURSE003', 'Machine Learning Essentials', 'Introduction to machine learning algorithms and applications', 'Dr. Emily Rodriguez', 'AI/ML', 55.5, 'Intermediate', '2024-02-01 11:15:00', '2024-08-18 13:20:00', TRUE, 399.99),
('COURSE004', 'Business Intelligence with Tableau', 'Creating powerful visualizations and dashboards with Tableau', 'Jennifer Lee', 'Business Intelligence', 35.0, 'Intermediate', '2024-02-10 14:20:00', '2024-08-22 10:15:00', TRUE, 349.99),
('COURSE005', 'SQL for Data Analysis', 'Mastering SQL for data querying and analysis', 'Robert Kim', 'Database', 45.0, 'Beginner', '2024-01-20 08:45:00', '2024-08-19 15:30:00', TRUE, 279.99),
('COURSE006', 'Cloud Computing with AWS', 'Introduction to Amazon Web Services and cloud architecture', 'Lisa Wang', 'Cloud Computing', 50.0, 'Intermediate', '2024-02-15 13:30:00', '2024-08-21 12:45:00', TRUE, 429.99),
('COURSE007', 'Project Management Fundamentals', 'Essential project management skills and methodologies', 'David Thompson', 'Management', 30.0, 'Beginner', '2024-01-25 16:00:00', '2024-08-17 09:20:00', TRUE, 249.99),
('COURSE008', 'Cybersecurity Basics', 'Introduction to cybersecurity principles and best practices', 'Maria Garcia', 'Security', 42.5, 'Beginner', '2024-02-05 12:15:00', '2024-08-20 14:10:00', TRUE, 329.99),
('COURSE009', 'Digital Marketing Analytics', 'Using data analytics for digital marketing optimization', 'Alex Johnson', 'Marketing', 38.0, 'Intermediate', '2024-02-20 10:45:00', '2024-08-16 11:30:00', TRUE, 319.99),
('COURSE010', 'Leadership in the Digital Age', 'Modern leadership strategies for digital transformation', 'Dr. Anna Wilson', 'Leadership', 25.5, 'Advanced', '2024-01-30 15:20:00', '2024-08-14 16:50:00', TRUE, 379.99);

-- Insert sample Disco enrollments
INSERT INTO BRONZE.DISCO_ENROLLMENTS VALUES
('E001', 'U001', 'COURSE001', '2024-03-01 09:30:00', '2024-04-15 16:45:00', 100.0, 92.5, 'Completed', 42.3, '2024-04-15 16:45:00'),
('E002', 'U002', 'COURSE002', '2024-03-05 10:15:00', NULL, 75.0, NULL, 'In Progress', 45.2, '2024-08-22 14:20:00'),
('E003', 'U003', 'COURSE003', '2024-03-10 11:20:00', '2024-05-20 13:30:00', 100.0, 88.7, 'Completed', 58.1, '2024-05-20 13:30:00'),
('E004', 'U004', 'COURSE004', '2024-03-15 14:45:00', '2024-04-30 17:20:00', 100.0, 95.2, 'Completed', 36.8, '2024-04-30 17:20:00'),
('E005', 'U005', 'COURSE005', '2024-03-20 08:30:00', NULL, 60.0, NULL, 'In Progress', 27.5, '2024-08-21 16:10:00'),
('E006', 'U006', 'COURSE006', '2024-03-25 12:10:00', '2024-06-10 15:45:00', 100.0, 91.3, 'Completed', 52.7, '2024-06-10 15:45:00'),
('E007', 'U007', 'COURSE007', '2024-04-01 16:30:00', '2024-04-25 12:15:00', 100.0, 89.6, 'Completed', 31.2, '2024-04-25 12:15:00'),
('E008', 'U008', 'COURSE008', '2024-04-05 09:45:00', NULL, 45.0, NULL, 'In Progress', 19.1, '2024-08-20 11:30:00'),
('E009', 'U009', 'COURSE009', '2024-04-10 13:20:00', '2024-05-30 14:50:00', 100.0, 93.8, 'Completed', 39.4, '2024-05-30 14:50:00'),
('E010', 'U010', 'COURSE010', '2024-04-15 11:00:00', '2024-05-05 16:30:00', 100.0, 96.1, 'Completed', 26.8, '2024-05-05 16:30:00'),
('E011', 'U001', 'COURSE003', '2024-05-01 10:30:00', NULL, 30.0, NULL, 'In Progress', 16.7, '2024-08-22 09:45:00'),
('E012', 'U002', 'COURSE005', '2024-05-10 14:15:00', '2024-06-25 17:40:00', 100.0, 87.4, 'Completed', 46.3, '2024-06-25 17:40:00'),
('E013', 'U003', 'COURSE007', '2024-05-15 09:20:00', '2024-06-05 13:25:00', 100.0, 94.7, 'Completed', 32.1, '2024-06-05 13:25:00'),
('E014', 'U004', 'COURSE009', '2024-05-20 15:45:00', NULL, 80.0, NULL, 'In Progress', 30.4, '2024-08-21 12:20:00'),
('E015', 'U005', 'COURSE001', '2024-06-01 11:30:00', '2024-07-20 16:15:00', 100.0, 90.2, 'Completed', 41.8, '2024-07-20 16:15:00');

-- =====================================================
-- SILVER LAYER: Cleaned and Transformed Views
-- =====================================================

-- Cleaned contacts view
CREATE OR REPLACE VIEW SILVER.CONTACTS_CLEAN AS
SELECT 
    contact_id,
    LOWER(email) as email,
    INITCAP(first_name) as first_name,
    INITCAP(last_name) as last_name,
    CONCAT(INITCAP(first_name), ' ', INITCAP(last_name)) as full_name,
    company,
    job_title,
    phone,
    lead_source,
    lifecycle_stage,
    created_date,
    last_modified_date,
    annual_revenue,
    industry,
    country,
    state,
    CASE 
        WHEN annual_revenue >= 5000000 THEN 'Enterprise'
        WHEN annual_revenue >= 1000000 THEN 'Mid-Market'
        WHEN annual_revenue >= 100000 THEN 'SMB'
        ELSE 'Startup'
    END as company_size_segment
FROM BRONZE.HUBSPOT_CONTACTS;

-- Deals with contact information
CREATE OR REPLACE VIEW SILVER.DEALS_ENRICHED AS
SELECT 
    d.deal_id,
    d.contact_id,
    c.full_name as contact_name,
    c.company,
    c.company_size_segment,
    d.deal_name,
    d.deal_stage,
    d.deal_amount,
    d.close_date,
    d.created_date,
    d.last_modified_date,
    d.deal_owner,
    d.deal_source,
    d.probability,
    d.deal_type,
    CASE 
        WHEN d.deal_stage = 'Closed Won' THEN 'Won'
        WHEN d.deal_stage = 'Closed Lost' THEN 'Lost'
        ELSE 'Open'
    END as deal_status,
    DATEDIFF('day', d.created_date, COALESCE(d.close_date, CURRENT_DATE())) as days_in_pipeline
FROM BRONZE.HUBSPOT_DEALS d
JOIN SILVER.CONTACTS_CLEAN c ON d.contact_id = c.contact_id;

-- Course performance metrics
CREATE OR REPLACE VIEW SILVER.COURSE_PERFORMANCE AS
SELECT 
    c.course_id,
    c.course_name,
    c.instructor_name,
    c.course_category,
    c.difficulty_level,
    c.duration_hours,
    c.course_price,
    COUNT(e.enrollment_id) as total_enrollments,
    COUNT(CASE WHEN e.status = 'Completed' THEN 1 END) as completed_enrollments,
    COUNT(CASE WHEN e.status = 'In Progress' THEN 1 END) as active_enrollments,
    ROUND(COUNT(CASE WHEN e.status = 'Completed' THEN 1 END) * 100.0 / NULLIF(COUNT(e.enrollment_id), 0), 2) as completion_rate,
    ROUND(AVG(CASE WHEN e.status = 'Completed' THEN e.final_score END), 2) as avg_final_score,
    ROUND(AVG(e.time_spent_hours), 2) as avg_time_spent,
    SUM(CASE WHEN e.status = 'Completed' THEN c.course_price ELSE 0 END) as revenue_generated
FROM BRONZE.DISCO_COURSES c
LEFT JOIN BRONZE.DISCO_ENROLLMENTS e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_name, c.instructor_name, c.course_category, 
         c.difficulty_level, c.duration_hours, c.course_price;

-- =====================================================
-- GOLD LAYER: Business-Ready Analytics
-- =====================================================

-- Executive KPIs
CREATE OR REPLACE VIEW GOLD.EXECUTIVE_KPIS AS
SELECT 
    -- Sales KPIs
    (SELECT COUNT(*) FROM SILVER.DEALS_ENRICHED WHERE deal_status = 'Won') as deals_won,
    (SELECT SUM(deal_amount) FROM SILVER.DEALS_ENRICHED WHERE deal_status = 'Won') as total_revenue,
    (SELECT COUNT(*) FROM SILVER.DEALS_ENRICHED WHERE deal_status = 'Open') as active_deals,
    (SELECT SUM(deal_amount) FROM SILVER.DEALS_ENRICHED WHERE deal_status = 'Open') as pipeline_value,
    (SELECT ROUND(AVG(deal_amount), 2) FROM SILVER.DEALS_ENRICHED WHERE deal_status = 'Won') as avg_deal_size,
    
    -- Learning KPIs
    (SELECT COUNT(*) FROM BRONZE.DISCO_COURSES WHERE is_active = TRUE) as active_courses,
    (SELECT COUNT(*) FROM BRONZE.DISCO_ENROLLMENTS) as total_enrollments,
    (SELECT COUNT(*) FROM BRONZE.DISCO_ENROLLMENTS WHERE status = 'Completed') as completed_enrollments,
    (SELECT ROUND(COUNT(CASE WHEN status = 'Completed' THEN 1 END) * 100.0 / COUNT(*), 2) 
     FROM BRONZE.DISCO_ENROLLMENTS) as overall_completion_rate,
    (SELECT ROUND(AVG(final_score), 2) FROM BRONZE.DISCO_ENROLLMENTS WHERE status = 'Completed') as avg_course_score;

-- Monthly revenue trend
CREATE OR REPLACE VIEW GOLD.MONTHLY_REVENUE AS
SELECT 
    DATE_TRUNC('month', close_date) as month,
    COUNT(*) as deals_closed,
    SUM(deal_amount) as revenue,
    ROUND(AVG(deal_amount), 2) as avg_deal_size
FROM SILVER.DEALS_ENRICHED 
WHERE deal_status = 'Won'
GROUP BY DATE_TRUNC('month', close_date)
ORDER BY month;

-- Sales pipeline by stage
CREATE OR REPLACE VIEW GOLD.PIPELINE_BY_STAGE AS
SELECT 
    deal_stage,
    COUNT(*) as deal_count,
    SUM(deal_amount) as total_value,
    ROUND(AVG(deal_amount), 2) as avg_deal_value,
    ROUND(AVG(probability), 2) as avg_probability
FROM SILVER.DEALS_ENRICHED 
WHERE deal_status = 'Open'
GROUP BY deal_stage
ORDER BY total_value DESC;

-- Top performing courses
CREATE OR REPLACE VIEW GOLD.TOP_COURSES AS
SELECT 
    course_name,
    instructor_name,
    course_category,
    total_enrollments,
    completion_rate,
    avg_final_score,
    revenue_generated
FROM SILVER.COURSE_PERFORMANCE
WHERE total_enrollments > 0
ORDER BY completion_rate DESC, total_enrollments DESC;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify data loading
SELECT 'HUBSPOT_CONTACTS' as table_name, COUNT(*) as record_count FROM BRONZE.HUBSPOT_CONTACTS
UNION ALL
SELECT 'HUBSPOT_DEALS' as table_name, COUNT(*) as record_count FROM BRONZE.HUBSPOT_DEALS
UNION ALL
SELECT 'DISCO_COURSES' as table_name, COUNT(*) as record_count FROM BRONZE.DISCO_COURSES
UNION ALL
SELECT 'DISCO_ENROLLMENTS' as table_name, COUNT(*) as record_count FROM BRONZE.DISCO_ENROLLMENTS;

-- Test key business metrics
SELECT * FROM GOLD.EXECUTIVE_KPIS;

-- Show sample data from each layer
SELECT 'Bronze Layer Sample' as layer, contact_id, email, company FROM BRONZE.HUBSPOT_CONTACTS LIMIT 3;
SELECT 'Silver Layer Sample' as layer, contact_id, full_name, company_size_segment FROM SILVER.CONTACTS_CLEAN LIMIT 3;
SELECT 'Gold Layer Sample' as layer, deals_won, total_revenue, overall_completion_rate FROM GOLD.EXECUTIVE_KPIS;

SELECT 'Setup Complete!' as status, CURRENT_TIMESTAMP() as completed_at;
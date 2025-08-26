# Olympus Analytics dbt Project

A comprehensive data transformation project for Olympus Analytics, integrating HubSpot CRM and Disco LMS data into a unified analytics platform.

## Project Overview

This dbt project transforms raw data from HubSpot CRM and Disco LMS into business-ready analytics tables following a medallion architecture (Bronze → Silver → Gold). The project enables comprehensive reporting on sales performance, learning analytics, and user engagement.

## Architecture

### Data Flow
```
Raw Data Sources → Bronze Layer → Silver Layer → Gold Layer → Analytics Dashboard
```

### Layer Descriptions

#### Bronze Layer (Staging)
- **Purpose**: Raw data ingestion with basic cleaning and validation
- **Models**: `stg_*` models
- **Schema**: `BRONZE`
- **Materialization**: Tables

#### Silver Layer (Integration)
- **Purpose**: Data integration, enrichment, and business logic application
- **Models**: `int_*` models
- **Schema**: `SILVER`
- **Materialization**: Tables

#### Gold Layer (Marts)
- **Purpose**: Business-ready dimensional models for analytics
- **Models**: `dim_*` and `fact_*` models
- **Schema**: `GOLD`
- **Materialization**: Tables

## Data Sources

### HubSpot CRM
- **Contacts**: Customer and prospect information
- **Companies**: Organization details and firmographics
- **Deals**: Sales opportunities and pipeline data

### Disco LMS
- **Users**: Learning platform users and profiles
- **Courses**: Training content and metadata
- **Enrollments**: Learning progress and completion data

## Models

### Bronze Layer Models

| Model | Description | Source |
|-------|-------------|--------|
| `stg_hubspot_contacts` | Staged HubSpot contacts | `raw.hubspot_contacts` |
| `stg_hubspot_companies` | Staged HubSpot companies | `raw.hubspot_companies` |
| `stg_hubspot_deals` | Staged HubSpot deals | `raw.hubspot_deals` |
| `stg_disco_users` | Staged Disco LMS users | `raw.disco_users` |
| `stg_disco_courses` | Staged Disco LMS courses | `raw.disco_courses` |
| `stg_disco_enrollments` | Staged Disco LMS enrollments | `raw.disco_enrollments` |

### Silver Layer Models

| Model | Description | Dependencies |
|-------|-------------|-------------|
| `int_users_unified` | Unified user data from HubSpot and Disco | `stg_hubspot_contacts`, `stg_disco_users` |
| `int_deals_enriched` | Enriched deals with company/contact info | `stg_hubspot_deals`, `stg_hubspot_companies`, `stg_hubspot_contacts` |
| `int_learning_analytics` | Enriched learning data with metrics | `stg_disco_enrollments`, `stg_disco_courses`, `stg_disco_users` |

### Gold Layer Models

| Model | Description | Type | Dependencies |
|-------|-------------|------|-------------|
| `dim_users` | User dimension table | Dimension | `int_users_unified` |
| `dim_courses` | Course dimension table | Dimension | `stg_disco_courses` |
| `fact_learning_analytics` | Learning analytics fact table | Fact | `int_learning_analytics` |
| `fact_sales_performance` | Sales performance fact table | Fact | `int_deals_enriched` |

## Key Features

### Data Quality
- Comprehensive data validation and testing
- Null value handling and data type casting
- Duplicate detection and resolution
- Business rule validation

### Business Logic
- User deduplication across systems
- Deal status standardization
- Learning progress categorization
- Performance tier classification
- Engagement level scoring

### Analytics Ready
- Pre-calculated KPIs and metrics
- Time-based dimensions for reporting
- Business-friendly categorizations
- Optimized for dashboard consumption

## Setup Instructions

### Prerequisites
- dbt Core 1.0+
- Snowflake account with appropriate permissions
- Access to HubSpot and Disco LMS data

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dbt_olympus_analytics
   ```

2. **Install dbt dependencies**
   ```bash
   dbt deps
   ```

3. **Configure profiles.yml**
   
   Copy the provided `profiles.yml` to your dbt profiles directory (`~/.dbt/`) and update with your Snowflake credentials:
   
   ```yaml
   olympus_analytics:
     target: dev
     outputs:
       dev:
         type: snowflake
         account: <your-account>
         user: <your-username>
         password: <your-password>
         # ... other configurations
   ```

4. **Set environment variables**
   ```bash
   export SNOWFLAKE_USER=<your-username>
   export SNOWFLAKE_PASSWORD=<your-password>
   export SNOWFLAKE_ACCOUNT=<your-account>
   export SNOWFLAKE_ROLE=<your-role>
   ```

5. **Test connection**
   ```bash
   dbt debug
   ```

### Running the Project

1. **Run all models**
   ```bash
   dbt run
   ```

2. **Run tests**
   ```bash
   dbt test
   ```

3. **Generate documentation**
   ```bash
   dbt docs generate
   dbt docs serve
   ```

4. **Run specific layers**
   ```bash
   # Bronze layer only
   dbt run --select tag:bronze
   
   # Silver layer only
   dbt run --select tag:silver
   
   # Gold layer only
   dbt run --select tag:gold
   ```

## Configuration

### Variables

The project uses the following variables (defined in `dbt_project.yml`):

- `start_date`: Start date for data processing (default: '2023-01-01')
- `end_date`: End date for data processing (default: '2025-12-31')

### Materialization Strategy

- **Bronze**: Tables (for data lineage and debugging)
- **Silver**: Tables (for performance and complex joins)
- **Gold**: Tables (for dashboard performance)

## Testing

The project includes comprehensive testing:

- **Source tests**: Validate raw data quality
- **Model tests**: Ensure transformation accuracy
- **Business logic tests**: Validate calculated fields
- **Referential integrity**: Check foreign key relationships

### Running Tests

```bash
# Run all tests
dbt test

# Run tests for specific models
dbt test --select dim_users

# Run only source tests
dbt test --select source:*
```

## Monitoring and Maintenance

### Performance Optimization
- Models are materialized as tables for optimal query performance
- Clustering keys are applied where appropriate
- Regular VACUUM and ANALYZE operations recommended

### Data Freshness
- Source data should be refreshed daily
- dbt models can be run incrementally for large datasets
- Monitor data quality metrics regularly

### Troubleshooting

1. **Connection Issues**
   - Verify Snowflake credentials
   - Check network connectivity
   - Validate warehouse permissions

2. **Model Failures**
   - Check dbt logs for detailed error messages
   - Validate source data availability
   - Review model dependencies

3. **Test Failures**
   - Investigate data quality issues
   - Review business logic assumptions
   - Update tests as business rules evolve

## Contributing

### Development Workflow

1. Create feature branch
2. Develop and test changes locally
3. Run full test suite
4. Submit pull request
5. Deploy to production after review

### Code Standards

- Follow dbt best practices
- Use descriptive model and column names
- Include comprehensive documentation
- Add appropriate tests for new models
- Follow SQL style guide

## Support

For questions or issues:

1. Check the documentation
2. Review existing issues
3. Contact the data team
4. Submit detailed bug reports

## License

This project is proprietary to Olympus Analytics.

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Maintained By**: Olympus Analytics Data Team
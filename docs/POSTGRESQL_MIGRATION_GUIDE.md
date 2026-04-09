# MySQL to PostgreSQL Migration Guide

**Status**: Migration configuration completed (April 9, 2026)  
**Target Deployment**: All environments (Dev, QA, Production)  
**Data Strategy**: Fresh start (no legacy data migration)

---

## Overview

This guide documents the complete migration from MySQL 8.0 to PostgreSQL 12+ for the Nursery Backend API. The schema has been updated, and all configurations are ready for deployment.

## What's Been Changed

### 1. **Prisma Schema** (`prisma/schema.prisma`)
- ✅ Updated datasource provider from `mysql` to `postgresql`
- ✅ Converted MySQL-specific types:
  - `@db.LongText` → `@db.Text` (for all string fields)
  - `@db.VarChar(255)` → Default string type
  - All 13 core models compatible with PostgreSQL
  - AI chat models (AIChatConversation, AIChatMessage) supported

### 2. **Docker Configuration** (`docker-compose.yml`)
- ✅ Replaced MySQL 8.0 with PostgreSQL 15 Alpine
- ✅ Updated service name: `mysql` → `postgresql`
- ✅ Updated environment variables for PostgreSQL
- ✅ Updated health check to use `pg_isready`
- ✅ Updated container name: `auth_mysql` → `auth_postgresql`
- ✅ Updated volume: `mysql_data` → `postgresql_data`

### 3. **Configuration Files**
- ✅ `config/dev_app_config.json`: Updated to `postgresql://postgres:postgres@localhost:5432/nursery_db`
- ✅ `config/qa_app_config.json`: Updated to `postgresql://postgres:postgres@localhost:5432/auth_db`
- ✅ `config/prod_app_config.json`: Set to use `${DATABASE_URL}` environment variable
- ✅ `prisma/migrations/migration_lock.toml`: Updated to `provider = "postgresql"`

### 4. **Code Base**
- ✅ No MySQL-specific SQL queries found (using Prisma ORM exclusively)
- ✅ All operations are database-agnostic
- ✅ No changes required to Python source code

---

## Pre-Deployment Checklist

Before deploying to any environment, verify:

- [ ] PostgreSQL server is version 12 or higher
- [ ] Database credentials are available
- [ ] Network connectivity to PostgreSQL host verified
- [ ] Backup of any existing data completed (if applicable)
- [ ] Environment variable `DATABASE_URL` is properly configured
- [ ] Application can connect to PostgreSQL and create tables

---

## Deployment Steps

### Phase 1: Development Environment

1. **Update environment variable**
   ```bash
   # Set DATABASE_URL for development
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/nursery_db"
   ```

2. **Run Prisma migrations**
   ```bash
   cd d:\My Projects\nursery-backend
   python -m prisma migrate deploy
   ```
   This will:
   - Connect to PostgreSQL
   - Create all database tables based on the schema
   - Apply all migrations in `prisma/migrations/`

3. **Initialize and seed database (optional)**
   ```bash
   python scripts/init_db.py
   python scripts/seed_db.py
   ```
   This will populate initial categories and products for testing.

4. **Run tests**
   ```bash
   # Run all tests against PostgreSQL
   pytest test_phase1_api.py -v
   pytest test_register.py -v
   pytest test_prisma_models.py -v
   ```

5. **Start application**
   ```bash
   python run_app.py
   ```

### Phase 2: QA Environment

Same as development, but with QA-specific credentials:
```bash
export DATABASE_URL="postgresql://[qa_username]:[qa_password]@[qa_host]:5432/[qa_database]"
python -m prisma migrate deploy
```

### Phase 3: Production Deployment

**Prerequisites:**
- PostgreSQL database provisioned on your hosting platform
- Credentials securely stored in environment variables
- Backup strategy in place
- Deployment window scheduled

**Steps:**

1. **Update production environment variables** on your hosting platform:
   ```
   DATABASE_URL=postgresql://[prod_user]:[prod_password]@[prod_host]:5432/[prod_database]
   ```

2. **Rebuild Docker image** (if using Docker in production):
   ```bash
   docker build -t nursery-backend:postgresql --build-arg ENVIRONMENT=production .
   ```

3. **Deploy updated application code** with the migrated schema

4. **Run migrations on production** (Critical - only do once):
   ```bash
   python -m prisma migrate deploy
   ```
   This will create all tables in the PostgreSQL database.

5. **Verify database connectivity**:
   ```bash
   # Run a health check endpoint
   curl http://localhost:8000/health
   ```

6. **Monitor application logs** for any errors related to database connections

7. **Run smoke tests** on key endpoints:
   - User registration/login
   - Product browsing
   - Cart operations
   - Order creation
   - Admin dashboard

---

## Database Connection Properties

### Development (Local)
```
Type: PostgreSQL
Host: localhost
Port: 5432
Database: nursery_db
User: postgres
Password: postgres
Connection String: postgresql://postgres:postgres@localhost:5432/nursery_db
```

### Docker Compose (If Using)
```
Type: PostgreSQL
Host: postgresql (container name)
Port: 5432
Database: nursery_db
User: postgres
Password: postgres
Connection String: postgresql://postgres:postgres@postgresql:5432/nursery_db
```

### Production
```
Type: PostgreSQL (12+)
Host: [Your hosting provider's PostgreSQL host]
Port: 5432 (default)
Database: [Your database name]
User: [Your username]
Password: [Your password - store securely]
Connection String: ${DATABASE_URL} (from environment variable)
```

---

## Prisma Migration Commands Reference

```bash
# Generate Prisma client
python -m prisma generate

# Deploy all pending migrations to database
python -m prisma migrate deploy

# Create a new migration (after schema changes)
python -m prisma migrate create --name [migration_name]

# View migration status
python -m prisma migrate status

# Reset database (⚠️ CAUTION: Deletes all data)
python -m prisma migrate reset
```

---

## Rollback Procedure

If issues occur and you need to revert:

1. **Stop the application**
2. **Keep backups** of the PostgreSQL database
3. **Revert code to MySQL version** (if necessary)
4. **Restore from backup** of the old database
5. **Check git history** for the previous MySQL configuration:
   ```bash
   git log --oneline -- prisma/schema.prisma
   git checkout [previous_commit] -- prisma/schema.prisma docker-compose.yml config/
   ```

---

## Troubleshooting

### Connection Refused
- Verify PostgreSQL service is running
- Check host, port, and credentials in DATABASE_URL
- Ensure network connectivity to PostgreSQL server

### Table Already Exists
- Verify the database is empty before first migration
- If tables exist, back up data and drop tables:
  ```bash
  python -m prisma migrate reset
  ```

### Authentication Failed
- Verify credentials in DATABASE_URL
- Ensure user has permissions to create tables
- Check PostgreSQL user role: `CREATE ROLE`, `CREATE DATABASE`, `CONNECT`

### Slow Performance After Migration
- Run table analysis: `ANALYZE;` in PostgreSQL
- Create indexes if needed (Prisma handles this via @@index)
- Monitor with your hosting provider's tools

### Migration Lock Error
- Verify `prisma/migrations/migration_lock.toml` shows `provider = "postgresql"`
- Reset migration lock if needed:
  ```bash
  rm prisma/migrations/migration_lock.toml
  python -m prisma migrate deploy
  ```

---

## Post-Migration Validation

After deployment, verify:

1. **Schema created**: Connect to PostgreSQL and check tables exist
   ```sql
   SELECT * FROM information_schema.tables WHERE table_schema = 'public';
   ```

2. **Models match**: Verify all 13 core models + AI chat models are present
3. **Indexes created**: Confirm indexes are built for performance
4. **Foreign keys**: Verify relationships between tables
5. **Test all API endpoints**: Especially auth, products, cart, orders
6. **Admin panel**: Test all admin operations
7. **AI chat**: If using AI features

---

## PostgreSQL Database Size Comparison

Expected database size (empty schema with indexes):
- **MySQL**: ~2-3 MB
- **PostgreSQL**: ~2-3 MB  
(Similar, minimal difference)

Expected with seed data (categories + products):
- Both: ~1-5 MB

---

## Hosting Platform Specific Notes

### Render PostgreSQL
- Connection string format: `postgresql://user:password@host/database`
- Port: 5432
- SSL may be required: Add `?sslmode=require` to connection string

### Railway PostgreSQL
- Connection string provided in environment
- Set as `DATABASE_URL` directly
- Automatically handles SSL

### AWS RDS PostgreSQL
- Security group must allow inbound port 5432
- Connection string: `postgresql://admin:password@database-name.region.rds.amazonaws.com:5432/dbname`
- Enable automated backups in AWS console

### Heroku PostgreSQL
- Automatically provides DATABASE_URL on app creation
- Use `heroku addons:create heroku-postgresql:standard-0` (if needed)

---

## Files Modified in This Migration

```
✅ prisma/schema.prisma
✅ prisma/migrations/migration_lock.toml
✅ docker-compose.yml
✅ config/dev_app_config.json
✅ config/qa_app_config.json
✅ config/prod_app_config.json (no change needed - uses env var)
```

## Files NOT Modified (No Changes Needed)

```
- src/plugins/database.py (ORM-agnostic)
- src/services/*.py (ORM-agnostic)
- src/core/*.py (ORM-agnostic)
- src/controllers/*.py (ORM-agnostic)
- scripts/init_db.py (ORM-agnostic)
- scripts/seed_db.py (ORM-agnostic)
- All other Python source files
```

---

## Support & Questions

For issues during deployment:
1. Check troubleshooting section above
2. Review Prisma PostgreSQL documentation: https://www.prisma.io/docs/orm/reference/prisma-schema-reference#postgresql
3. Check PostgreSQL logs on your server
4. Verify all environment variables are set correctly

---

**Migration Completed**: April 9, 2026  
**Prisma Version**: 0.11.0  
**Target PostgreSQL Version**: 12+  
**Status**: Ready for Deployment ✅

# PostgreSQL Migration Deployment Checklist

**Date**: April 9, 2026  
**Project**: Nursery Backend API  
**Target**: MySQL → PostgreSQL Migration  

---

## Pre-Deployment (Days Before)

### Infrastructure
- [ ] PostgreSQL 12+ database provisioned
- [ ] Network connectivity verified to PostgreSQL host
- [ ] Database user created with CREATE TABLE, CREATE DATABASE permissions
- [ ] Backup strategy confirmed (daily/hourly automated backups)
- [ ] Backup of existing MySQL database completed (if applicable)
- [ ] Database credentials stored securely (environment variables, secrets manager)

### Code & Configuration
- [ ] Latest code with PostgreSQL migration pulled/deployed
- [ ] All environment variables prepared (DATABASE_URL format verified)
- [ ] Dockerfile updated and tested locally
- [ ] Application can build successfully
- [ ] All tests pass against PostgreSQL in dev environment

### Team Communication
- [ ] Deployment window scheduled with stakeholders
- [ ] On-call support person assigned
- [ ] Rollback plan documented and reviewed
- [ ] Team members briefed on deployment steps

---

## Day of Deployment

### 1-2 Hours Before
- [ ] Verify PostgreSQL server is healthy and responding
- [ ] Test database connectivity with credentials:
  ```bash
  psql postgresql://user:password@host:5432/database
  ```
- [ ] Confirm backups are running
- [ ] Notify team: "Deployment starting in X minutes"
- [ ] Do final code review of migration changes

### 30 Minutes Before
- [ ] Take final backup of MySQL (if applicable)
- [ ] Prepare rollback command if needed
- [ ] Verify no other deployments are in progress
- [ ] Alert team: "Deployment starting in 30 minutes, API may be unavailable"

### Deployment Execution

#### Step 1: Stop application (if running)
```bash
# Stop current application
systemctl stop nursery-api
# OR
docker stop nursery-backend-app
```
- [ ] Application stopped successfully
- [ ] No requests being processed

#### Step 2: Update environment variables
```bash
# Set DATABASE_URL to PostgreSQL connection string
export DATABASE_URL="postgresql://user:password@host:5432/nursery_db"
```
- [ ] DATABASE_URL verified in environment
- [ ] Value formatted correctly: `postgresql://user:password@host:port/database`

#### Step 3: Deploy new application code
```bash
# Pull latest code
git pull origin main

# OR rebuild Docker image
docker build -t nursery-backend:postgresql .
```
- [ ] Code deployed successfully
- [ ] No build errors
- [ ] Dockerfile dependencies resolved

#### Step 4: Run Prisma migrations
```bash
# Navigate to app directory
cd /path/to/nursery-backend

# Run migrations to create schema
python -m prisma migrate deploy
```
- [ ] Migrations completed without errors
- [ ] All tables created in PostgreSQL
- [ ] Check PostgreSQL logs for any warnings

#### Step 5: Start application
```bash
# Start application
systemctl start nursery-api
# OR
docker run -d --name nursery-backend-app \
  -e DATABASE_URL=$DATABASE_URL \
  nursery-backend:postgresql
```
- [ ] Application started successfully
- [ ] No errors in application logs
- [ ] Application is listening on port 8000

---

## Post-Deployment Verification (Critical)

### Immediate Checks (0-5 minutes)
```bash
# Check application is responding
curl http://localhost:8000/health
```
- [ ] Health check returns 200 OK
- [ ] Application logs show "Connected to PostgreSQL"
- [ ] No database connection errors in logs

### Functional Tests (5-15 minutes)
```bash
# Run smoke tests
python -m pytest test_phase1_api.py::test_health_check -v
python -m pytest test_register.py::test_user_registration -v
python -m pytest test_phase1_api.py::test_product_list -v
```
- [ ] User registration works
- [ ] Product list retrieves data
- [ ] Cart operations function
- [ ] Order creation succeeds
- [ ] Admin endpoints accessible (if applicable)

### Database Validation (5 minutes)
```bash
# Connect to PostgreSQL and verify tables
psql postgresql://user:password@host:5432/database

# In psql:
\dt  # List all tables
SELECT COUNT(*) FROM users;  # Verify schema created
```
- [ ] All 13+ core tables present
- [ ] No errors in table relationships
- [ ] Indexes created successfully

### Performance Baseline (5 minutes)
- [ ] Response times normal (compare to MySQL if available)
- [ ] No slowdowns in API responses
- [ ] Database query performance acceptable
- [ ] Connection pool working properly

### Real-World Testing (15-30 minutes)
- [ ] End-to-end user flow tested (register → login → browse → cart → order)
- [ ] Admin operations tested (create product, update inventory, view logs)
- [ ] AI chat feature tested (if applicable)
- [ ] Real users can access application

---

## Monitoring for 24 Hours Post-Deployment

### First Hour
- [ ] Check error logs every 5-10 minutes
- [ ] Monitor database query performance
- [ ] Watch for connection pool issues
- [ ] Alert on any errors

### First 24 Hours
- [ ] Review application error logs for PostgreSQL-related issues
- [ ] Monitor database size and growth
- [ ] Check for memory leaks or unusual resource usage
- [ ] Gather feedback from users


### Metrics to Watch
- [ ] Database connection count (should be stable)
- [ ] Query response times (should match pre-migration baseline)
- [ ] Error rate (should be minimal, ideally 0%)
- [ ] CPU and memory usage on database server
- [ ] Replication lag (if using read replicas)

---

## If Issues Occur During Deployment

### Quick Diagnostics
```bash
# Check application logs
docker logs nursery-backend-app  # if Docker
journalctl -u nursery-api -n 50  # if systemd

# Test database connection
psql $DATABASE_URL

# Check migration status
python -m prisma migrate status
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Connection refused | Verify DATABASE_URL, check PostgreSQL service running |
| Authentication failed | Verify user credentials, check pg_hba.conf permissions |
| Table doesn't exist | Ensure `prisma migrate deploy` completed, check migration logs |
| Slow queries | Run `ANALYZE;` on database, check indexes created |
| Too many connections | Increase `max_connections` in PostgreSQL config |

### Decision Tree
```
Error in logs?
├─ YES → Check error type
│   ├─ Connection error → Verify DATABASE_URL and network
│   ├─ Permission error → Check PostgreSQL user permissions
│   ├─ Table error → Re-run prisma migrate deploy
│   └─ Other → Check PostgreSQL logs
└─ NO → Performance issue?
    ├─ YES → Run ANALYZE, check indexes
    └─ NO → Deployment successful!
```

### Rollback Steps (If critical issues found)
```bash
# 1. Stop current application
docker stop nursery-backend-app

# 2. Restore DATABASE_URL to MySQL (if needed)
export DATABASE_URL="mysql://root:root@localhost:3306/nursery_db"

# 3. Revert application code
git revert HEAD~1

# 4. Rebuild and restart with MySQL
docker build -t nursery-backend:mysql .
docker run -d -e DATABASE_URL=$DATABASE_URL nursery-backend:mysql

# 5. Verify rollback successful
curl http://localhost:8000/health
```
- [ ] Rollback completed
- [ ] Application responding
- [ ] Data remains intact

---

## Post-Rollback (If Rollback Necessary)

- [ ] Incident documented (what failed, at what step)
- [ ] Root cause analysis performed
- [ ] Issues fixed in development
- [ ] Deployment reattempted after fixes

---

## Success Criteria

✅ **Deployment is SUCCESSFUL if:**
- [ ] Application is running and responding to requests
- [ ] All health checks pass
- [ ] Users can log in, browse products, place orders
- [ ] Admin functions work correctly
- [ ] No errors in logs after 24 hours
- [ ] Database is properly created with all tables
- [ ] Performance is acceptable
- [ ] Backups are working

❌ **Deployment needs to ROLLBACK if:**
- [ ] Application won't start
- [ ] Cannot connect to PostgreSQL
- [ ] Core functionality broken (login fails, products inaccessible)
- [ ] Unrecoverable data corruption
- [ ] Performance degradation >50%

---

## Post-Success Steps

After 24 hours of stable operation:

- [ ] Decommission MySQL database (after final backup)
- [ ] Document PostgreSQL connection details in team wiki
- [ ] Update deployment documentation with actual connection details
- [ ] Schedule team meeting to discuss lessons learned
- [ ] Monitor database growth for scaling needs
- [ ] Set up PostgreSQL automated maintenance (VACUUM, ANALYZE)

---

## Deployment Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| DevOps Lead | | | |
| Project Manager | | | |
| Tech Lead | | | |
| On-Call Support | | | |

---

## Useful Commands

```bash
# Verify PostgreSQL running
systemctl status postgresql

# Check version
psql --version

# Connect to database
psql postgresql://user:password@host:5432/database

# View database tables
\dt

# View table structure
\d table_name

# View indexes
\di

# View database size
SELECT pg_size_pretty(pg_database_size('nursery_db'));

# View active connections
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;

# Generate Prisma client
python -m prisma generate

# View migration status
python -m prisma migrate status
```

---

**Last Updated**: April 9, 2026  
**Next Review**: After first successful production deployment

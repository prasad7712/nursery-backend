# Deploying Nursery Backend to Render

**Last Updated**: April 9, 2026  
**Database**: PostgreSQL  
**Status**: Ready for Production Deployment

---

## Prerequisites

Before you start, you need:

1. **GitHub Repository Access**
   - Your repo must be pushed to GitHub: `https://github.com/prasad7712/nursery-backend`
   - Ensure all branches are up to date

2. **Render Account**
   - Create free account at [render.com](https://render.com)
   - Link your GitHub account to Render

3. **PostgreSQL Database**
   - Will be created in Render PostgreSQL service

---

## Step 1: Create PostgreSQL Database on Render

### In Render Dashboard:

1. Click **"New +"** → **"PostgreSQL"**
2. Configure database:
   - **Name**: `nursery_db`
   - **Database**: `nursery_db`
   - **User**: `postgres` (default)
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid, depending on your needs)
3. Click **"Create Database"**
4. **Save the connection string** (you'll need it in Step 2)

Connection string format:
```
postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/nursery_db
```

---

## Step 2: Create Web Service on Render

### In Render Dashboard:

1. Click **"New +"** → **"Web Service"**
2. **Connect Repository**:
   - Select your GitHub repo: `nursery-backend`
   - Branch: `main`
   - Click **"Connect"**

3. **Configure Service**:
   - **Name**: `nursery-backend`
   - **Region**: Same as your database
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install --prefer-binary -r requirements.txt && prisma generate`
   - **Start Command**: `python run_app.py`
   - **Plan**: Free (or paid)

4. **Add Environment Variables**:
   Click **"Add Environment Variable"** and add:
   
   ```
   DATABASE_URL = [paste your PostgreSQL connection string from Step 1]
   ENVIRONMENT = production
   DEBUG = False
   JWT_SECRET_KEY = [generate a strong random key]
   ADMIN_EMAIL = admin@yourdomain.com
   ADMIN_PASSWORD = [secure password]
   ADMIN_FIRST_NAME = Admin
   ADMIN_LAST_NAME = User
   RAZORPAY_KEY_ID = [your key if using payments]
   RAZORPAY_KEY_SECRET = [your secret if using payments]
   RAZORPAY_WEBHOOK_SECRET = [your webhook secret]
   GROQ_API_KEY = [your Groq API key if using AI]
   ```

5. Click **"Create Web Service"**

### Important Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `ENVIRONMENT` | `production` | Disables debug mode |
| `DEBUG` | `False` | Disable debug in production |
| `JWT_SECRET_KEY` | Strong random key (32+ chars) | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ADMIN_EMAIL` | Your email | Auto-created on first startup |
| `ADMIN_PASSWORD` | Secure password | Must be 8+ chars with uppercase, lowercase, digit, special char |

---

## Step 3: Deploy the Application

### Automatic Deployment
Once you create the Web Service, Render will automatically:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Generate Prisma client
4. Start the application

**Monitor the deployment**:
- Go to your service's **"Logs"** tab
- Watch for:
  ```
  ✅ Database connected successfully via Prisma
  ✅ Admin user created successfully!
  ✅ All services connected successfully
  INFO: Application startup complete.
  ```

### Manual Redeploy (if needed)
Go to your service → Click **"Manual Deploy"** → Select branch → Click **"Deploy"**

---

## Step 4: Initialize Database

Once deployment is complete:

1. **Run migrations**:
   ```bash
   # In Render shell (if available):
   python -m prisma migrate deploy
   ```

2. **Seed database** (optional):
   ```bash
   python scripts/seed_db.py
   ```

3. **Verify deployment**:
   ```bash
   curl https://[your-app-name].onrender.com/health
   ```
   Should return: `{"status": "ok"}`

---

## Step 5: Test Your Deployment

### Test Endpoints

```bash
# Health check
curl https://[your-app-name].onrender.com/health

# API docs
https://[your-app-name].onrender.com/docs

# Register new user
curl -X POST https://[your-app-name].onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST https://[your-app-name].onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123!"
  }'

# List products
curl https://[your-app-name].onrender.com/products
```

### Access Admin Dashboard

1. Navigate to: `https://[your-app-name].onrender.com/docs`
2. Login with:
   - Email: `admin@yourdomain.com` (or value from ADMIN_EMAIL)
   - Password: `[ADMIN_PASSWORD value]`

---

## Troubleshooting

### Build Fails - "pydantic-core compilation error"

**Solution**: Already fixed in `requirements.txt` and `build.sh`

The issue was pydantic-core trying to compile on Render's read-only filesystem. Fixed by:
- Downgrading `pydantic==2.9.0` (has pre-built wheels)
- Adding `build.sh` with `--prefer-binary` flag
- Specifying Python 3.11 (better wheel support than 3.14.3)

### Build Fails - "prisma generate error"

**Solution**: Check these steps:
1. Verify `prisma` version in requirements.txt: `prisma==0.15.0`
2. Ensure `DATABASE_URL` environment variable is set
3. Check that PostgreSQL database exists (from Step 1)

### Application Won't Start - "Database connection failed"

**Solution**:
1. Verify `DATABASE_URL` is correct:
   ```
   postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/nursery_db
   ```
2. Check PostgreSQL service is running on Render
3. Verify database name is `nursery_db` (case-sensitive)
4. Wait 30 seconds - Render PostgreSQL takes time to initialize

### Application Crashes After Deploy

**Solution**: Check logs for errors:
1. Go to service → **"Logs"**
2. Look for red error messages
3. Common issues:
   - Missing environment variables
   - Incorrect DATABASE_URL
   - Outdated Prisma schema

### API Endponits Return 502 Bad Gateway

**Solution**:
1. Restart web service: Service → **"Manual Deploy"**
2. Check recent deploys in **"Events"** tab
3. Verify all environment variables are set
4. Ensure PostgreSQL database is healthy

---

## Database Management

### Backup Your Database

```bash
# Render PostgreSQL services have automatic backups
# Access them in: Render Dashboard → Database → Backups

# To manually export:
pg_dump postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/nursery_db > backup.sql
```

### Monitor Database

In Render Dashboard:
1. Go to your PostgreSQL service
2. Check **"Metrics"** for:
   - Connection count
   - Storage usage
   - Query performance

### Connect to Database Directly

```bash
psql postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/nursery_db

# Once connected:
\dt                    # List tables
SELECT COUNT(*) FROM users;  # Count users
\q                     # Quit
```

---

## Environment Variables Reference

### Required
```
DATABASE_URL=postgresql://postgres:password@host:5432/nursery_db
JWT_SECRET_KEY=your-very-secure-random-key-here-32-chars-minimum
```

### Recommended
```
ENVIRONMENT=production
DEBUG=False
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecurePassword123!
```

### Optional (for Features)
```
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxx
RAZORPAY_WEBHOOK_SECRET=xxxx
GROQ_API_KEY=gsk_xxxxx
DEMO_MODE=false
```

### Generate Strong JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Generate Admin Password (Requirements: 8+ chars, upper, lower, digit, special)
```bash
python -c "
import secrets
import string
chars = string.ascii_letters + string.digits + '!@#$%^&*'
password = ''.join(secrets.choice(chars) for _ in range(12))
print(password)
"
```

---

## Deployment Checklist

### Before Deploying
- [ ] All code committed and pushed to GitHub
- [ ] `requirements.txt` updated with latest versions
- [ ] `.env` file NOT committed (confidential data)
- [ ] PostgreSQL database created on Render
- [ ] Environment variables prepared
- [ ] JWT_SECRET_KEY generated
- [ ] Admin credentials secured

### During Deployment
- [ ] Monitor build logs for errors
- [ ] Wait for application to start completely
- [ ] Check for any migration errors
- [ ] Verify database connectivity

### After Deployment
- [ ] Test health endpoint: `/health`
- [ ] Test API documentation: `/docs`
- [ ] Test user registration
- [ ] Test user login
- [ ] Test product listing
- [ ] Check admin dashboard access

---

## Continuous Deployment

### Auto-Deploy on GitHub Push

**Already configured**: Render automatically deploys when you push to your GitHub repository.

To disable/enable:
1. Service → **"Settings"**
2. Under "Deploy on Push": toggle on/off

### Deploy Specific Branch

1. Service → **"Settings"**
2. Change "Branch": `main` → `your-branch`
3. Manually deploy that branch

### Rollback to Previous Version

1. Service → **"Events"** tab
2. Find previous deployment
3. Click **"Rollback"** (if available)

---

## Monitoring & Maintenance

### Enable Error Alerts

1. Service → **"Notifications"**
2. Add email for alerts on:
   - Build failures
   - Runtime errors
   - Memory/CPU issues

### Monitor Performance

1. Service → **"Metrics"** tab
2. Check:
   - CPU usage (should be < 80%)
   - Memory usage (should be < 500MB on free tier)
   - Request count
   - Error rate

### Scale When Needed

- **Free tier**: ~100 concurrent users
- **Paid tier**: Upgradeable to handle more traffic
- Go to Service → **"Plan"** to upgrade

---

## Cost Estimates (As of April 2026)

| Item | Free Tier | Paid Tier |
|------|-----------|-----------|
| Web Service | Free (0.50 hrs/month) | $7/month |
| PostgreSQL DB | $15/month | $15/month + |
| **Total** | **~$15/month** | **$22+/month** |

*Note: Free web service uses shared CPU and sleeps after inactivity*

---

## Support & Troubleshooting

### Render Support
- **Docs**: https://render.com/docs
- **Status**: https://status.render.com

### Application Logs
- Located in: Service → **"Logs"**
- Filter by: Time, log level, keyword

### Debug Issues

1. **Check application logs** in Render dashboard
2. **SSH into service** (if available):
   ```bash
   render connect [service-name]
   ```
3. **Inspect environment**:
   ```bash
   echo $DATABASE_URL
   python -m prisma migrate status
   ```

### Common Commands in Render Shell

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test database connection
python -c "from src.plugins.database import db; print(db)"

# Run migrations
python -m prisma migrate deploy

# Check service status
systemctl status gunicorn
```

---

## Next Steps

1. ✅ Create PostgreSQL database on Render
2. ✅ Create Web Service connected to GitHub
3. ✅ Set all environment variables
4. ✅ Monitor initial deployment
5. ✅ Run integration tests against production
6. ✅ Set up monitoring and alerts
7. ✅ Configure custom domain (optional)
8. ✅ Set up backups (automated by Render)

---

## Quick Reference Links

- **Render Dashboard**: https://dashboard.render.com
- **Your Service**: https://[your-app-name].onrender.com
- **API Docs**: https://[your-app-name].onrender.com/docs
- **Database Connection**: Use `$DATABASE_URL` environment variable

---

**Happy Deploying!** 🚀

For more help, see [POSTGRESQL_MIGRATION_COMPLETE.md](POSTGRESQL_MIGRATION_COMPLETE.md)

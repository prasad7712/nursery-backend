# Render Deployment Configuration - REQUIRED SETUP

## ⚠️ IMPORTANT: Manual Render Configuration Required

For existing Render services, `render.yaml` is **not automatically used**. You must manually configure these settings in the Render dashboard:

---

## Step-by-Step Configuration in Render Dashboard

### 1. Go to Your Service Settings
- Visit: https://dashboard.render.com
- Click on your service: `nursery-backend`
- Click the **Settings** tab

### 2. Configure Build Command
In the **Build Command** field, replace the current command with:
```bash
chmod +x render-build.sh && ./render-build.sh
```

### 3. Configure Start Command
In the **Start Command** field, replace with:
```bash
python run_app.py
```

### 4. Configure Environment Variables
Add or verify these environment variables:
- `ENVIRONMENT` = `production`
- `PORT` = `8001`
- `PYTHONUNBUFFERED` = `1`
- `DATABASE_URL` = (your PostgreSQL connection string from Render database)
- `ADMIN_EMAIL` = `admin@nursery.local`
- `ADMIN_PASSWORD` = `Admin@123` (change in production!)
- `JWT_SECRET_KEY` = (generate a strong secret key)
- `RAZORPAY_KEY_ID` = (your Razorpay key)
- `RAZORPAY_KEY_SECRET` = (your Razorpay secret)
- `GROQ_API_KEY` = (your Groq API key)

### 5. Save and Re-Deploy
1. Click **Save Changes** at the bottom
2. Manually deploy:
   - Click **Events** tab
   - Click **Manual Deploy** button
   - Select branch: `main`
   - Click **Deploy**

---

## What the Build Script Does

The `render-build.sh` script:
1. ✅ Upgrades pip, setuptools, and wheel
2. ✅ Installs all Python dependencies with wheel preference
3. ✅ Generates Prisma client (`prisma generate`)
4. ✅ Fetches Prisma query engine binaries (`prisma py fetch`)
5. ✅ Verifies Prisma is working
6. ✅ Caches binaries in `/opt/render/.prisma-cache`

---

## Deployment Success Indicators

When the build succeeds, you should see:
```
✅ Build completed successfully
INFO:     Started server process
INFO:     Application startup complete.
🚀 Starting FastAPI Auth Service...
✅✅✅ Groq AI initialized successfully
✅ Database connection successful
✅ All services connected successfully
```

---

## Troubleshooting

### If Build Still Fails
1. Check **Build Logs** in Render Events tab
2. Look for errors about missing binaries
3. Try a **Clear Build Cache + Redeploy**:
   - Settings → Build & Deploy
   - Click "Clear Cache"
   - Then Manual Deploy

### If App Won't Start
1. Check **Runtime Logs** in Events tab
2. Verify DATABASE_URL is correctly set
3. Ensure all required environment variables are present
4. Try restarting the service from Settings

---

## Next: After Deployment

Once the app is running:
1. Visit `https://nursery-backend-xxxx.onrender.com/docs`
2. Test the API endpoints
3. Verify database connectivity
4. Check logs for any errors

**The deployment should be complete once the app responds without errors!**

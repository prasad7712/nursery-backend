# Quick Start: Deploy to Render (Fixed Build)

**Time to Deploy**: ~10 minutes  
**Status**: ✅ Ready (build issue fixed)

---

## 1️⃣ Push Updated Code to GitHub (2 min)

```bash
cd d:\My Projects\nursery-backend

git add requirements.txt render.yaml build.sh
git commit -m "Fix: Render build config for PostgreSQL deployment"
git push origin main
```

**Verify on GitHub**: https://github.com/prasad7712/nursery-backend

---

## 2️⃣ Create PostgreSQL Database on Render (3 min)

1. Go to **[dashboard.render.com](https://dashboard.render.com)**
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in:
   - **Name**: `nursery_db`
   - **Database**: `nursery_db`
   - **User**: `postgres` (auto)
   - **Region**: Choose your region (e.g., US, EU)
   - **Plan**: Free (unless you need paid features)
4. Click **"Create Database"**
5. **📌 SAVE THIS CONNECTION STRING**:
   ```
   postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/nursery_db
   ```

---

## 3️⃣ Create Web Service on Render (3 min)

1. Click **"New +"** → **"Web Service"**
2. **Connect Repository**: 
   - Choose: `nursery-backend`
   - Branch: `main`
   - Click **"Connect"**
3. **Fill in Details**:
   - **Name**: `nursery-backend`
   - **Region**: Same as your database
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install --prefer-binary -r requirements.txt && prisma generate`
   - **Start Command**: `python run_app.py`
   - **Plan**: Free (can upgrade later)
4. Click **"Create Web Service"**

---

## 4️⃣ Add Environment Variables (2 min)

After creating the web service:

1. Go to your service → **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add each variable (from the table below):

### Required Variables

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your connection string from Step 2 |
| `JWT_SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### Recommended Variables

| Key | Value |
|-----|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `False` |
| `ADMIN_EMAIL` | Your email address |
| `ADMIN_PASSWORD` | Strong password (8+ chars, upper, lower, digit, special) |
| `ADMIN_FIRST_NAME` | `Admin` |
| `ADMIN_LAST_NAME` | `User` |

### Optional Variables (if using)

| Key | Value |
|-----|-------|
| `RAZORPAY_KEY_ID` | Your Razorpay key |
| `RAZORPAY_KEY_SECRET` | Your Razorpay secret |
| `GROQ_API_KEY` | Your Groq API key |
| `DEMO_MODE` | `false` |

---

## 5️⃣ Deploy! (3 min)

1. After adding variables, Render automatically starts a deploy
2. Go to **"Events"** tab to watch the deployment
3. **Watch for green checkmark** ✅ (deployment succeeded)
4. In **"Logs"** tab, look for:
   ```
   ✅ Database connected successfully via Prisma
   ✅ Admin user created successfully!
   ✅ All services connected successfully
   INFO: Application startup complete.
   ```

---

## 6️⃣ Test Your Deployment ✅

Get your app URL from the service page (looks like: `your-app-name.onrender.com`)

### Test Health Check
```bash
curl https://your-app-name.onrender.com/health
```
Should return: `{"status":"ok"}`

### Access API Documentation
```
https://your-app-name.onrender.com/docs
```

### Test User Registration
```bash
curl -X POST https://your-app-name.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### List Products
```bash
curl https://your-app-name.onrender.com/products
```

---

## ✅ Done!

Your backend is now live on Render with PostgreSQL! 🎉

### What Was Fixed
- ✅ pydantic-core compilation error (used pre-built wheels)
- ✅ Python 3.14.3 wheel support issue (downgraded to 3.11)
- ✅ Render build environment configuration (render.yaml)
- ✅ Database migration working with PostgreSQL

---

## Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| Build fails | Check logs - usually missing env vars. View [RENDER_BUILD_FIX.md](RENDER_BUILD_FIX.md) |
| App won't start | Verify DATABASE_URL is correct in Environment tab |
| Pages return 502 | Go to Events → Manual Deploy |
| Products not showing | Wait 30 seconds, then refresh - DB migration completing |
| Login fails | Verify ADMIN_EMAIL and ADMIN_PASSWORD match what you set |

---

## Next Steps

### Optional Enhancements
1. **Custom Domain**: Service Settings → Domains
2. **SSL Certificate**: Automatic with Render
3. **Monitoring**: Service → Metrics tab
4. **Backups**: Database → Backups tab (automatic daily)

### Production Best Practices
- [ ] Change default admin password
- [ ] Set DEBUG=False (already done)
- [ ] Generate strong JWT_SECRET_KEY
- [ ] Enable PostgreSQL backups
- [ ] Set up error notifications
- [ ] Monitor performance metrics

---

## Links

- **Your Service**: `https://[your-app-name].onrender.com`
- **API Docs**: `https://[your-app-name].onrender.com/docs`
- **Render Dashboard**: https://dashboard.render.com
- **Full Guide**: [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)

---

**Congratulations! You've successfully deployed your Nursery Backend to Render!** 🚀

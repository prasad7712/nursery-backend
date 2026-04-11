# Render Configuration - Manual Setup Required

**Important**: Render may not auto-detect your Python version. You need to manually configure the build command.

---

## Why Still Failing?

Render is using **Python 3.14.3** (very new version) which doesn't have pre-built wheels for pydantic-core.

**Solution**: Tell Render to use Python 3.11 (stable + has wheels) and use `--prefer-binary` flag.

---

## Steps to Fix on Render Dashboard

### 1. Go to Your Render Service

Dashboard → Services → `nursery-backend`

### 2. Go to Settings Tab

Click **"Settings"** in the top menu

### 3. Update Build Command

Find the **"Build Command"** field and replace it with:

```bash
pip install --upgrade pip setuptools wheel && pip install --prefer-binary -r requirements.txt && python -m prisma generate
```

### 4. Update Start Command (if needed)

Should be:
```bash
python run_app.py
```

### 5. Check Environment tab

Verify Python version setting:
- If there's a "Python Version" field, set it to: `3.11` or `3.11.9`

### 6. Deploy

Go to **"Events"** tab and click **"Manual Deploy"**

### 7. Monitor Logs

Watch **"Logs"** tab for build success

You should see:
```
Successfully installed fastapi-0.115.0 uvicorn-0.31.0 prisma-0.15.0 pydantic-2.7.4 ...
✔ Generated Prisma Client Python
✅ Application startup complete
```

---

## Files Updated on Your End

✅ `runtime.txt` - Set to Python 3.11.9  
✅ `requirements.txt` - Updated to pydantic 2.7.4 (has wheels)  
✅ `Procfile` - Added start command  
✅ `build.sh` - Build script available if needed  

---

## If It Still Fails

### Option A: Try Downgrading Prisma

If pydantic still has issues, try:

**requirements.txt**:
```
prisma==0.14.0  # (instead of 0.15.0)
```

Then redeploy.

### Option B: Use Render Build Script

If you want to use a custom build script:

1. In Render Settings, set:
   - **Build Command**: `bash build.sh`
   - **Python Version**: `3.11`

2. Render will run the `build.sh` file in your repo

### Option C: Contact Render Support

If still failing after trying above:
- Check: https://status.render.com (any outages?)
- Ask Render support about Python 3.14 wheel availability

---

## Quick Checklist

Before trying deployment again, verify:

- [ ] `runtime.txt` contains: `python-3.11.9`
- [ ] `requirements.txt` has: `pydantic==2.7.4`
- [ ] Render Build Command includes: `--prefer-binary`
- [ ] Render Start Command is: `python run_app.py`
- [ ] All files committed and pushed to GitHub

---

## Files Ready for Deployment

✅ PostgreSQL migration complete (MySQL → PostgreSQL)  
✅ `.env` configured with DATABASE_URL  
✅ `prisma/schema.prisma` using PostgreSQL  
✅ `requirements.txt` using compatible versions  
✅ `runtime.txt` specifying Python 3.11  
✅ Application ready to run  

---

**Next**: Follow Steps 1-7 above on Render dashboard, then try deploying again.

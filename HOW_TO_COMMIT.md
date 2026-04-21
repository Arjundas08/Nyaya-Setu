# 📤 HOW TO COMMIT & PUSH TO GITHUB

## STEP 1: Check Git Status

Open PowerShell in your project folder:

```powershell
cd "c:\Users\hp\OneDrive\Desktop\nyaya-setu-1"
git status
```

You should see many files listed as "Untracked" (red)

---

## STEP 2: Stage All Files

```powershell
git add .
```

Check again:
```powershell
git status
```

Now files should appear in green (ready to commit)

---

## STEP 3: Create Your First Commit

```powershell
git commit -m "Initial commit: Nyaya-Setu deployment ready"
```

✓ All changes are now saved locally

---

## STEP 4: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to: **https://github.com/new**
2. Fill in:
   ```
   Repository name: nyaya-setu
   Description: AI-powered legal assistance for Indian citizens
   Public (so Render can access it)
   ```
3. Click "Create repository"
4. **Copy the HTTPS URL** (looks like: `https://github.com/YOUR_USERNAME/nyaya-setu.git`)

### Option B: Using GitHub CLI (if installed)

```powershell
gh repo create nyaya-setu --public --source=. --remote=origin --push
```

---

## STEP 5: Connect Local Repo to GitHub

Copy-paste this (replace YOUR_USERNAME):

```powershell
git remote add origin https://github.com/YOUR_USERNAME/nyaya-setu.git
git branch -M main
```

Verify:
```powershell
git remote -v
```

Should show:
```
origin  https://github.com/YOUR_USERNAME/nyaya-setu.git (fetch)
origin  https://github.com/YOUR_USERNAME/nyaya-setu.git (push)
```

---

## STEP 6: Push to GitHub

```powershell
git push -u origin main
```

First time might ask for authentication:
- Click "Sign in with browser" or
- Generate personal access token at: https://github.com/settings/tokens

After authentication, code is uploaded to GitHub ✓

---

## STEP 7: Verify on GitHub

1. Go to: `https://github.com/YOUR_USERNAME/nyaya-setu`
2. Should see all your files there
3. Click on files to verify ✓

---

## ✅ COMPLETE COMMAND SEQUENCE (Copy & Paste All)

Open PowerShell and run these one by one:

```powershell
# 1. Go to project folder
cd "c:\Users\hp\OneDrive\Desktop\nyaya-setu-1"

# 2. Initialize git (if not already done)
git init

# 3. Check status
git status

# 4. Stage all files
git add .

# 5. Create commit
git commit -m "Initial commit: Nyaya-Setu ready for deployment"

# 6. Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/nyaya-setu.git

# 7. Rename branch to main
git branch -M main

# 8. Push to GitHub
git push -u origin main
```

---

## 🔍 IF YOU GET ERRORS

### Error: "fatal: not a git repository"
**Solution:**
```powershell
git init
```

### Error: "remote origin already exists"
**Solution:**
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/nyaya-setu.git
```

### Error: "Permission denied" or "401 Unauthorized"
**Solution:**
1. Go to: https://github.com/settings/tokens
2. Generate new token (check `repo` permission)
3. Copy token
4. When prompted for password, paste the token

### Error: "branch main does not exist"
**Solution:**
```powershell
git branch -M main
git push -u origin main
```

---

## 📋 WHAT FILES GET COMMITTED

**Included:**
- ✅ All .py files (code)
- ✅ requirements.txt
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ nginx.conf
- ✅ README.md
- ✅ All frontend/backend files

**Excluded** (in .gitignore):
- ❌ .env (API keys - NEVER commit)
- ❌ venv/ (virtual environment)
- ❌ .venv/ (virtual environment)
- ❌ chroma_db/ (will be rebuilt)
- ❌ __pycache__/
- ❌ *.pyc files

This is good - secrets stay safe ✓

---

## 🔄 FUTURE COMMITS (After First Time)

After initial commit, to push future changes:

```powershell
# Make changes to your code
# Then:

git add .
git commit -m "Your message describing what changed"
git push
```

That's it! No need for `git remote add` or `git branch -M` again.

---

## 📊 VERIFY COMMIT HISTORY

Check what you committed:

```powershell
git log --oneline
```

Should show:
```
abc1234 Initial commit: Nyaya-Setu ready for deployment
```

---

## ✅ WHEN DONE

You should have:
- ✓ Local repo with all code committed
- ✓ GitHub repository created
- ✓ Code pushed to GitHub
- ✓ Can see all files at: https://github.com/YOUR_USERNAME/nyaya-setu

**Next:** Use this GitHub repo to deploy on Render ✓

---

## 🚀 QUICK CHECKLIST

- [ ] PowerShell open in project folder
- [ ] Ran `git init`
- [ ] Ran `git add .`
- [ ] Ran `git commit -m "..."`
- [ ] Created repo on GitHub.com
- [ ] Ran `git remote add origin ...`
- [ ] Ran `git push -u origin main`
- [ ] Verified files appear on GitHub.com
- [ ] Ready to deploy on Render! ✓

---

**Done! Your code is now on GitHub. Ready for Render deployment! 🎉**

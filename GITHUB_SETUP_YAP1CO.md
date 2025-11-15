# Setting Up GitHub Account for yap1co

## Current Situation

- **Git Config:** Manish / manish@divayani.com
- **GitHub CLI:** Logged in as `techomanx`
- **Repository:** https://github.com/yap1co/projectsigma.git
- **Goal:** Commit and push as `yap1co`

## Option 1: Use yap1co Account via GitHub CLI (Recommended)

### Step 1: Logout Current Account

```powershell
gh auth logout
```

### Step 2: Login as yap1co

```powershell
gh auth login
```

**Follow the prompts:**
1. Choose "GitHub.com"
2. Choose "HTTPS" (recommended)
3. Choose "Login with a web browser"
4. Copy the code shown
5. Press Enter (browser will open)
6. Paste the code in browser
7. Authorize GitHub CLI
8. Select account: **yap1co** (if you have access)

### Step 3: Update Git Config (Optional but Recommended)

If you want commits to show as yap1co:

```powershell
# Set for this repository only
git config user.name "yap1co"
git config user.email "your-yap1co-email@example.com"

# Or set globally (affects all repositories)
git config --global user.name "yap1co"
git config --global user.email "your-yap1co-email@example.com"
```

**Note:** Replace `your-yap1co-email@example.com` with the email associated with your yap1co GitHub account.

## Option 2: Keep Current Config, Use yap1co for Authentication Only

If you want to keep "Manish" as the commit author but authenticate as yap1co:

1. Just switch GitHub CLI account (Steps 1-2 above)
2. Keep your current Git config
3. Commits will show "Manish" but will be pushed with yap1co's permissions

## Option 3: Use SSH Keys (Advanced)

If you have SSH keys set up for yap1co:

```powershell
# Check existing SSH keys
ls ~/.ssh/*.pub

# Add SSH key to GitHub (if not already added)
# Copy public key: cat ~/.ssh/id_rsa.pub
# Add to GitHub: https://github.com/settings/keys

# Change remote to SSH
git remote set-url origin git@github.com:yap1co/projectsigma.git
```

## Verify Setup

```powershell
# Check GitHub CLI account
gh auth status

# Check Git config
git config user.name
git config user.email

# Check remote URL
git remote -v
```

## Important Notes

1. **Repository Access:** Make sure your yap1co account has write access to the repository
2. **Email Privacy:** If your GitHub email is private, use GitHub's no-reply email:
   - Format: `yap1co@users.noreply.github.com`
   - Or find it at: https://github.com/settings/emails
3. **Branch Divergence:** Your local branch has diverged from remote. You'll need to handle this before pushing.

## Next Steps After Authentication

1. **Handle Diverged Branches:**
   ```powershell
   # Pull and merge remote changes
   git pull origin main --no-rebase
   
   # Or if you want to rebase
   git pull origin main --rebase
   ```

2. **Stage Your Changes:**
   ```powershell
   git add .
   ```

3. **Commit:**
   ```powershell
   git commit -m "Add beginner setup guides and database schema"
   ```

4. **Push:**
   ```powershell
   git push origin main
   ```

## Troubleshooting

### "Permission denied" when pushing

**Solution:**
- Make sure yap1co account has write access to repository
- Check repository settings: https://github.com/yap1co/projectsigma/settings/access
- Verify authentication: `gh auth status`

### "Repository not found"

**Solution:**
- Repository might be private and your account doesn't have access
- Check you're logged in as the correct account: `gh auth status`
- Verify repository URL: `git remote -v`

### "Updates were rejected"

**Solution:**
- Your branch has diverged - pull first:
  ```powershell
  git pull origin main
  ```
- Resolve any merge conflicts
- Then push again


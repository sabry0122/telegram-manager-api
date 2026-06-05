@echo off
echo ========================================
echo   Upload to GitHub - Step by Step
echo ========================================
echo.

echo Step 1: Configure Git (first time only)
echo ----------------------------------------
set /p EMAIL="Enter your GitHub email: "
set /p NAME="Enter your name: "

git config --global user.email "%EMAIL%"
git config --global user.name "%NAME%"

echo.
echo Step 2: Create GitHub Repository
echo ----------------------------------------
echo 1. Go to: https://github.com/new
echo 2. Repository name: telegram-manager-api
echo 3. Make it Private
echo 4. DO NOT add README or .gitignore
echo 5. Click "Create repository"
echo.
pause

echo.
echo Step 3: Copy your repository URL
echo ----------------------------------------
echo Example: https://github.com/yourusername/telegram-manager-api.git
echo.
set /p REPO_URL="Paste your repository URL here: "

echo.
echo Step 4: Uploading files...
echo ----------------------------------------

git init
git add .
git commit -m "Initial commit - Backend API"
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ========================================
echo   SUCCESS! Files uploaded to GitHub!
echo ========================================
echo.
echo Next step: Deploy to Render.com
echo 1. Go to: https://render.com
echo 2. New + -> Web Service
echo 3. Connect your GitHub repository
echo 4. Select: telegram-manager-api
echo 5. Click Deploy!
echo.
pause

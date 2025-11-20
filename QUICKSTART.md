# ⚡ QUICK START GUIDE
## Get Pie Global Furniture Running in 10 Minutes

---

## 🎯 Prerequisites (Install These First)

1. **Python 3.12+**: Download from [python.org](https://www.python.org/downloads/)
2. **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
3. **PostgreSQL 14+**: Download from [postgresql.org](https://www.postgresql.org/download/)
4. **Git**: Download from [git-scm.com](https://git-scm.com/)

---

## 🚀 5-MINUTE BACKEND SETUP

### Step 1: Open Terminal in Backend Folder
```powershell
cd "C:\Users\Scott Newton\Desktop\Pie Global Funitures\backend"
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Create Database
```powershell
# Open PostgreSQL command line (psql) and run:
# CREATE DATABASE pie_global_db;
# Or use pgAdmin to create database named "pie_global_db"
```

### Step 5: Configure Environment
```powershell
# Copy .env.example to .env
copy .env.example .env

# Edit .env file and set your PostgreSQL password
# Minimum required: POSTGRES_PASSWORD=your_password
```

### Step 6: Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Admin User
```powershell
python manage.py createsuperuser
# Follow prompts to create username and password
```

### Step 8: Start Server
```powershell
python manage.py runserver
```

✅ **Backend is now running at http://localhost:8000**  
✅ **Admin panel at http://localhost:8000/admin**

---

## 🎨 5-MINUTE FRONTEND SETUP

### Step 1: Open NEW Terminal in Frontend Folder
```powershell
cd "C:\Users\Scott Newton\Desktop\Pie Global Funitures\frontend"
```

### Step 2: Install Dependencies
```powershell
npm install
```

### Step 3: Create Environment File
```powershell
# Copy .env.example to .env
copy .env.example .env

# .env should contain:
# VITE_API_URL=http://localhost:8000/api
```

### Step 4: Start Development Server
```powershell
npm run dev
```

✅ **Frontend is now running at http://localhost:3000**

---

## 🎉 YOU'RE DONE!

### Access Your Application
- **Website**: http://localhost:3000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/

### Next Steps
1. Log in to admin panel
2. Add some products
3. Upload slider images
4. Upload hero video
5. View your beautiful website!

---

## 🐛 TROUBLESHOOTING

### Backend Issues

**❌ "No module named 'rest_framework'"**
```powershell
pip install djangorestframework
```

**❌ "Could not connect to database"**
- Ensure PostgreSQL is running
- Check database name in .env is "pie_global_db"
- Verify PostgreSQL password in .env

**❌ "SECRET_KEY not set"**
- Ensure you copied .env.example to .env
- The default value will work for development

**❌ "Port 8000 already in use"**
```powershell
# Use different port
python manage.py runserver 8001
```

### Frontend Issues

**❌ "Cannot find module"**
```powershell
# Delete node_modules and reinstall
rmdir /s node_modules
npm install
```

**❌ "Port 3000 already in use"**
```powershell
# Vite will automatically use port 3001
```

**❌ "API calls failing"**
- Ensure backend is running on port 8000
- Check VITE_API_URL in .env
- Clear browser cache

---

## 📝 COMMON TASKS

### Add a Product (via Admin)
1. Go to http://localhost:8000/admin
2. Click "Products" → "Add Product"
3. Fill in name, price, category
4. Upload main image
5. Set stock quantity
6. Click "Save"

### Add Slider Images
1. Go to Admin → "Slider Images" → "Add"
2. Upload image
3. Set order number (lower = first)
4. Check "Active"
5. Save

### View Orders
1. Go to Admin → "Orders"
2. See all customer orders
3. Change status
4. Mark as paid

### Reply to Messages
1. Go to Admin → "User Messages"
2. Click on message
3. Write reply in "Reply text" field
4. Check "Replied"
5. Save

---

## 🔄 DAILY WORKFLOW

### Starting Work
```powershell
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Stopping Servers
- Press `Ctrl + C` in both terminals

### Making Database Changes
```powershell
# After modifying models.py
python manage.py makemigrations
python manage.py migrate
```

---

## 📚 HELPFUL COMMANDS

### Backend
```powershell
# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Shell (interactive Python)
python manage.py shell

# Check for issues
python manage.py check
```

### Frontend
```powershell
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 🎓 LEARNING RESOURCES

### Backend (Django)
- Official Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- PostgreSQL: https://www.postgresql.org/docs/

### Frontend (React)
- React Docs: https://react.dev/
- TypeScript: https://www.typescriptlang.org/docs/
- Tailwind CSS: https://tailwindcss.com/docs
- Vite: https://vitejs.dev/guide/

---

## 💡 TIPS

1. **Keep terminals open**: You need 2 terminals running (backend + frontend)
2. **Use admin panel**: Easiest way to add content
3. **Check console**: Browser console shows errors
4. **Read errors**: Error messages tell you what's wrong
5. **Git commit often**: Save your work frequently

---

## ✅ VERIFICATION

Everything working if you see:
- ✅ Backend: "Starting development server at http://127.0.0.1:8000/"
- ✅ Frontend: "Local: http://localhost:3000/"
- ✅ Admin panel loads and you can log in
- ✅ Frontend website loads and looks good
- ✅ No red errors in terminals

---

## 🆘 STILL STUCK?

1. Read the full README.md
2. Check AUDIT_REPORT.md for details
3. Read DEPLOYMENT.md for advanced setup
4. Check error messages carefully
5. Search error message on Google/Stack Overflow

---

## 🎉 SUCCESS!

You now have a **professional e-commerce platform** running locally!

**Happy coding! 🚀**

---

*Last updated: November 20, 2025*

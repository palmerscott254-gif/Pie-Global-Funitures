# 🚀 DEPLOYMENT CHECKLIST
## Production Deployment Guide for Pie Global Furniture

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### Backend (Django)

#### Environment & Security
- [ ] Set `DEBUG=False` in production `.env`
- [ ] Generate strong `SECRET_KEY` (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `CORS_ALLOWED_ORIGINS` to your frontend domain
- [ ] Configure database connection (PostgreSQL production credentials)
- [ ] Set up email configuration for notifications
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure security headers (already in settings)

#### Database
- [ ] Create production PostgreSQL database
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Load initial data (if any)
- [ ] Set up database backups

#### Static & Media Files
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Configure cloud storage for media (AWS S3/Cloudinary)
- [ ] Update `settings.py` with storage backend
- [ ] Test file uploads

#### Performance
- [ ] Install production server: Gunicorn already in requirements
- [ ] Configure Gunicorn workers (2-4 * CPU cores)
- [ ] Set up Redis for caching (optional but recommended)
- [ ] Enable database connection pooling
- [ ] Configure CDN for static files (CloudFront, CloudFlare)

#### Monitoring & Logging
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging to file
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure application monitoring (New Relic, DataDog)

---

### Frontend (React)

#### Environment
- [ ] Set production `VITE_API_URL` in `.env`
- [ ] Remove any development-only code
- [ ] Check for console.log statements
- [ ] Verify all environment variables

#### Build & Optimization
- [ ] Run production build: `npm run build`
- [ ] Check bundle size (should be < 500KB)
- [ ] Test built files locally: `npm run preview`
- [ ] Verify lazy loading works
- [ ] Check all routes work

#### SEO & Meta
- [ ] Add favicon and app icons
- [ ] Configure meta tags for each page
- [ ] Set up sitemap.xml
- [ ] Configure robots.txt
- [ ] Add Open Graph tags
- [ ] Add Twitter Card tags

#### Performance
- [ ] Enable gzip/brotli compression
- [ ] Configure caching headers
- [ ] Optimize images (WebP format)
- [ ] Enable HTTP/2
- [ ] Set up CDN

---

## 🌐 HOSTING OPTIONS

### Backend Options
1. **Heroku** - Easy, expensive
2. **Railway** - Modern, affordable
3. **DigitalOcean App Platform** - Good balance
4. **AWS Elastic Beanstalk** - Scalable, complex
5. **Google Cloud Run** - Serverless
6. **Render** - Simple, free tier

### Frontend Options
1. **Vercel** - Best for React, free tier ⭐
2. **Netlify** - Good, free tier
3. **CloudFlare Pages** - Fast, free
4. **AWS S3 + CloudFront** - Scalable
5. **GitHub Pages** - Simple, free (no server-side)

### Database Options
1. **Heroku Postgres** - Easy
2. **DigitalOcean Managed Postgres** - Affordable
3. **AWS RDS** - Scalable
4. **Supabase** - Modern, free tier
5. **Neon** - Serverless Postgres

---

## 📋 DEPLOYMENT STEPS

### Option 1: Separate Hosting (Recommended)

#### Backend on Railway/Render
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo>
git push -u origin main

# 2. Connect Railway/Render to GitHub
# - Create new project
# - Connect GitHub repository
# - Select backend folder

# 3. Configure environment variables in dashboard
# - All variables from .env.example
# - Set DEBUG=False
# - Set ALLOWED_HOSTS
# - Set database URL

# 4. Deploy automatically
```

#### Frontend on Vercel
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy from frontend folder
cd frontend
vercel

# 3. Configure settings
# - Build command: npm run build
# - Output directory: dist
# - Install command: npm install

# 4. Set environment variables
# - VITE_API_URL: your backend URL
```

### Option 2: Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "pie_global.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: pie_global_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: gunicorn pie_global.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - media_files:/app/media
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/pie_global_db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  media_files:
```

---

## 🧪 TESTING BEFORE DEPLOYMENT

### Backend Tests
```bash
# Run all tests
python manage.py test

# Check for security issues
python manage.py check --deploy

# Test API endpoints
curl http://localhost:8000/api/products/
```

### Frontend Tests
```bash
# Build and preview
npm run build
npm run preview

# Check bundle size
npm run build -- --report

# Test all routes manually
```

---

## 📊 POST-DEPLOYMENT CHECKLIST

### Verification
- [ ] Test all API endpoints work
- [ ] Test frontend loads correctly
- [ ] Test image uploads work
- [ ] Test order creation works
- [ ] Test admin panel works
- [ ] Test contact form works
- [ ] Test cart functionality
- [ ] Test on mobile devices
- [ ] Test on different browsers
- [ ] Check page load speed (< 3 seconds)
- [ ] Verify SSL certificate works
- [ ] Check SEO meta tags
- [ ] Test 404 page
- [ ] Test error handling

### Monitoring Setup
- [ ] Set up error alerts
- [ ] Set up uptime monitoring
- [ ] Set up performance monitoring
- [ ] Set up database monitoring
- [ ] Configure log rotation
- [ ] Set up automated backups

### Marketing & SEO
- [ ] Submit sitemap to Google Search Console
- [ ] Submit sitemap to Bing Webmaster Tools
- [ ] Set up Google Analytics
- [ ] Set up Facebook Pixel (if needed)
- [ ] Create social media accounts
- [ ] Test Open Graph sharing

---

## 🔧 MAINTENANCE

### Daily
- [ ] Check error logs
- [ ] Monitor uptime
- [ ] Check database health

### Weekly
- [ ] Review performance metrics
- [ ] Check security alerts
- [ ] Update dependencies (patch versions)
- [ ] Review user feedback

### Monthly
- [ ] Database backup verification
- [ ] Security audit
- [ ] Performance optimization
- [ ] Update minor versions
- [ ] Review analytics

### Quarterly
- [ ] Major version updates
- [ ] Feature additions
- [ ] Security penetration testing
- [ ] User experience improvements

---

## 🆘 TROUBLESHOOTING

### Common Issues

**500 Internal Server Error**
- Check DEBUG=False is set
- Check SECRET_KEY is set
- Check database connection
- Check static files collected
- Check ALLOWED_HOSTS

**Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check Whitenoise configuration
- Verify STATIC_ROOT path

**CORS Errors**
- Check CORS_ALLOWED_ORIGINS
- Ensure frontend URL is in list
- Check API URL in frontend .env

**Database Connection Failed**
- Verify DATABASE_URL
- Check firewall rules
- Verify credentials
- Check SSL requirements

---

## 📞 SUPPORT

For deployment support:
- Check Django docs: https://docs.djangoproject.com/
- Check React docs: https://react.dev/
- Hosting support: Contact your provider
- Emergency: [your-email@domain.com]

---

## ✅ FINAL CHECKLIST

Before going live:
- [ ] All environment variables set
- [ ] SSL/HTTPS enabled
- [ ] Database backed up
- [ ] Error tracking active
- [ ] Monitoring active
- [ ] All tests passing
- [ ] Performance optimized
- [ ] Security hardened
- [ ] Documentation complete
- [ ] Team trained

**Ready to launch! 🚀**

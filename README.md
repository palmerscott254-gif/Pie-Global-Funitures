# Pie Global Furniture

A full-stack e-commerce platform for Pie Global Furniture built with Django REST Framework and React + TypeScript.

## Project Structure

```
├── backend/          # Django REST API
│   ├── apps/        # Django applications
│   ├── pie_global/  # Project settings
│   ├── media/       # User-uploaded media files
│   └── staticfiles/ # Static assets
└── frontend/        # React + TypeScript application
    ├── src/         # Source code
    └── public/      # Public assets
```

## Features

- **Product Management**: Browse furniture products with categories and filters
- **Shopping Cart**: Add products to cart and manage orders
- **User Authentication**: Custom user authentication system
- **Admin Panel**: Django admin interface for content management
- **Image Gallery**: Product images with slider functionality
- **Contact Forms**: Message system for customer inquiries
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS
- **AWS S3 Integration**: Cloud storage for media files

## Technology Stack

### Backend
- **Framework**: Django 5.1.4
- **API**: Django REST Framework 3.15.2
- **Database**: PostgreSQL (production) / SQLite (development)
- **Storage**: AWS S3 (via django-storages & boto3)
- **CORS**: django-cors-headers
- **Server**: Gunicorn with Whitenoise for static files

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit
- **HTTP Client**: Axios
- **Routing**: React Router

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (for production)
- AWS S3 bucket (for media storage)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** in the backend directory:
   ```env
   # Django Settings
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (for production)
   DATABASE_URL=postgresql://postgres:254admin020@localhost:5432/pie_global_db
   # OR individual PostgreSQL settings
   POSTGRES_DB=pie_global_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=254admin020
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   
   # AWS S3 Storage
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_STORAGE_BUCKET_NAME=pieglobal
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Or use the shell command:
   ```bash
   python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
   ```

7. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**:
   ```bash
   python manage.py runserver
   ```

   The API will be available at: http://127.0.0.1:8000/

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create `.env` file** in the frontend directory:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at: http://localhost:5173/

## API Endpoints

### Products
- `GET /api/products/` - List all products
- `GET /api/products/:id/` - Get product details
- `POST /api/products/` - Create product (admin)
- `PUT /api/products/:id/` - Update product (admin)
- `DELETE /api/products/:id/` - Delete product (admin)

### Home
- `GET /api/home/sliders/` - Get slider images
- `GET /api/home/videos/` - Get promotional videos

### About
- `GET /api/about/` - Get about page content

### Orders
- `POST /api/orders/` - Create order
- `GET /api/orders/` - List orders (admin)

### Messages
- `POST /api/messages/` - Submit contact message
- `GET /api/messages/` - List messages (admin)

### Users
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login

## Deployment

### Render Deployment

The project is configured for deployment on Render.com. See `render.yaml` for service configuration.

**Required Environment Variables** (set in Render dashboard):
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=your-domain.onrender.com,pieglobalfunitures.co.ke`
- `DATABASE_URL` (auto-provided by Render PostgreSQL)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`

### Build Commands

**Backend**:
```bash
cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Frontend**:
```bash
cd frontend && npm install && npm run build
```

## Project Management Scripts

### Backend Scripts
- `backend/install.sh` - Setup script for Unix/Linux
- `backend/install.bat` - Setup script for Windows
- `backend/build.sh` - Production build script
- `backend/check_env.py` - Environment variable checker
- `backend/upload_media_to_s3.py` - Upload local media to S3
- `backend/populate_s3_records.py` - Create S3 media records

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

See LICENSE file for details.

## Contact

- Website: https://pieglobalfunitures.co.ke
- Email: info@pieglobalfunitures.co.ke

## Development Notes

### Default Admin Credentials
- Username: `admin`
- Password: `admin123`
- **⚠️ Change these in production!**

### Database
- Development uses SQLite by default
- Production uses PostgreSQL
- Media files stored in AWS S3

### Static Files
- Served by Whitenoise in production
- Collected in `backend/staticfiles/`

### CORS
- Configured in Django settings
- Update `CORS_ALLOWED_ORIGINS` for production domains

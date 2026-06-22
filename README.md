# CraveHub - AI Food Intelligence Platform

CraveHub is an advanced, AI-powered food intelligence and delivery platform featuring a dynamic, highly-responsive frontend built with React and Vite, seamlessly connected to a robust Django REST Framework backend.

## Features
- **AI Recommendation Engine**: Powered by Groq AI, offering smart, weather-based, and mood-based food suggestions.
- **Dynamic Service Hub**: Instamart, Dineout, Party Orders, Catering, and Gifts all integrated into a unified dashboard.
- **Real-time Search & Filtering**: Fast and fluid search with categories, dietary filters, and live results.
- **Favorites System**: Instantly save your favorite restaurants and dishes directly from the interactive menus.
- **Full Backend Integration**: Django handles users, menus, orders, real-time status tracking, and AI integration.

## Tech Stack
- **Frontend**: React, Vite, TailwindCSS (Vanilla custom classes), Context API.
- **Backend**: Python, Django, Django REST Framework.
- **AI Integrations**: Groq AI API.
- **Database**: PostgreSQL (or SQLite for development) and Redis (for caching).

## Getting Started (Docker)

The easiest way to run the entire CraveHub platform is using Docker Compose.

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running the Project

1. Ensure you have the `docker-compose.yml` file in the root directory.
2. In your terminal, run the following command to build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Once the containers are running:
   - The **Frontend** will be available at: `http://localhost:5173`
   - The **Backend API** will be available at: `http://localhost:8000`

### Accessing the Backend Container (Migrations & Superuser)
If you need to run database migrations or create an admin user, you can run commands inside the backend container:

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create a superuser
docker-compose exec backend python manage.py createsuperuser
```

---

## Local Development (Without Docker)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Enjoy using CraveHub!

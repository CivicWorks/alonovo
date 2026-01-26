# TODO: Server Deployment

## Immediate (on server)

1. **Create Postgres database**
   ```bash
   createdb alonovo_dev
   ```

2. **Backend setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create `.env` file** in `/backend/`
   ```
   DB_NAME=alonovo_dev
   DB_USER=your_postgres_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=generate-a-real-secret-key
   DEBUG=True
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://your-domain.com
   ```

4. **Run migrations and load data**
   ```bash
   python manage.py migrate
   python manage.py load_initial_data
   python manage.py createsuperuser
   ```

5. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

6. **Create `.env` file** in `/frontend/`
   ```
   PUBLIC_API_URL=http://localhost:8000/api
   ```

7. **Test locally**
   ```bash
   # Terminal 1
   cd backend && source venv/bin/activate && python manage.py runserver

   # Terminal 2
   cd frontend && npm run dev
   ```

8. **Verify**
   - Frontend at http://localhost:5173 shows 20 companies
   - API at http://localhost:8000/api/companies/ returns JSON
   - Admin at http://localhost:8000/admin/ works

## After verification works

- Configure production web server (gunicorn/nginx)
- Set DEBUG=False
- Configure static files
- Set up SSL

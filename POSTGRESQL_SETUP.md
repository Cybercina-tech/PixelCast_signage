# PostgreSQL Migration Setup Guide

This guide will help you migrate from SQLite to PostgreSQL using Docker for development.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with pip
- Virtual environment activated (recommended)

## Step-by-Step Setup

### 1. Update Dependencies

The `requirements.txt` has been updated with `psycopg2-binary`. Install it:

```bash
cd BackEnd
pip install -r requirements.txt
```

### 2. Create Environment File

Create a `.env` file in the `BackEnd` directory with the following content:

**BackEnd/.env:**
```env
# Django Settings
SECRET_KEY=django-insecure-7szgl4mmm9n0!&u3d4-=iut39ffowsvlr^r9img3r!izj=n3tq
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
# Set USE_SQLITE=True to use SQLite instead of PostgreSQL (fallback)
USE_SQLITE=False

# PostgreSQL Database Settings (when USE_SQLITE=False)
# These values should match your docker-compose.yml configuration
DB_NAME=screengram_db
DB_USER=screengram_user
DB_PASSWORD=Screengram2024!SecurePass#
DB_HOST=localhost
DB_PORT=5432

# Account Lockout Configuration
ACCOUNT_LOCKOUT_ENABLED=True
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900
```

**Note:** The `.env` file is already in `.gitignore` and will not be committed to version control.

### 3. Start PostgreSQL Container

From the root directory (where `docker-compose.yml` is located):

```bash
# Start the PostgreSQL container
docker-compose up -d

# Verify the container is running
docker-compose ps

# Check container logs (optional)
docker-compose logs db
```

### 4. Verify Database Connection

Test the connection using the management command:

```bash
cd BackEnd
python manage.py db_check

# For verbose output:
python manage.py db_check --verbose
```

### 5. Run Migrations

Apply all database migrations to PostgreSQL:

```bash
cd BackEnd
python manage.py migrate
```

### 6. Create Superuser

Create a Django superuser account:

```bash
cd BackEnd
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

## Quick Command Reference

### Start Database
```bash
docker-compose up -d
```

### Stop Database
```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ Deletes Data)
```bash
docker-compose down -v
```

### Check Container Status
```bash
docker-compose ps
```

### View Database Logs
```bash
docker-compose logs -f db
```

### Connect to PostgreSQL CLI
```bash
docker-compose exec db psql -U screengram_user -d screengram_db
```

### List Databases
```bash
docker-compose exec db psql -U screengram_user -l
```

### Verify Connection
```bash
cd BackEnd
python manage.py db_check
```

### Run Migrations
```bash
cd BackEnd
python manage.py migrate
```

### Create Superuser
```bash
cd BackEnd
python manage.py createsuperuser
```

## Fallback to SQLite

If you need to temporarily use SQLite (e.g., without Docker), set in `.env`:

```env
USE_SQLITE=True
```

The application will automatically use SQLite when this flag is set.

## Troubleshooting

### Connection Refused

**Error:** `connection refused` or `could not connect to server`

**Solutions:**
1. Verify container is running: `docker-compose ps`
2. Check if port 5432 is already in use: `netstat -an | grep 5432` (Linux/Mac) or `netstat -an | findstr 5432` (Windows)
3. Verify `DB_HOST=localhost` in `.env` file
4. Restart container: `docker-compose restart db`

### Authentication Failed

**Error:** `password authentication failed`

**Solutions:**
1. Verify `DB_PASSWORD` in `.env` matches the password in `docker-compose.yml`
2. Restart container: `docker-compose down && docker-compose up -d`
3. Check container logs: `docker-compose logs db`

### Database Does Not Exist

**Error:** `database "screengram_db" does not exist`

**Solutions:**
1. The database should be created automatically when the container starts
2. Manually create it: `docker-compose exec db createdb -U screengram_user screengram_db`
3. Verify in `docker-compose.yml` that `POSTGRES_DB=screengram_db`

### Migration Errors

If you encounter migration errors:

1. Check current migration status:
   ```bash
   python manage.py showmigrations
   ```

2. Fake initial migrations (if starting fresh):
   ```bash
   python manage.py migrate --fake-initial
   ```

3. Check for conflicting migrations:
   ```bash
   python manage.py makemigrations --dry-run
   ```

## Data Migration from SQLite (Optional)

If you have existing data in SQLite and want to migrate it:

1. **Export from SQLite:**
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Start PostgreSQL container and run migrations**

3. **Load into PostgreSQL:**
   ```bash
   python manage.py loaddata data.json
   ```

**Note:** This is a basic approach. For production migrations, consider using Django's database routing or specialized migration tools.

## Production Considerations

For production deployment:

1. **Use stronger passwords** - Generate secure random passwords
2. **Use environment variables** - Don't hardcode credentials
3. **Enable SSL/TLS** - Configure PostgreSQL SSL connections
4. **Use connection pooling** - Consider pgBouncer or similar
5. **Set up backups** - Configure automated PostgreSQL backups
6. **Monitor performance** - Set up database monitoring

## Security Notes

- The default password in `docker-compose.yml` and `.env` is for development only
- **Never commit `.env` files** to version control (already in `.gitignore`)
- **Change default passwords** before deploying to production
- Use Docker secrets or environment variable injection for production

## Next Steps

After successful setup:

1. ✅ Database connection verified
2. ✅ Migrations applied
3. ✅ Superuser created
4. 🚀 Start developing!

To start the Django development server:

```bash
cd BackEnd
python manage.py runserver
```


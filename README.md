# music-mood-recommender-app

## Prerequisites

Ensure you have the following installed on your machine:

- Python 3.10+
- PostgreSQL
- [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
- Virtualenv

## Installation

### Clone the Repository

```bash
git clone https://github.com/annsilin/music-mood-recommender-app.git
cd music-mood-recommender-app
```

### Set Up the Virtual Environment

On Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```cmd
python -m venv venv
.\venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Set the necessary environment variables in your OS. On Linux or macOS, you can use `export`:

```bash
export DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
export JWT_SECRET_KEY=your-jwt-secret-key
export FLASK_RUN_PORT=5000
export LASTFM_API_KEY=your-lastfm-api-key
export LASTFM_SECRET_KEY=your-lastfm-api-key
```

On Windows, use `set`:

```cmd
set DATABASE_URL=postgresql://username:password@localhost:5432/yourdatabase
set JWT_SECRET_KEY=your-jwt-secret-key
set FLASK_RUN_PORT=5000
set LASTFM_API_KEY=your-lastfm-api-key
set LASTFM_SECRET_KEY=your-lastfm-api-key
```

Replace `username`, `password`, `localhost`, `5432`, and `yourdatabase` with your PostgreSQL credentials and database
name.

`LASTFM_API_KEY` and `LASTFM_SECRET_KEY` are needed in order to use functionality to fetch music genre and/or album cover using
Last.fm API when adding songs to the database via admin UI. If you don't need this functionality, you can skip adding
these variables, otherwise obtain your credentials from https://www.last.fm/en/api

### Initialize the Database

Ensure PostgreSQL is running and create your database if it doesn't exist.

Run the following commands to initialize the database:

```bash
flask db init
flask db upgrade
```

## Running the Application

### Start Redis Server

Ensure the Redis server is running. You can start it using:

```bash
sudo service redis-server start
```

### Start the Flask Application

```bash
flask run
```

### Start the RQ Worker

In a separate terminal window, start the RQ worker:

```bash
rq worker
```

### Adding Admin user

Execute Flask CLI command to add admin user into the database:

```bash
flask create_admin <username>
```

If you want to delete admin user from the database, execute this command:

```bash
flask remove_admin <username>
```

### Populating the database

If you want to populate the database with the songs using admin UI, navigate to `<your_app_url>/admin` in your browser
window, authorize with admin account created with CLI command and follow the on-page instructions.
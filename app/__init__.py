from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from rq import Queue
from redis import Redis

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
redis_conn = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
queue = Queue(connection=redis_conn, default_timeout=-1)


from app import routes, models, commands, bg_jobs

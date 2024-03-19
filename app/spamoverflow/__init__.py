from flask import Flask
from os import environ
from spamoverflow.models.spamoverflow import Email, Domain, Customer
from apscheduler.schedulers.background import BackgroundScheduler
from spamoverflow.tasks.periodic_tasks import update_domains_count
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})  # Set cache timeout to 5 minutes = 300secs


def create_app(config_overrides=None): 
   app = Flask(__name__) 

   #This enables the postgres database if an environmental variable is declared, which it will be if we are using docker-compose.yml
   app.config['SQLALCHEMY_DATABASE_URI'] = environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///db.sqlite")
   if config_overrides: 
       app.config.update(config_overrides)
 
   # Load the models 
   from spamoverflow.models import db
   db.init_app(app) 

   #Initialize the caching
   cache.init_app(app)
 
   # Create the database tables 
   with app.app_context(): 
      db.create_all()

 
   # Register the blueprints 
   from spamoverflow.views.routes import api
   app.register_blueprint(api) 

   def run_update_domains_count():
        with app.app_context():
            update_domains_count()

   scheduler = BackgroundScheduler()
   scheduler.add_job(run_update_domains_count, 'interval', seconds=30)  #5 minutes is the max delay. I chose 30sec as trigger to keep it up to date.
   scheduler.start()
 
   return app

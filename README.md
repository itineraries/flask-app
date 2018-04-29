# flask-app
User stuff

This is a basic user interface that allows users to create accounts and login. It also allows you to save places, this will all at some point be merged with the rest of the application.

To setup: 
run pip install -r requirements.txt

set up a file called the-config.cfg, here you can configure the MONGO_DB settings and email server settings if you want.
Here's a setup sample:

MONGODB_SETTINGS = {
    'db': dbname,
    'host': hostname
}

SECRET_KEY = os.environ.get('SECRET_KEY') 

DEBUG=True
#EMAIL SETTINGS
MAIL_SERVER = 'mail_server_name'
MAIL_PORT = mail_port
MAIL_USE_TLS = False
MAIL_USE_SSL = True
ADMINS = ['youremail@example.com']
MAIL_USERNAME = 'yourotheremail@email.com'
MAIL_PASSWORD = 'otherEmailPassword'

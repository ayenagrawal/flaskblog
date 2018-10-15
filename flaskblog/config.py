# import os


class Config:
    SECRET_KEY = r'\xdb\xe6Y\xa9\xd1\xde\xc6\xaf\t\xa5`\x06\xf1Sf\xc5h\x0fGJ\x9di\x8d'
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'mailclient420@gmail.com'
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = 'a1!b2@c3#d4$'
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

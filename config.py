import os

class Config:
    SECRET_KEY = 'dotcomakiSECRETKEY'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
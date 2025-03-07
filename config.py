import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '90lynnrd')
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///appointments.db')
class BaseConfig:
    JWT_SECRET_KEY = 'HOSPITAL123'
    MONGO_URI = 'mongodb://localhost:27017/hospital?authSource=admin'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * 7

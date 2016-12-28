# -*- coding:utf-8 -*-
#!/usr/bin/env python

import os

class Config:
    SECRET_KEY = '\x9aL\x99|\xb0Z;-\xd67Y\x8c\x13\x1cP\xa4\xec9\x08.{\xdd\x96\xfc'
    SSL_DISABLE = False
    MAIL_SERVER = 'smtp.126.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'xxxx@126.com' #os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = 'xxxx' #os.getenv('MAIL_PASSWORD') #授权码
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'xxxx@126.com'
    FLASKY_ADMIN = 'xxxx@xx.com'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@192.168.0.251:3306/test'

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@192.168.0.251:3306/test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@192.168.0.251:3306/test'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to admin
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr=cls.FLASKY_MAIL_SENDER,
                toaddrs=[cls.FLASKY_ADMIN],
                subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
                credentials=credentials,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

    import logging
    from logging.handlers import SysLogHandler
    syslog_handler = SysLogHandler()
    syslog_handler.setLevel(logging.WARNING)
    app.logger.addHandler(syslog_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,

    'default': DevelopmentConfig
}

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #配置flask配置对象中键：SQLALCHEMY_COMMIT_TEARDOWN,设置为True,应用会自动在每次请求结束后提交数据库中变动
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    BOOTSTRAP_SERVE_LOCAL = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:xxx@127.0.0.1:3306/kgdev"
    NEO4J_URL = "bolt://127.0.0.1:7687"
    # NEO4J_URL = "neo4j+s://1b68a766.databases.neo4j.io"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "xxx"
    # NEO4J_PASSWORD = "FkaZST_8kFzsClpW8ES6k-kf-D4UWnz-mvja2kiXtEE"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:casia2022@127.0.0.1:3306/kgtest"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:casia2022@127.0.0.1:3306/kgdb"


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

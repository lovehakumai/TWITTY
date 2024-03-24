from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# SQLAlchemyインスタンスの作成
db = SQLAlchemy()

# Migrateインスタンスの作成は、アプリとdbインスタンスが利用可能になった後で行うため、
# ここでは初期化だけを行わずにインスタンスを作成します。
migrate = Migrate()
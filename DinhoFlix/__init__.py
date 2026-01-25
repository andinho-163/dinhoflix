from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
import sqlalchemy

# ===============================
# CRIAÇÃO DA APLICAÇÃO
# ===============================
app = Flask(
    __name__,
    static_folder='static',
    instance_relative_config=True
)

app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 1GB

# Garante que a pasta instance exista
os.makedirs(app.instance_path, exist_ok=True)

# ===============================
# CONFIGURAÇÕES
# ===============================
app.config['SECRET_KEY'] = '29cecf8afd6176f06bb3f55472d490d1'


# Banco de dados (sempre dentro de /instance)
if os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(app.instance_path, 'SiteTeste.db')
    )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

# ===============================
# EXTENSÕES
# ===============================
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'alert-info'

# ===============================
# MODELS
# ===============================
from DinhoFlix import models

# ===============================
# CRIAÇÃO / VERIFICAÇÃO DO BANCO
# ===============================
engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sqlalchemy.inspect(engine)

if not inspector.has_table("usuario"):
    with app.app_context():
        database.create_all()
        print("✅ Banco de dados criado com sucesso!")
else:
    print("ℹ️ Banco de dados já existente.")

# ===============================
# IMPORTAÇÃO DAS ROTAS
# ===============================

from DinhoFlix.routes import curtir_video
app.jinja_env.globals.update(curtir_video=curtir_video)
from DinhoFlix import routes

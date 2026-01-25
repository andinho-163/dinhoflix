from DinhoFlix import database, login_manager
from datetime import datetime, timezone
from flask_login import UserMixin


# ===============================
# LOGIN
# ===============================
@login_manager.user_loader
def load_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))


# ===============================
# USUÁRIO
# ===============================
class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)

    foto_perfil = database.Column(database.String, default='default.jpg')

    # RELACIONAMENTOS
    videos = database.relationship('Video', backref='autor', lazy=True)
    posts = database.relationship('Post', backref='autor', lazy=True)
    depoimentos = database.relationship('Depoimento', backref='autor', lazy=True)

    likes = database.relationship('Like', backref='usuario', lazy=True)
    comentarios = database.relationship('Comentario', backref='autor', lazy=True)


# ===============================
# VÍDEO
# ===============================
class Video(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    descricao = database.Column(database.Text, nullable=False)
    arquivo_video = database.Column(database.String, nullable=False)
    thumbnail = database.Column(database.String, nullable=False)

    data_criacao = database.Column(
        database.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    likes = database.relationship('Like', backref='video', lazy=True)
    comentarios = database.relationship('Comentario', backref='video', lazy=True)


# ===============================
# POST
# ===============================
class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)

    data_criacao = database.Column(
        database.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    likes = database.relationship('Like', backref='post', lazy=True)
    comentarios = database.relationship('Comentario', backref='post', lazy=True)


# ===============================
# DEPOIMENTO
# ===============================
class Depoimento(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)

    data_criacao = database.Column(
        database.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    likes = database.relationship('Like', backref='depoimento', lazy=True)
    comentarios = database.relationship('Comentario', backref='depoimento', lazy=True)


# ===============================
# LIKE (GENÉRICO)
# ===============================
class Like(database.Model):
    id = database.Column(database.Integer, primary_key=True)

    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    video_id = database.Column(database.Integer, database.ForeignKey('video.id'), nullable=True)
    post_id = database.Column(database.Integer, database.ForeignKey('post.id'), nullable=True)
    depoimento_id = database.Column(database.Integer, database.ForeignKey('depoimento.id'), nullable=True)

    __table_args__ = (
        database.UniqueConstraint('usuario_id', 'video_id', name='unique_like_video'),
        database.UniqueConstraint('usuario_id', 'post_id', name='unique_like_post'),
        database.UniqueConstraint('usuario_id', 'depoimento_id', name='unique_like_depoimento'),
    )


# ===============================
# COMENTÁRIO (GENÉRICO)
# ===============================
class Comentario(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    texto = database.Column(database.Text, nullable=False)

    data_criacao = database.Column(
        database.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

    video_id = database.Column(database.Integer, database.ForeignKey('video.id'), nullable=True)
    post_id = database.Column(database.Integer, database.ForeignKey('post.id'), nullable=True)
    depoimento_id = database.Column(database.Integer, database.ForeignKey('depoimento.id'), nullable=True)

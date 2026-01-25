# ==========================================
# IMPORTAÇÕES
# ==========================================

import os
import secrets
import subprocess

from PIL import Image

import imageio_ffmpeg as ffmpeg

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
    abort,
    jsonify
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)

from DinhoFlix import app, database, bcrypt
from DinhoFlix.forms import (
    FormLogin,
    FormCriarConta,
    FormEditarPerfil,
    FormCriarPost,
    FormUploadVideo,
    FormDepoimento
)
from DinhoFlix.models import (
    Usuario,
    Video,
    Post,
    Depoimento,
    Like,
    Comentario
)

# ==========================================
# FEED / NAVEGAÇÃO
# ==========================================

@app.route('/')
def home():
    return render_template(
        'home.html',
        videos=Video.query.order_by(Video.id.desc()).all(),
        posts=Post.query.order_by(Post.id.desc()).all(),
        depoimentos=Depoimento.query.order_by(Depoimento.id.desc()).all()
    )


@app.route('/explorar/<tipo>')
def explorar(tipo):
    if tipo == 'videos':
        return render_template(
            'home.html',
            videos=Video.query.order_by(Video.id.desc()).all(),
            posts=[],
            depoimentos=[]
        )

    if tipo == 'posts':
        return render_template(
            'home.html',
            videos=[],
            posts=Post.query.order_by(Post.id.desc()).all(),
            depoimentos=[]
        )

    if tipo == 'relatos':
        return render_template(
            'home.html',
            videos=[],
            posts=[],
            depoimentos=Depoimento.query.order_by(Depoimento.id.desc()).all()
        )

    abort(404)


# ==========================================
# AUTENTICAÇÃO
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criar = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_fazerlogin' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash('Bem-vindo!', 'success')
            return redirect(url_for('home'))
        flash('Credenciais inválidas', 'danger')

    if form_criar.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_hash = bcrypt.generate_password_hash(form_criar.senha.data).decode()

        usuario = Usuario(
            username=form_criar.username.data,
            email=form_criar.email.data,
            senha=senha_hash
        )
        database.session.add(usuario)
        database.session.commit()

        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template(
        'login.html',
        form_login=form_login,
        form_criarconta=form_criar
    )


@app.route('/sair')
@login_required
def sair():
    logout_user()
    return redirect(url_for('home'))


# ==========================================
# PERFIL
# ==========================================

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.foto_perfil.data:
            current_user.foto_perfil = salvar_imagem(form.foto_perfil.data)

        database.session.commit()
        flash('Perfil atualizado!', 'success')
        return redirect(url_for('perfil'))

    form.username.data = current_user.username
    form.email.data = current_user.email

    return render_template('editarperfil.html', form=form)


# ==========================================
# VÍDEOS
# ==========================================

@app.route('/video/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    form = FormUploadVideo()

    if form.validate_on_submit():
        nome_video = salvar_video(form.arquivo.data)

        if form.thumbnail.data:
            thumb = salvar_thumbnail(form.thumbnail.data)
        else:
            thumb = gerar_thumbnail_automatica(nome_video)

        video = Video(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            arquivo_video=nome_video,
            thumbnail=thumb,
            autor=current_user
        )

        database.session.add(video)
        database.session.commit()

        flash('Vídeo publicado!', 'success')
        return redirect(url_for('home'))

    return render_template('upload_video.html', form=form)


@app.route('/video/<int:video_id>')
@login_required
def exibir_video(video_id):
    video = Video.query.get_or_404(video_id)
    return render_template('video.html', video=video)


from flask import send_from_directory

@app.route('/media/videos/<filename>')
def media_video(filename):
    caminho = os.path.join(app.root_path, 'static/videos')
    return send_from_directory(caminho, filename)


@app.route('/curtir/video/<int:video_id>', methods=['POST'])
@login_required
def curtir_video(video_id):
    like = Like.query.filter_by(
        usuario_id=current_user.id,
        video_id=video_id
    ).first()

    if like:
        database.session.delete(like)
        liked = False
    else:
        database.session.add(
            Like(usuario_id=current_user.id, video_id=video_id)
        )
        liked = True

    database.session.commit()

    total = Like.query.filter_by(video_id=video_id).count()
    return jsonify(liked=liked, total_likes=total)

@app.route('/video/excluir/<int:video_id>', methods=['POST'])
@login_required
def excluir_video(video_id):
    video = Video.query.get_or_404(video_id)

    if video.autor != current_user:
        abort(403)

    database.session.delete(video)
    database.session.commit()
    flash('Vídeo excluído', 'success')
    return redirect(url_for('home'))


# ==========================================
# POSTS / RELATOS
# ==========================================

@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()

    if form.validate_on_submit():
        post = Post(
            titulo=form.titulo.data,
            corpo=form.corpo.data,
            autor=current_user
        )
        database.session.add(post)
        database.session.commit()
        flash('Post criado!', 'success')
        return redirect(url_for('home'))

    return render_template('criarpost.html', form=form)


@app.route('/depoimento/novo', methods=['GET', 'POST'])
@login_required
def criar_depoimento():
    form = FormDepoimento()

    if form.validate_on_submit():
        depoimento = Depoimento(
            titulo=form.titulo.data,
            corpo=form.corpo.data,
            autor=current_user
        )
        database.session.add(depoimento)
        database.session.commit()
        flash('Relato enviado!', 'success')
        return redirect(url_for('home'))

    return render_template('criar_depoimento.html', form=form)


# ==========================================
# COMENTÁRIOS
# ==========================================

@app.route('/comentario/<tipo>/<int:conteudo_id>', methods=['POST'])
@login_required
def comentar(tipo, conteudo_id):
    texto = request.form.get('texto')

    if not texto:
        return jsonify({'erro': 'Comentário vazio'}), 400

    comentario = Comentario(texto=texto, autor=current_user)

    if tipo == 'video':
        comentario.video_id = conteudo_id
    elif tipo == 'post':
        comentario.post_id = conteudo_id
    elif tipo == 'depoimento':
        comentario.depoimento_id = conteudo_id
    else:
        abort(400)

    database.session.add(comentario)
    database.session.commit()

    return jsonify({
        'id': comentario.id,
        'texto': comentario.texto,
        'usuario': current_user.username
    })


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def salvar_imagem(imagem):
    nome = secrets.token_hex(8) + os.path.splitext(imagem.filename)[1]
    caminho = os.path.join(app.root_path, 'static/fotos_perfil', nome)

    img = Image.open(imagem)
    img.thumbnail((400, 400))
    img.save(caminho)

    return nome


def salvar_video(arquivo):
    nome = secrets.token_hex(8) + os.path.splitext(arquivo.filename)[1]
    caminho = os.path.join(app.root_path, 'static/videos', nome)
    arquivo.save(caminho)
    return nome


def salvar_thumbnail(imagem):
    nome = secrets.token_hex(8) + os.path.splitext(imagem.filename)[1]
    caminho = os.path.join(app.root_path, 'static/thumbnails', nome)
    Image.open(imagem).save(caminho)
    return nome


def gerar_thumbnail_automatica(nome_video):
    caminho_video = os.path.join(app.root_path, 'static/videos', nome_video)
    nome_thumb = nome_video.rsplit('.', 1)[0] + '.jpg'
    caminho_thumb = os.path.join(app.root_path, 'static/thumbnails', nome_thumb)

    ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    comando = [
        ffmpeg_path,
        "-y",
        "-i", caminho_video,
        "-ss", "00:00:01",
        "-vframes", "1",
        caminho_thumb
    ]

    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return nome_thumb

# ==========================================
# IMPORTAÇÕES
# ==========================================

import os
import secrets
from PIL import Image

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
# 1. FEED E NAVEGAÇÃO
# ==========================================

@app.route('/')
def home():
    """Feed principal unificado."""
    return render_template(
        'home.html',
        videos=Video.query.order_by(Video.id.desc()).all(),
        posts=Post.query.order_by(Post.id.desc()).all(),
        depoimentos=Depoimento.query.order_by(Depoimento.id.desc()).all()
    )


@app.route('/contatos')
def contatos():
    return render_template('contatos.html')


@app.route('/explorar/<tipo>')
def explorar(tipo):
    """Filtro do feed por tipo."""
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
# 2. AUTENTICAÇÃO
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
        flash('Credenciais inválidas.', 'danger')

    if form_criar.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_hash = bcrypt.generate_password_hash(
            form_criar.senha.data
        ).decode()

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
# 3. PERFIL
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
# 4. VÍDEOS
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


# ==========================================
# 5. POSTS E RELATOS
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
# 6. CURTIDAS (POST / DEPOIMENTO)
# ==========================================

@app.route('/curtir/<tipo>/<int:conteudo_id>', methods=['POST'])
@login_required
def curtir_generico(tipo, conteudo_id):
    filtro = dict(usuario_id=current_user.id)

    if tipo == 'post':
        filtro['post_id'] = conteudo_id
    elif tipo == 'depoimento':
        filtro['depoimento_id'] = conteudo_id
    else:
        abort(400)

    like = Like.query.filter_by(**filtro).first()

    if like:
        database.session.delete(like)
        liked = False
    else:
        database.session.add(Like(**filtro))
        liked = True

    database.session.commit()

    total = Like.query.filter_by(**{k: v for k, v in filtro.items() if k != 'usuario_id'}).count()

    return jsonify(liked=liked, total_likes=total)


# ==========================================
# 7. COMENTÁRIOS (GENÉRICO)
# ==========================================

@app.route('/comentario/<tipo>/<int:id>', methods=['POST'])
@login_required
def comentar(tipo, id):
    texto = request.form.get('texto')

    if not texto:
        return jsonify({'error': 'Comentário vazio'}), 400

    if tipo == 'video':
        video = Video.query.get_or_404(id)
        comentario = Comentario(
            texto=texto,
            autor=current_user,
            video=video
        )

    elif tipo == 'post':
        post = Post.query.get_or_404(id)
        comentario = Comentario(
            texto=texto,
            autor=current_user,
            post=post
        )

    elif tipo == 'depoimento':
        depoimento = Depoimento.query.get_or_404(id)
        comentario = Comentario(
            texto=texto,
            autor=current_user,
            depoimento=depoimento
        )

    else:
        return jsonify({'error': 'Tipo inválido'}), 400

    database.session.add(comentario)
    database.session.commit()

    return jsonify({
        'id': comentario.id,
        'texto': comentario.texto,
        'usuario': current_user.username
    })



@app.route('/comentario/apagar/<int:comentario_id>', methods=['POST'])
@login_required
def apagar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)

    if comentario.usuario_id != current_user.id:
        abort(403)

    database.session.delete(comentario)
    database.session.commit()
    return jsonify(sucesso=True)


# ==========================================
# 8. FUNÇÕES AUXILIARES
# ==========================================

def salvar_imagem(imagem):
    pasta = os.path.join(app.root_path, 'static/fotos_perfil')
    os.makedirs(pasta, exist_ok=True)

    nome = secrets.token_hex(8) + os.path.splitext(imagem.filename)[1]
    caminho = os.path.join(pasta, nome)

    img = Image.open(imagem)
    img.thumbnail((400, 400))
    img.save(caminho)

    return nome



def salvar_video(arquivo):
    pasta = os.path.join(app.root_path, 'static/videos')
    os.makedirs(pasta, exist_ok=True)

    nome = secrets.token_hex(8) + os.path.splitext(arquivo.filename)[1]
    arquivo.save(os.path.join(pasta, nome))
    return nome



def salvar_thumbnail(imagem):
    pasta = os.path.join(app.root_path, 'static/thumbnails')
    os.makedirs(pasta, exist_ok=True)

    nome = secrets.token_hex(8) + os.path.splitext(imagem.filename)[1]
    caminho = os.path.join(pasta, nome)
    Image.open(imagem).save(caminho)
    return nome



def gerar_thumbnail_automatica(nome_video):
    import cv2  # IMPORTAÇÃO LOCAL (SAFE PARA PRODUÇÃO)

    caminho_video = os.path.join(app.root_path, 'static/videos', nome_video)
    nome_thumb = nome_video.rsplit('.', 1)[0] + '.jpg'
    caminho_thumb = os.path.join(app.root_path, 'static/thumbnails', nome_thumb)

    cap = cv2.VideoCapture(caminho_video)
    cap.set(cv2.CAP_PROP_POS_MSEC, 2000)
    sucesso, frame = cap.read()

    if sucesso:
        cv2.imwrite(caminho_thumb, frame)

    cap.release()
    return nome_thumb


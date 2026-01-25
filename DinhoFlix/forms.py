from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, length, Email, EqualTo, ValidationError
from DinhoFlix.models import Usuario, Video
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado! Faça login para continuar.')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), length(6, 20)])
    lembrar_dados = BooleanField('Lembrar dados de Acesso')
    botao_submit_fazerlogin = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'])])

    # Checkbox de cursos (conforme seu editarperfil.html utiliza)
    curso_excel = BooleanField('Excel')
    curso_vba = BooleanField('VBA')
    curso_python = BooleanField('Python')

    botao_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com este E-mail.')


class FormUploadVideo(FlaskForm):
    titulo = StringField('Título do Vídeo', validators=[DataRequired(), length(2, 100)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    # FileAllowed restringe o tipo de arquivo para segurança
    arquivo = FileField('Arquivo de Vídeo (MP4)', validators=[DataRequired(), FileAllowed(['mp4', 'mov'])])
    thumbnail = FileField('Capa do Vídeo (Thumbnail)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    botao_submit = SubmitField('Publicar Vídeo')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), length(2, 140)])
    corpo = TextAreaField('Conteúdo', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')

class FormDepoimento(FlaskForm):
    titulo = StringField('Título da sua Experiência', validators=[DataRequired(), length(2, 100)])
    corpo = TextAreaField('Conte o seu relato...', validators=[DataRequired()])
    botao_submit = SubmitField('Publicar Relato')
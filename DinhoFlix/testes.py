from main import app, database

#with app.app_context(): #Permite que o banco de dados seja rodado
#    database.create_all() #Cria um banco de dados

# ----- Cria um usuário dentro do banco de dados -----

# with app.app_context():
#     usuario = Usuario(username='Anderson Luiz', email='anddamere@gmail.com', senha='123456')
#     usuario2 = Usuario(username='Dinho', email='anddamere@hotmail.com', senha='123456')
#     database.session.add(usuario)
#     database.session.add(usuario2)
#     database.session.commit()
# with app.app_context():
#     meus_usuarios = Usuario.query.all()
#     print(meus_usuarios)
#     primeiro_usuario = Usuario.query.first()
#     print(primeiro_usuario.senha)

# ----- Cria um Post dentro do banco de dados -----

# with app.app_context():
#     meu_post = Post(id_usuario=1, titulo='Primeiro Post do Dinho', corpo='Dinho faz meu Site')
#     database.session.add(meu_post)
#     database.session.commit()

# ----- Exibe informações dentro do banco de dados -----

# with app.app_context():
#     post = Post.query.first()
#     print(post.titulo)
#     print(post.id_usuario)
#     print(post.corpo)
#     print(post.autor)

# ----- Limpa e recria o Banco de Dados(db)  -----

# with app.app_context():
#     database.drop_all()
#     database.create_all()
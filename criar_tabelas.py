from DinhoFlix import app, database

with app.app_context():
    database.create_all()
    print("Tabelas criadas com sucesso!")


from DinhoFlix import app, database

if __name__ == '__main__':
    with app.app_context():
        database.create_all() # Isso cria o arquivo .db do zero com as tabelas novas
    app.run(debug=True)
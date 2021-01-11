from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector, os
from helpers import login_required

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="yourpassword",
  database="meuplanejamento"
)

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(16)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        
        mycursor = mydb.cursor()
        sql = "SELECT * FROM users WHERE name = %s"
        val = (request.form.get("usuario"), )
        mycursor.execute(sql, val)
        
        myresult = mycursor.fetchall()
        
        if  len(myresult) != 1 or not check_password_hash(myresult[0][2], request.form.get("senha")):
            return "erro no login"
        session['id'] = myresult[0][0]
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/cadastrar', methods=['GET', 'POST'])
def registrar():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        mycursor = mydb.cursor()
        sql = "SELECT * FROM users WHERE name = %s"
        val = (request.form.get("nome"), )
        mycursor.execute(sql, val)
        
        myresult = mycursor.fetchall()
        
        if  len(myresult) > 0:
            return render_template("cadastrar_erro.html")

        # se passar em todas as validações, insere o usuário no banco
        sql = "INSERT INTO users (name, password) VALUES (%s, %s)"
        senha = request.form.get("senha1")
        # armazena o hash da senha
        hashed = generate_password_hash(senha)
        val = (request.form.get("nome"), hashed)
        mycursor.execute(sql, val)
        mydb.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("cadastrar.html")

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        texto = request.form.get('time')
        texto = texto.split(':')
        
        mycursor = mydb.cursor()
        sql = "INSERT INTO historico (disciplina, tempo, user_id) VALUES (%s, %s, %s)"
        val = (texto[1], texto[0], session['id'])
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('index'))

    else:        
        mycursor = mydb.cursor()
        sql = "SELECT name FROM disciplines WHERE users_id = %s"
        val = (session['id'], )
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        lista = []

        for tuplas in myresult:
            for disciplina in tuplas:
                lista.append(disciplina)        

        return render_template("index.html", disciplinas = lista)

@app.route('/disciplina', methods=['GET',  'POST'])
@login_required
def disciplina():
    if request.method == "POST":
        mycursor = mydb.cursor()
        sql = "INSERT INTO disciplines (name, users_id) VALUES (%s, %s)"
        val = (request.form.get('disciplina'), session['id'])
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('index'))
    else:
        return render_template("cadastrar_disciplina.html")

@app.route('/historico')
@login_required
def historico():
    mycursor = mydb.cursor()
    sql = "SELECT disciplina, tempo FROM historico WHERE user_id = %s"
    val = (session['id'], )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    
    return render_template("historico.html", dados=myresult)

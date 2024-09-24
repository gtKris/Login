from flask import Flask, request,session, redirect, url_for, render_template
import sqlite3
import hashlib
import os
import re

app = Flask(__name__ ,template_folder='../templates')

app.secret_key = 'fmdp' 

# Conectar a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('userdata.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla si no existe
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS userdata(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lastname TEXT NOT NULL,
            gmail TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Ruta de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el registro
@app.route('/register', methods=['POST'])
def register():
    
    name = request.form['name']
    lastname = request.form['lastname']
    gmail = request.form['gmail']
    username = request.form['username']
    password = request.form['password']

    # Generar un salt aleatorio
    salt = os.urandom(16).hex()
    # Combinar el salt con la contraseña antes de hashear
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    
    # Almacenar el salt y el hash juntos
    salted_hashed_password = salt + ':' + hashed_password

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verificar si el nombre de usuario ya existe
    cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
    existing_user = cur.fetchone()

    if existing_user:
        conn.close()
        return 'Username already exists!', 400

    try:
        cur.execute("INSERT INTO userdata (name, lastname, gmail, username, password) VALUES (?, ?, ?, ?, ?)", 
                    (name, lastname, gmail, username, salted_hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return 'Failed to register user.', 400
    conn.close()
    return redirect(url_for('index'))



# Ruta para el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Obtener la contraseña almacenada (que contiene el salt y el hash)
    cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return 'Invalid username or password!', 400

    # Verificar si el valor almacenado tiene el formato salt:hashed_password
    stored_password = user['password']
    if ':' not in stored_password:
        conn.close()
        return 'Password format invalid. Please reset your password.', 400

    # Separar el salt y el hash almacenados
    stored_salt, stored_hashed_password = stored_password.split(':')

    # Hashear la contraseña ingresada con el salt almacenado
    salted_password = password + stored_salt
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    # Comparar el hash calculado con el almacenado
    if hashed_password == stored_hashed_password:
        session['user_id'] = user['id']  # Guarda el user_id en la sesión
        conn.close()
        return redirect(url_for('profile'))  # Redirige al perfil del usuario
    else:
        conn.close()
        return 'Invalid username or password!', 400


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirigir al login si no está autenticado

    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session['user_id']

    # Si el método es POST, actualizar los datos
    if request.method == 'POST':
        new_email = request.form['gmail']
        new_password = request.form['password']
        
        # Validar correo electrónico
        email_pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, new_email):
            return 'Correo electrónico no válido.', 400

        # Validar contraseña (mínimo 8 caracteres si se ingresa)
        if new_password and len(new_password) < 8:
            return 'La contraseña debe tener al menos 8 caracteres.', 400

        # Hashear la nueva contraseña si es proporcionada
        if new_password:
            salt = os.urandom(16).hex()
            salted_password = new_password + salt
            hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
            salted_hashed_password = salt + ':' + hashed_password
        else:
            salted_hashed_password = None  # Mantener la contraseña actual

        # Actualizar los datos del usuario
        if new_email:
            cur.execute("UPDATE userdata SET gmail = ? WHERE id = ?", (new_email, user_id))
        if salted_hashed_password:
            cur.execute("UPDATE userdata SET password = ? WHERE id = ?", (salted_hashed_password, user_id))

        conn.commit()
        conn.close()
        return 'Datos actualizados exitosamente!', 200

    # Obtener los datos actuales del usuario
    cur.execute("SELECT * FROM userdata WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()

    return render_template('profile.html', user=user)


    

@app.route('/show_users')
def show_users():
    if 'user_id' not in session:
        return redirect(url_for('index')) 

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM userdata")
    users = cur.fetchall()
    conn.close()
    return render_template('show_users.html', users=users)


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Elimina el user_id de la sesión
    return redirect(url_for('index'))



if __name__ == '__main__':
    create_table()
    app.run(debug=True)

from flask import Flask, request,session, redirect, url_for, render_template
import sqlite3
import hashlib
import os
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from flask import flash 
from datetime import datetime, timedelta 
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
        session['message'] = '¡El nombre de usuario ya existe!'
        session['message_type'] = 'error'
        return 'Username already exists!', 400

    try:
        cur.execute("INSERT INTO userdata (name, lastname, gmail, username, password) VALUES (?, ?, ?, ?, ?)", 
                    (name, lastname, gmail, username, salted_hashed_password))
        conn.commit()
        session['message'] = 'Registro exitoso!'
        session['message_type'] = 'success'

    except sqlite3.IntegrityError:
        conn.close()
        session['message'] = '¡Fallo al registrar el usuario!'
        session['message_type'] = 'error'
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
        session['message'] = 'Credenciales incorrectas , por favor verifica de nuevo'
        session['message_type'] = 'error'
        return redirect(url_for('index'))

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
        session['message'] = '¡Credenciales incorrectas , por favor verifica de nuevo!'
        session['message_type'] = 'error'
        return redirect(url_for('index'))


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
            session['message'] = '¡Formato!'
            session['message_type'] = 'error'
            return 'Correo electrónico no válido.', 400
            

        # Validar contraseña (mínimo 8 caracteres si se ingresa)
        if new_password and len(new_password) < 8:
            session['message'] = '¡La contraseña debe tener al menos 8 caracteres!'
            session['message_type'] = 'error'
            return redirect(url_for('profile'))

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
        session['message'] = 'Los datos han sido actualizados correctamente'
        session['message_type'] = 'success'
        return redirect(url_for('index'))

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


def send_email_smtplib(recipient_email, reset_code):
    """Send an email using smtplib."""
   
    sender_email = "soportefacturas78@gmail.com"
    sender_password = "nuou hkri vqwq avth"
    
    # Configura el servidor SMTP de Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Crear el mensaje
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = "Código de restablecimiento de contraseña"
    
    # Cuerpo del correo
    body = f"Tu código de restablecimiento es: {reset_code}"
    message.attach(MIMEText(body, 'plain'))

    try:
        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar la conexión segura
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print(f"Correo enviado a {recipient_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        gmail = request.form['gmail']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM userdata WHERE gmail = ?", (gmail,))
        user = cur.fetchone()
        
        if not user:
            conn.close()
            session['message'] = 'Correo electronico no encontrado'
            session['message_type'] = 'error'
            return redirect(url_for('forgot_password'))

        # Generar un código de verificación de 6 dígitos
        reset_code = str(random.randint(100000, 999999))
        code_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

        # Actualizar tanto el código de verificación como la fecha de expiración
        cur.execute("UPDATE userdata SET reset_code = ?, code_expiry = ? WHERE gmail = ?", (reset_code, code_expiry, gmail))
        conn.commit()
        conn.close()

        # Enviar el código por correo usando smtplib
        send_email_smtplib(gmail, reset_code)

        flash(f"El código de verificación ha sido enviado a {gmail}")

        return redirect(url_for('verify_code', gmail=gmail))

    return render_template('forgot_password.html')



@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    gmail = request.args.get('gmail')
    
    if request.method == 'POST':
        entered_code = request.form['reset_code']
        new_password = request.form['new_password']
        
        # Obtener el código de la base de datos
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT reset_code, code_expiry FROM userdata WHERE gmail = ?", (gmail,))
        user = cur.fetchone()
        
        if not user:
            conn.close()
            session['message'] = 'Correo electronico no encontrado'
            session['message_type'] = 'error'
            return redirect(url_for('index'))

        reset_code = user['reset_code']
        code_expiry = datetime.strptime(user['code_expiry'], '%Y-%m-%d %H:%M:%S')  # Usar formato sin microsegundos

        # Verificar si el código ha expirado
        if datetime.now() > code_expiry:
            conn.close()
            session['message'] = 'El codigo ha expirado'
            session['message_type'] = 'error'
            return redirect(url_for('index'))

        # Verificar si el código coincide
        if entered_code != reset_code:
            conn.close()
            session['message'] = 'Codigo incorrecto'
            session['message_type'] = 'error'
            return redirect(url_for('index'))
        

        # Hashear la nueva contraseña
        salt = os.urandom(16).hex()
        salted_password = new_password + salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
        salted_hashed_password = salt + ':' + hashed_password

        # Actualizar la contraseña en la base de datos
        cur.execute("UPDATE userdata SET password = ?, reset_code = NULL, code_expiry = NULL WHERE gmail = ?", 
                    (salted_hashed_password, gmail))
        conn.commit()
        conn.close()

        session['message'] = 'La contraseña ha sido actualizada'
        session['message_type'] = 'success'
        return redirect(url_for('index'))

    return render_template('verify_code.html', gmail=gmail)


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Elimina el user_id de la sesión
    return redirect(url_for('index'))



if __name__ == '__main__':
    create_table()
    app.run(debug=True)

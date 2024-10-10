import imaplib
import email
from email.header import decode_header
import os

# Datos de acceso
USERNAME = 'soportefacturas78@gmail.com'
PASSWORD = 'nuou hkri vqwq avth'

# Conectar al servidor IMAP de Gmail
def conectar_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(USERNAME, PASSWORD)
    return mail

# Descargar PDFs de correos que contengan "Factura electrónica"
def descargar_pdfs_factura_electronica():
    mail = conectar_gmail()

    # Seleccionar el buzón de entrada
    mail.select('inbox')

    # Buscar correos en general en el buzón de entrada
    status, mensajes = mail.search(None, 'ALL')

    # Obtener lista de IDs de correos
    mensajes_ids = mensajes[0].split()

    for mail_id in mensajes_ids:
        # Obtener el correo por ID
        status, msg_data = mail.fetch(mail_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Decodificar el asunto (subject)
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # Si el asunto está en bytes, lo decodificamos
                    subject = subject.decode(encoding if encoding else 'utf-8')

                from_ = msg.get("From")
                print(f"De: {from_}")
                print(f"Asunto: {subject}")

                # Si el mensaje tiene múltiples partes
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # Buscar el cuerpo del mensaje en texto plano que contenga "Factura electrónica"
                        if "attachment" not in content_disposition:
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                if "Factura electrónica" in body:
                                    print("Se encontró 'Factura electrónica' en el cuerpo del correo.")
                                else:
                                    # Si no contiene "Factura electrónica", omitir este correo
                                    continue

                        # Si hay un archivo adjunto PDF
                        if "attachment" in content_disposition and "pdf" in content_type:
                            # Decodificar el nombre del archivo
                            filename = part.get_filename()
                            if filename:
                                # Crear una carpeta para guardar los PDFs si no existe
                                if not os.path.isdir("PDFs_Factura_Electronica"):
                                    os.makedirs("PDFs_Factura_Electronica")

                                # Guardar el archivo PDF
                                filepath = os.path.join("PDFs_Factura_Electronica", filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                    print(f"PDF guardado: {filepath}")
                else:
                    # Si no es multipart, obtener el cuerpo del mensaje
                    body = msg.get_payload(decode=True).decode()
                    if "Factura electrónica" in body:
                        print("Se encontró 'Factura electrónica' en el cuerpo del correo.")
                    else:
                        # Si no contiene "Factura electrónica", omitir este correo
                        continue

    # Cerrar la conexión
    mail.logout()

# Llamar la función para descargar PDFs con "Factura electrónica"
descargar_pdfs_factura_electronica()

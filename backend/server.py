from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import fitz  # PyMuPDF
import pytesseract
import psycopg2
from PIL import Image
import io
from supabase import create_client
from dotenv import load_dotenv

import logging



# 📌 Cargar variables de entorno
load_dotenv()

# 📌 Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📌 Conectar a Supabase PostgreSQL
try:
    conn = psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )
    cursor = conn.cursor()
    print("✅ Conexión a la base de datos exitosa.")
except Exception as e:
    print(f"❌ Error al conectar a la base de datos: {e}")
    exit()

# 📌 Configurar Flask
app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde React

# 📌 Carpeta de subida local
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/api/upload", methods=["POST"])
def upload_pdf():
    app.logger.info("🔄 Recibiendo archivo...")

    if 'file' not in request.files:
        app.logger.error("❌ No se encontró la clave 'file' en la solicitud")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("❌ No se seleccionó ningún archivo")
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        file.save(file_path)
        app.logger.info(f"✅ Archivo guardado localmente: {file_path}")
    except Exception as e:
        app.logger.error(f"❌ Error al guardar archivo localmente: {e}")
        return jsonify({"error": "Error saving file"}), 500

    try:
        # 📌 Subir PDF a Supabase Storage
        app.logger.info("🔄 Subiendo PDF a Supabase Storage...")
        public_url = upload_to_supabase(file_path)
        app.logger.info(f"✅ PDF subido con URL: {public_url}")
    except Exception as e:
        app.logger.error(f"❌ Error en la subida a Supabase: {e}")
        return jsonify({"error": "Error uploading to Supabase"}), 500

    try:
        # 📌 Extraer texto del PDF con OCR
        app.logger.info("🔄 Ejecutando OCR para extraer texto...")
        extracted_text = extract_text_from_pdf(file_path)
        app.logger.info("✅ Texto extraído con éxito.")
    except Exception as e:
        app.logger.error(f"❌ Error en OCR: {e}")
        return jsonify({"error": "Error in OCR processing"}), 500

    try:
        # 📌 Guardar en la base de datos
        app.logger.info("🔄 Guardando en la base de datos...")
        save_document_to_db(file.filename, public_url, extracted_text)
        app.logger.info("✅ Documento guardado en la base de datos.")
    except Exception as e:
        app.logger.error(f"❌ Error al guardar en la base de datos: {e}")
        return jsonify({"error": "Error saving to database"}), 500

    return jsonify({
        "message": "File uploaded and processed successfully",
        "public_url": public_url,
        "extracted_text": extracted_text
    })



# 📌 Función para subir archivos a Supabase Storage
def upload_to_supabase(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()

    file_name = os.path.basename(file_path)
    bucket_name = "documents"
    
    response = supabase.storage.from_(bucket_name).upload(file_name, file_data)
    
    if response is None:
        raise Exception("❌ Error al subir el archivo a Supabase Storage")

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
    return public_url


# 📌 Función para extraer texto de PDF escaneado con OCR
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""

    for i in range(len(doc)):
        for img in doc[i].get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]

            img = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(img, lang="spa")
            extracted_text += text + "\n\n"

    return extracted_text.strip()


# 📌 Función para guardar documento y texto en la base de datos
def save_document_to_db(name, pdf_url, extracted_text):
    try:
        cursor.execute(
            "INSERT INTO documents (name, document_url) VALUES (%s, %s) RETURNING id",
            (name, pdf_url)
        )
        document_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO document_text (document_id, extracted_text) VALUES (%s, %s)",
            (document_id, extracted_text)
        )

        conn.commit()
        app.logger.info(f"✅ Documento '{name}' guardado en Supabase con ID {document_id}")

    except Exception as e:
        app.logger.error(f"❌ Error al guardar en la base de datos: {e}")
        conn.rollback()


# 📌 Ruta para obtener la lista de documentos
@app.route("/api/documents", methods=["GET"])
def get_documents():
    try:
        cursor.execute("SELECT id, name, document_url FROM documents ORDER BY id DESC")
        documents = cursor.fetchall()

        return jsonify([
            {"id": row[0], "name": row[1], "url": row[2]}
            for row in documents
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📌 Iniciar el servidor
if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True)

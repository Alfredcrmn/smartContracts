from flask import Flask, jsonify, request
from flask_cors import CORS  # Para manejar CORS
import os
import fitz  # PyMuPDF para leer PDFs
import pytesseract
import psycopg2  # Conexión a PostgreSQL en Supabase
from PIL import Image
import io
from supabase import create_client
from dotenv import load_dotenv

# 📌 Cargar variables de entorno desde .env
load_dotenv()

# 📌 Variables de conexión a Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# 📌 Conectar a Supabase Storage
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📌 Conectar a Supabase PostgreSQL
try:
    conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    cursor = conn.cursor()
    print("✅ Conexión a la base de datos exitosa.")

except Exception as e:
    print(f"❌ Error al conectar a la base de datos: {e}")
    exit()

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde React

@app.route("/api/upload", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Subir PDF a Supabase Storage
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    file_name = os.path.basename(file_path)
    storage_path = f"documents/{file_name}"
    response = supabase.storage.from_("documents").upload(file_name, file_data)
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/documents/{file_name}"

    # Extraer texto del PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Guardar en la base de datos
    save_document_to_db(file_name, public_url, extracted_text)

    return jsonify({"message": "File uploaded and processed successfully", "public_url": public_url, "extracted_text": extracted_text})

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
        print(f"✅ Documento '{name}' guardado en Supabase con ID {document_id}")

    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")
        conn.rollback()

if __name__ == "__main__":
    app.run(debug=True)
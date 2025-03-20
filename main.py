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


# 📌 1️⃣ Subir PDF a Supabase Storage
def upload_pdf_to_supabase(pdf_path, bucket="documents"):
    with open(pdf_path, "rb") as file:
        file_data = file.read()
    
    file_name = os.path.basename(pdf_path)  # Nombre del archivo
    storage_path = f"{bucket}/{file_name}"  # Ruta en Supabase Storage

    # Subir el archivo
    response = supabase.storage.from_(bucket).upload(file_name, file_data)

    # Obtener la URL pública del archivo
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_name}"
    return public_url


# 📌 2️⃣ Extraer texto de un PDF escaneado con OCR
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)  # Abrir el PDF
    extracted_text = ""

    for i in range(len(doc)):  # Recorre cada página
        for img in doc[i].get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]

            # Convertir bytes a imagen
            img = Image.open(io.BytesIO(img_bytes))

            # Aplicar OCR
            text = pytesseract.image_to_string(img, lang="spa")
            extracted_text += text + "\n\n"

    return extracted_text.strip()


# 📌 3️⃣ Guardar en Supabase (Documents + Document Text)
def save_document_to_db(name, pdf_url, extracted_text):
    try:
        # Insertar en `documents`
        cursor.execute(
            "INSERT INTO documents (name, document_url) VALUES (%s, %s) RETURNING id",
            (name, pdf_url)
        )
        document_id = cursor.fetchone()[0]  # Obtener el ID del documento insertado

        # Insertar en `document_text`
        cursor.execute(
            "INSERT INTO document_text (document_id, extracted_text) VALUES (%s, %s)",
            (document_id, extracted_text)
        )

        conn.commit()
        print(f"✅ Documento '{name}' guardado en Supabase con ID {document_id}")

    except Exception as e:
        print(f"❌ Error al guardar en la base de datos: {e}")
        conn.rollback()


# 📌 4️⃣ Ejecutar el proceso completo
def process_pdf(pdf_path):
    print("📄 Subiendo PDF a Supabase Storage...")
    pdf_url = upload_pdf_to_supabase(pdf_path)
    print(f"✅ PDF subido: {pdf_url}")

    print("🔍 Extrayendo texto con OCR...")
    extracted_text = extract_text_from_pdf(pdf_path)
    print("✅ Texto extraído correctamente.")

    print("📦 Guardando en la base de datos...")
    save_document_to_db(os.path.basename(pdf_path), pdf_url, extracted_text)

    print("🚀 Proceso completado.")


# 📌 Ejecutar con un PDF de prueba
pdf_file = "test2.pdf"
process_pdf(pdf_file)

# 📌 Cerrar conexión a la base de datos
cursor.close()
conn.close()

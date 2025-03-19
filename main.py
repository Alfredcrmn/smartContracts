import fitz  # PyMuPDF para leer PDFs
import pytesseract
from PIL import Image
import io

# Nombre del PDF en la misma carpeta que el script
pdf_path = "testSemana.pdf"

# Función para extraer imágenes de un PDF
def extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)  # Abrimos el PDF
    images = []

    for i in range(len(doc)):  # Iteramos sobre cada página
        for img in doc[i].get_images(full=True):  # Extraemos imágenes
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            images.append(img_bytes)  # Guardamos la imagen en bytes

    return images  # Lista de imágenes extraídas

# Función para aplicar OCR a una imagen
def ocr_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))  # Convertir bytes en imagen
    text = pytesseract.image_to_string(img, lang='spa')  # Extraer texto (OCR en español)
    return text.strip()  # Limpiar texto extraído

# Ejecutar el proceso
print("📄 Procesando PDF...")
images = extract_images_from_pdf(pdf_path)  # Extraer imágenes

print(f"🔍 Se encontraron {len(images)} páginas con imágenes.")

# Aplicar OCR a cada imagen extraída
for i, img_bytes in enumerate(images):
    print(f"\n📜 **Texto de la Página {i+1}:**\n")
    extracted_text = ocr_image(img_bytes)
    print(extracted_text)
    print("=" * 50)  # Separador entre páginas

print("\n✅ OCR completado.")

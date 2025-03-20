# smartContracts

📂 Gestor de Documentos con OCR y Búsqueda en Supabase
Un sistema que permite subir documentos PDF, extraer su texto con OCR, almacenarlos en Supabase y buscarlos por nombre o contenido.


📌 Captura de pantalla de la aplicación (Actualiza con una imagen real de tu app).

🚀 Características

✅ Subida de documentos PDF desde la interfaz.
✅ OCR (Reconocimiento de Texto) para extraer contenido de PDFs escaneados.
✅ Almacenamiento en Supabase (tanto los archivos como el texto extraído).
✅ Búsqueda avanzada por nombre del documento y contenido extraído.
✅ Interfaz moderna y minimalista desarrollada en React.

🛠 Tecnologías Usadas

Tecnología	Descripción
Python (Flask)	Backend API para manejar archivos y OCR
Tesseract OCR	Extrae texto de imágenes en los PDFs
PostgreSQL (Supabase)	Base de datos para almacenar documentos
React.js	Interfaz web interactiva
Axios	Conexión entre frontend y backend
Material UI / CSS Flat	Diseño moderno y responsivo
📥 Instalación
Sigue estos pasos para instalar y ejecutar el proyecto en tu máquina local.

🔹 1️⃣ Clonar el Repositorio

git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio

🔹 2️⃣ Configurar el Backend (Flask + Supabase)

cd backend
python -m venv venv      # Crear entorno virtual
source venv/bin/activate # En macOS/Linux
# En Windows: venv\Scripts\activate
pip install -r requirements.txt

🔹 3️⃣ Configurar las Variables de Entorno

Crea un archivo .env en la carpeta backend con los siguientes valores:


SUPABASE_URL=tu-url-de-supabase
SUPABASE_KEY=tu-api-key
user=postgres
password=tu-password
host=tu-host-de-supabase
port=6543
dbname=postgres

🔹 4️⃣ Iniciar el Servidor Flask

python server.py
📌 El servidor correrá en http://127.0.0.1:5000.

🔹 5️⃣ Configurar el Frontend (React)

cd frontend
npm install
npm start

📌 La aplicación web se abrirá en http://localhost:3000.

✨ Uso de la Aplicación

1️⃣ Sube un PDF desde la interfaz.
2️⃣ Espera la extracción de texto con OCR.
3️⃣ Consulta el documento guardado en la lista de documentos.
4️⃣ Usa la barra de búsqueda para encontrar archivos por nombre o contenido.

📦 Estructura del Proyecto

📂 tu-repositorio/
 ├── 📂 backend/         # Backend en Flask
 │   ├── server.py       # API principal
 │   ├── requirements.txt # Librerías de Python
 │   ├── .env.example    # Configuración de Supabase
 ├── 📂 frontend/        # Frontend en React
 │   ├── src/            # Código fuente
 │   ├── public/         # Archivos estáticos
 │   ├── App.js          # Componente principal
 │   ├── App.css         # Estilos de la app
 │   ├── package.json    # Dependencias de React
 ├── README.md           # Documentación del proyecto
 ├── .gitignore          # Archivos ignorados por Git

 
🤝 Contribuciones
¡Toda contribución es bienvenida! Sigue estos pasos para contribuir:

Haz un Fork del repositorio.
Crea una rama (git checkout -b nueva-feature).
Realiza cambios y haz un commit (git commit -m "Agrega nueva feature").
Envía un Pull Request (git push origin nueva-feature).


📄 Licencia
Este proyecto está bajo la Licencia MIT. Puedes usarlo libremente, pero no olvides dar crédito. 📜


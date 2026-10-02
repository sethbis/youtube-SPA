# Plataforma de Videos - React, FastAPI y AWS

Este proyecto implementa una Single Page Application (SPA) para una plataforma de videos siguiendo una arquitectura modular basada en servicios de Amazon Web Services (AWS).

---

## 1. Arquitectura del Sistema

- **Frontend (SPA):** React + Vite. Alojado como sitio web estatico en Amazon S3 (Bucket Frontend).
- **Backend (API REST):** FastAPI desplegado en una instancia Amazon EC2 (Ubuntu). Documentacion interactiva en `/docs`.
- **Base de Datos:** Amazon RDS (PostgreSQL o MySQL). Almacena unicamente datos relacionales estructurados.
- **Almacenamiento de Medios:** Amazon S3 dividido en dos buckets dedicados:
  - Bucket Videos: Almacena archivos en formato MP4 (tamano maximo 100 MB).
  - Bucket Miniaturas: Almacena imagenes en formato JPG, JPEG o PNG.
- **Seguridad y Acceso:**
  - IAM Role adjunto a la instancia EC2 para acceso seguro a S3 sin almacenar credenciales en codigo.
  - Security Groups para aislar el acceso a la base de datos RDS unicamente desde la IP/Security Group de la instancia EC2.
  - Variables de entorno tanto en EC2 como en el cliente web.

---

## 2. Estructura Modular del Proyecto

```text
Parcial-1/
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- config.py             # Configuracion y lectura de variables de entorno
|   |   |-- database.py           # Conexion SQLAlchemy y sesion de base de datos
|   |   |-- models.py             # Entidades User, Video y Comment
|   |   |-- schemas.py            # Esquemas Pydantic para peticiones y respuestas
|   |   |-- services/
|   |   |   |-- auth_service.py   # Hashing de contrasenas y generacion de JWT
|   |   |   |-- s3_service.py     # Subida y eliminacion de archivos en Amazon S3
|   |   |-- routers/
|   |   |   |-- auth.py           # Endpoints de usuarios y autenticacion
|   |   |   |-- videos.py         # Endpoints de gestion y catalogo de videos
|   |   |   |-- comments.py       # Endpoints de comentarios
|   |   |-- main.py               # Instancia de FastAPI, CORS y middleware
|   |-- requirements.txt          # Dependencias de Python
|   |-- .env.example              # Plantilla de variables de entorno para backend
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |   |-- Navbar.jsx        # Barra de navegacion principal
|   |   |   |-- VideoCard.jsx     # Tarjeta reutilizable de video para catalogos
|   |   |-- pages/
|   |   |   |-- AuthPage.jsx      # Pagina 1: Registro e Inicio de sesion
|   |   |   |-- HomePage.jsx      # Pagina 2: Catalogo principal de videos
|   |   |   |-- WatchPage.jsx     # Pagina 3: Reproductor, comentarios y recomendados
|   |   |   |-- ProfilePage.jsx   # Pagina 4: Perfil de usuario y gestion de videos
|   |   |-- services/
|   |   |   |-- api.js            # Cliente Axios configurado para FastAPI
|   |   |-- context/
|   |   |   |-- AuthContext.jsx   # Estado global de autenticacion del usuario
|   |   |-- App.jsx               # Enrutamiento de las 4 paginas de la SPA
|   |   |-- main.jsx              # Punto de entrada de React
|   |   |-- index.css             # Diseno visual limpio y responsivo
|   |-- index.html
|   |-- vite.config.js
|   |-- package.json
|   |-- .env.example              # Plantilla de variables de entorno para frontend
|-- deploy/
|   |-- fastapi.service           # Archivo de servicio systemd para EC2
|   |-- nginx.conf                # Configuracion de proxy inverso Nginx
|   |-- setup_ec2.sh              # Script de aprovisionamiento para EC2
|   |-- s3_cors.json              # Configuracion de CORS para buckets de S3
|   |-- s3_frontend_policy.json   # Politica publica para el bucket de Frontend
|-- .gitignore
|-- README.md
```

---

## 3. Entidades de Base de Datos (Amazon RDS)

### Usuario (`users`)
- `id`: Entero, clave primaria autoincremental.
- `name`: Cadena de texto con el nombre del usuario.
- `email`: Cadena de texto unica indexada.
- `password_hash`: Hash seguro de la contrasena (bcrypt).
- `created_at`: Fecha y hora de registro.

### Video (`videos`)
- `id`: Entero, clave primaria autoincremental.
- `title`: Titulo del video.
- `description`: Descripcion detallada del video.
- `video_url`: URL publica del archivo MP4 alojado en S3 Bucket Videos.
- `thumbnail_url`: URL publica de la imagen alojada en S3 Bucket Miniaturas.
- `views`: Contador de reproducciones (inicia en 0).
- `user_id`: Clave foranea que referencia a `users.id`.
- `created_at`: Fecha y hora de publicacion.

### Comentario (`comments`)
- `id`: Entero, clave primaria autoincremental.
- `content`: Texto del comentario publicado.
- `user_id`: Clave foranea que referencia a `users.id`.
- `video_id`: Clave foranea que referencia a `videos.id`.
- `created_at`: Fecha y hora de creacion.

---

## 4. Endpoints de la API FastAPI

### Usuarios
- `POST /users`: Registra un nuevo usuario (`name`, `email`, `password`).
- `POST /login`: Autentica al usuario y retorna token JWT y datos de perfil.
- `GET /users/{id}`: Obtiene el perfil del usuario y el conteo de videos publicados.

### Videos
- `POST /videos`: Publica un nuevo video recibiendo `title`, `description`, `video_file` (MP4, max 100MB) y `thumbnail_file` (JPG/PNG). Sube los archivos a S3 y guarda la referencia en RDS. Requiere token Bearer.
- `GET /videos`: Retorna la lista de videos ordenada por fecha descendente. Permite filtros por `user_id`, `exclude_id` y `limit`.
- `GET /videos/{id}`: Retorna el detalle del video e incrementa en 1 su contador de vistas.
- `PUT /videos/{id}`: Permite al autor del video actualizar el titulo y descripcion.
- `DELETE /videos/{id}`: Permite al autor del video eliminar el registro y los archivos de S3.

### Comentarios
- `POST /videos/{id}/comments`: Agrega un nuevo comentario al video indicado. Requiere token Bearer.
- `GET /videos/{id}/comments`: Lista cronologicamente los comentarios asociados al video.

### Documentacion
- `/docs`: Interfaz Swagger UI interactiva.

---

## 5. Paginas de la SPA (React)

- **Pagina 1 (Registro / Login - `/auth`):** Permite alternar entre formulario de creacion de cuenta e inicio de sesion con validaciones de nombre, correo y contrasena.
- **Pagina 2 (Principal - `/`):** Catalogo interactivo que presenta la miniatura, titulo, usuario publicador, numero de vistas y fecha de publicacion de cada video.
- **Pagina 3 (Reproductor - `/watch/:id`):** Reproduce el video seleccionado, muestra sus metadatos (titulo, descripcion, autor, vistas), lista y permite anadir comentarios, y despliega una seccion lateral con videos recomendados obtenidos dinamicamente de la API.
- **Pagina 4 (Perfil del usuario - `/profile`):** Informacion del usuario autenticado, cantidad de videos publicados, formulario de subida de video con validacion de archivos, y listado de sus videos con opciones para consultar, actualizar y eliminar.

---

## 6. Procedimiento de Despliegue en AWS

### Paso 1: Creacion de los 3 Buckets en Amazon S3

1. **Bucket 1 (Frontend):**
   - Nombre sugerido: `video-platform-frontend-tu-nombre`
   - Desmarcar la opcion "Bloquear todo el acceso publico".
   - En la pestana "Propiedades", habilitar "Alojamiento de sitios web estaticos" (Documento de indice: `index.html`, Documento de error: `index.html`).
   - En la pestana "Permisos" -> "Politica de bucket", aplicar el contenido de `deploy/s3_frontend_policy.json` reemplazando el nombre del bucket.

2. **Bucket 2 (Videos):**
   - Nombre sugerido: `video-platform-videos-tu-nombre`
   - Configurar la politica de CORS utilizando `deploy/s3_cors.json`.

3. **Bucket 3 (Miniaturas):**
   - Nombre sugerido: `video-platform-thumbnails-tu-nombre`
   - Configurar la politica de CORS utilizando `deploy/s3_cors.json`.

### Paso 2: Base de Datos en Amazon RDS

1. Crear una base de datos PostgreSQL o MySQL (db.t3.micro o db.t4g.micro en Free Tier).
2. Asignar un usuario administrador y contrasena segura.
3. En el Security Group de RDS, permitir trafico de entrada en el puerto 5432 (PostgreSQL) o 3306 (MySQL) unicamente desde la IP o Security Group de la instancia EC2.
4. Obtener el endpoint de conexion de RDS.

### Paso 3: Servidor en Amazon EC2

1. Lanzar una instancia EC2 Ubuntu 24.04 LTS (t2.micro o t3.micro).
2. Crear un rol IAM con la politica `AmazonS3FullAccess` y asociarlo a la instancia EC2 (Acciones -> Seguridad -> Modificar rol IAM). Esto permite a FastAPI interactuar con S3 sin usar credenciales hardcodeadas.
3. En el Security Group de EC2, habilitar puertos:
   - 22 (SSH)
   - 80 (HTTP)
   - 8000 (Opcional para pruebas directas de FastAPI)

### Paso 4: Despliegue de FastAPI en EC2

1. Conectarse a la instancia por SSH:
   ```bash
   ssh -i tu-clave.pem ubuntu@IP_PUBLICA_EC2
   ```
2. Clonar el repositorio en `/home/ubuntu/Parcial-1`:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO> /home/ubuntu/Parcial-1
   ```
3. Crear el archivo de entorno en el backend `/home/ubuntu/Parcial-1/backend/.env`:
   ```env
   DATABASE_URL=postgresql://usuario:contrasena@tu-rds-endpoint:5432/videodb
   SECRET_KEY=clave_secreta_jwt_muy_segura
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   AWS_REGION=us-east-1
   S3_BUCKET_VIDEOS=video-platform-videos-tu-nombre
   S3_BUCKET_THUMBNAILS=video-platform-thumbnails-tu-nombre
   S3_BUCKET_FRONTEND=video-platform-frontend-tu-nombre
   ```
4. Ejecutar el script automatizado de instalacion y configuracion:
   ```bash
   chmod +x /home/ubuntu/Parcial-1/deploy/setup_ec2.sh
   /home/ubuntu/Parcial-1/deploy/setup_ec2.sh
   ```
5. Verificar el funcionamiento del servicio:
   ```bash
   sudo systemctl status fastapi
   ```
6. Abrir en el navegador: `http://IP_PUBLICA_EC2/docs`

### Paso 5: Compilacion y Despliegue del Frontend en S3

1. En la carpeta `frontend/`, crear el archivo `.env` indicando la URL publica de la API:
   ```env
   VITE_API_URL=http://IP_PUBLICA_EC2
   ```
2. Compilar la aplicacion:
   ```bash
   npm install
   npm run build
   ```
   Esto generara la carpeta `dist/`.
3. Subir unicamente el contenido interno de `frontend/dist/` al Bucket 1 (Frontend) de S3:
   - Mediante AWS Console: Cargar los archivos que estan dentro de `dist/` (incluyendo `index.html` y la carpeta `assets/`).
   - O mediante AWS CLI:
     ```bash
     aws s3 sync frontend/dist/ s3://video-platform-frontend-tu-nombre --delete
     ```
4. Abrir la URL publica del Bucket S3 de Alojamiento estatico.

---

## 7. Lista de Evidencias para Entrega

1. **Repositorio:** Enlace a GitHub o GitLab con el codigo modular.
2. **URL Publica SPA:** Enlace al sitio web estatico en Amazon S3.
3. **URL Publica API:** Enlace a `http://IP_PUBLICA_EC2/docs`.
4. **Capturas de AWS:**
   - Instancia EC2 en ejecucion con IAM Role asignado y Security Group.
   - Base de datos Amazon RDS activa y accesible desde EC2.
   - Los tres buckets S3 creados con sus archivos cargados (Frontend, Videos, Miniaturas).
5. **Capturas de Funcionalidad de la SPA:**
   - Formulario de Registro de usuario.
   - Formulario de Inicio de Sesion.
   - Pagina Principal con el catalogo dinamico de videos.
   - Pagina de Reproductor con reproduccion del video y datos.
   - Publicacion y visualizacion de comentarios.
   - Seccion de videos recomendados cargados dinamicamente.
   - Perfil de usuario con contador de videos y formulario de publicacion.
   - Modificacion y eliminacion de videos desde el perfil.
6. **Video Explicativo:** Grabacion breve demostrando la arquitectura en AWS y el flujo funcional de la aplicacion.

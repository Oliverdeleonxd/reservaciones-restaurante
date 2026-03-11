# 🍽️ App Reservas de Restaurante

  

Sistema web para gestión de reservas de restaurante. Los clientes pueden consultar disponibilidad y reservar mesas, y el administrador puede gestionar mesas, horarios y reservas.

  

## 🚀 URLs de Producción

  

| Servicio | URL |

|----------|-----|

| **Frontend** | https://reservaciones-restaurante.vercel.app |

| **Backend API** | https://web-production-01d3e.up.railway.app/api |

| **Admin Django** | https://web-production-01d3e.up.railway.app/admin |

  

### 👤 Usuario Admin Demo

- **Usuario:** `admin`

- **Contraseña:** `admin123`

  

---

## 📦 Repositorios

| Repositorio | URL |
|-------------|-----|
| **Backend** | https://github.com/Oliverdeleonxd/reservaciones-restaurante |
| **Frontend** | https://github.com/Oliverdeleonxd/reservaciones-restaurante-frontend |


## 🛠️ Stack Tecnológico

  

**Backend**

- Python 3.10 + Django 5.x

- Django REST Framework

- PostgreSQL

- JWT (djangorestframework-simplejwt)

- Gunicorn + WhiteNoise

  

**Frontend**

- Vue 3 + Vite

- Vue Router 4

- Pinia

- Axios

  

---

  

## ⚙️ Correr Localmente

  

### Backend

  

```bash

# 1. Clonar el repositorio

git clone https://github.com/Oliverdeleonxd/reservaciones-restaurante.git

cd reservaciones-restaurante



  

# 2. Crear entorno virtual

python -m venv venv

source venv/bin/activate # Linux/Mac

# venv\Scripts\activate # Windows

  

# 3. Instalar dependencias

pip install -r requirements.txt

  

# 4. Crear archivo .env

cp .env.example .env

# Editar .env con tus valores

  

# 5. Crear base de datos PostgreSQL

createdb reservaciones_db

  

# 6. Ejecutar migraciones

python manage.py migrate

  

# 7. Crear superusuario

python manage.py createsuperuser

  

# 8. Levantar servidor

python manage.py runserver

```

  

### Frontend

  

```bash

cd frontend

  

# Instalar dependencias

npm install

  

# Crear archivo .env

echo "VITE_API_URL=http://127.0.0.1:8000/api" > .env.local

  

# Levantar servidor de desarrollo

npm run dev

```

  

---

  

## 🔐 Variables de Entorno

  

### Backend (`.env`)

  

```env

SECRET_KEY=tu-clave-secreta-aqui

DEBUG=False

DATABASE_URL=postgresql://usuario:password@host:5432/nombre_db

ALLOWED_HOSTS=tu-dominio.railway.app,localhost

CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app,http://localhost:5173

```

  

### Frontend (`.env.local`)

  

```env

VITE_API_URL=https://web-production-01d3e.up.railway.app/api

```

  

---

  

## 📡 API Endpoints

  

### Públicos

  

| Método | Endpoint | Descripción |

|--------|----------|-------------|

| `GET` | `/api/availability/?date=YYYY-MM-DD&personas=N` | Consultar horarios disponibles |

| `POST` | `/api/reservations/` | Crear reserva |

| `POST` | `/api/reservations/cancel/<uuid>/` | Cancelar reserva con código |

  

### Admin (requiere JWT)

  

| Método | Endpoint | Descripción |

|--------|----------|-------------|

| `POST` | `/api/auth/login/` | Login → obtener token JWT |

| `POST` | `/api/auth/refresh/` | Renovar token JWT |

| `GET/POST` | `/api/mesas/` | Listar / crear mesas |

| `PUT/DELETE` | `/api/mesas/<id>/` | Editar / eliminar mesa |

| `GET` | `/api/reservaciones/` | Listar todas las reservas |

| `POST` | `/api/admin-panel/reservations/<id>/cancel/` | Cancelar reserva (admin) |

| `GET` | `/api/admin-panel/metrics/` | Métricas de ocupación |

  

### Ejemplo: Crear Reserva

  

```json

POST /api/reservations/

{

"nombre": "Daniel Pérez",

"email": "daniel@email.com",

"telefono": "555-1234",

"fecha": "2026-03-15",

"hora": "19:00",

"personas": 3

}

```

  

### Ejemplo: Login Admin

  

```json

POST /api/auth/login/

{

"username": "admin",

"password": "admin123"

}

```

  

---

  

## 🧠 Lógica de Negocio

  

- ❌ No se puede reservar en el pasado

- ❌ No se puede reservar fuera del horario del restaurante

- ❌ No se puede reservar si no hay mesa con capacidad suficiente

- ❌ Una mesa no puede tener 2 reservas simultáneas

- ✅ Asignación automática de mesa disponible

- ✅ Concurrencia manejada con `select_for_update()` + `@transaction.atomic`

  

---

  

## 🧪 Tests

  

```bash

cd reservaciones-restaurante

source venv/bin/activate

python manage.py test reservaciones

```

  

**Tests incluidos:**

- `test_reservacion_valida` — Crea una reserva correctamente

- `test_reservacion_en_pasado` — Rechaza fechas pasadas

- `test_horario_invalido` — Rechaza horarios fuera de rango

- `test_sin_mesas_disponibles` — Error cuando no hay mesas libres

- `test_capacidad_insuficiente` — Error cuando no hay capacidad

- `test_cancelar_con_codigo` — Cancelación con código UUID

  

---

  

## 🚀 Despliegue

  

### Backend en Railway

  

1. Crear proyecto en [railway.app](https://railway.app)

2. Agregar servicio desde GitHub

3. Agregar servicio PostgreSQL

4. Configurar variables de entorno:

- `SECRET_KEY`

- `DEBUG=False`

- `DATABASE_URL=${{Postgres.DATABASE_URL}}`

- `ALLOWED_HOSTS`

- `CORS_ALLOWED_ORIGINS`

5. Railway detecta automáticamente Python y usa `requirements.txt`

  

### Frontend en Vercel

  

```bash

npm install -g vercel

vercel

vercel env add VITE_API_URL # URL del backend Railway

vercel --prod

```

  

---

  

## 📁 Estructura del Proyecto

  

```

reservaciones-restaurante/

├── config/

│ ├── settings.py

│ ├── urls.py

│ └── wsgi.py

├── reservaciones/

│ ├── models.py # Mesa, Reservacion, ConfiguracionRestaurante

│ ├── serializers.py # Validaciones de entrada

│ ├── services.py # Lógica de negocio (Service Layer)

│ ├── views.py # Endpoints API

│ ├── urls.py

│ ├── admin.py

│ └── tests.py

├── requirements.txt

├── Procfile

└── README.md

  

frontend/

├── src/

│ ├── views/

│ │ ├── HomeView.vue # Formulario de reserva

│ │ ├── ConfirmacionView.vue # Confirmación + código cancelación

│ │ ├── CancelarView.vue # Cancelar con código

│ │ ├── AdminView.vue # Panel administrador

│ │ └── LoginView.vue # Login JWT

│ ├── stores/

│ │ └── auth.js # Pinia store autenticación

│ ├── services/

│ │ └── api.js # Axios + interceptor JWT

│ └── router/

│ └── index.js

├── package.json

└── vite.config.js

```
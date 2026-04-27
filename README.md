# clima-org-mvp

Sistema MVP para el análisis de clima organizacional y detección temprana de burnout mediante encuestas periódicas anónimas.

El instrumento combina el **MBI simplificado (9 ítems)** — que mide agotamiento emocional, despersonalización y logro personal — con **6 ítems de clima organizacional** que cubren comunicación, reconocimiento, carga de trabajo, relaciones, autonomía y liderazgo.

---

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) con WSL2 habilitado (Windows) o Docker Engine (Linux/macOS)

No se necesita Python, pip ni ninguna dependencia local.

---

## Quick Start

```bash
# 1. Clonar y entrar al directorio
git clone <repo-url>
cd clima-org-mvp

# 2. Crear .env desde el ejemplo
cp .env.example .env
# Editar ADMIN_API_KEY con un valor seguro antes de continuar

# 3. Levantar servicios
docker compose up --build

# 4. Acceder a los servicios
# API REST + docs interactivos: http://localhost:8000/docs
# Dashboard analítico:          http://localhost:8501
```

Los datos persisten en `./data/clima.db` (SQLite montado como volumen).

---

## Flujo de uso completo

### 1. Crear una campaña

```bash
curl -X POST http://localhost:8000/admin/surveys \
  -H "X-Admin-Key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Q1 2026","campaign_date":"2026-04-01"}'
```

### 2. Activar la campaña

```bash
# Reemplazar {SURVEY_ID} con el id devuelto en el paso anterior
curl -X PATCH http://localhost:8000/admin/surveys/{SURVEY_ID}/status \
  -H "X-Admin-Key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

### 3. Generar tokens para un departamento

```bash
curl -X POST http://localhost:8000/admin/surveys/{SURVEY_ID}/tokens \
  -H "X-Admin-Key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"department":"Engineering","count":3}'
```

La respuesta devuelve la lista de tokens generados.

### 4. Compartir el link con los empleados

```
http://localhost:8000/surveys/{SURVEY_ID}?token={TOKEN}
```

Cada token es de un solo uso y permite completar la encuesta de forma anónima.

### 5. Ver resultados en el dashboard

```
http://localhost:8501
```

El dashboard actualiza los resultados en tiempo real a medida que llegan las respuestas.

---

## Variables de entorno

| Variable       | Descripción                                                  | Ejemplo                              |
|----------------|--------------------------------------------------------------|--------------------------------------|
| `ADMIN_API_KEY` | Clave secreta para los endpoints `/admin/*`. Debe ser larga y aleatoria. | `s3cur3-r4nd0m-k3y-h3r3` |
| `API_URL`       | URL interna que usa el dashboard para conectarse a la API.   | `http://api:8000`                    |
| `DATABASE_URL`  | Cadena de conexión SQLAlchemy para la base de datos.         | `sqlite:////app/data/clima.db`       |

---

## Instrumento de encuesta

### Bloque MBI simplificado (9 ítems, escala 0–6)

Basado en el Maslach Burnout Inventory. Evalúa tres dimensiones:

| Dimensión             | Items | Interpretación                                          |
|-----------------------|-------|---------------------------------------------------------|
| Agotamiento emocional | q1–q5 | Puntuaciones altas indican mayor riesgo de burnout      |
| Despersonalización    | q6–q7 | Puntuaciones altas indican distanciamiento afectivo     |
| Logro personal        | q8–q9 | Puntuaciones bajas indican menor sensación de eficacia  |

### Bloque Clima organizacional (6 ítems, escala 1–5)

| Dimensión      | Item | Descripción                                     |
|----------------|------|-------------------------------------------------|
| Comunicación   | q10  | Flujo de información en el equipo               |
| Reconocimiento | q11  | Valoración del trabajo por parte de superiores  |
| Carga laboral  | q12  | Percepción de manejabilidad de la carga         |
| Relaciones     | q13  | Calidad de las relaciones con compañeros        |
| Autonomía      | q14  | Libertad para tomar decisiones en el rol        |
| Liderazgo      | q15  | Apoyo del líder directo                         |

---

## Estructura del proyecto

```
clima-org-mvp/
├── api/                        # Backend FastAPI
│   ├── main.py                 # Punto de entrada, registro de routers
│   ├── config.py               # Configuración desde variables de entorno
│   ├── database.py             # Engine SQLAlchemy y sesiones
│   ├── constants.py            # Definición de las 15 preguntas del instrumento
│   ├── models/
│   │   └── models.py           # Modelos ORM (Survey, Token, Response)
│   ├── schemas/
│   │   └── schemas.py          # Esquemas Pydantic (request/response)
│   ├── routers/
│   │   ├── admin.py            # Endpoints admin: crear campañas, tokens, resultados
│   │   ├── surveys.py          # Endpoint público: formulario de encuesta (HTML)
│   │   ├── responses.py        # Endpoint público: envío de respuestas
│   │   └── scores.py           # Endpoint de puntuaciones y agregados
│   ├── services/
│   │   ├── scoring.py          # Lógica de cálculo MBI y clima
│   │   ├── tokens.py           # Generación y validación de tokens
│   │   └── alerts.py           # Detección de umbrales y alertas de burnout
│   ├── templates/
│   │   └── survey_form.html    # Formulario HTML de encuesta (Jinja2)
│   ├── tests/
│   │   ├── conftest.py         # Fixtures pytest (DB en memoria)
│   │   └── test_scoring.py     # Tests unitarios del motor de puntuación
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/                  # Frontend analítico Streamlit
│   ├── app.py                  # Página principal y navegación
│   ├── pages/
│   │   ├── 1_overview.py       # Resumen general por campaña
│   │   ├── 2_heatmap.py        # Heatmap de puntuaciones por departamento
│   │   ├── 3_tendencias.py     # Evolución temporal de métricas
│   │   ├── 4_alertas.py        # Lista de alertas activas de burnout
│   │   └── 5_exportar.py       # Exportación de datos a CSV
│   ├── requirements.txt
│   └── Dockerfile
├── data/                       # Volumen persistente (generado en runtime)
│   └── clima.db                # Base de datos SQLite
├── docker-compose.yml          # Orquestación de servicios
├── .env.example                # Plantilla de variables de entorno
└── .dockerignore
```

---

## Escalabilidad

Este MVP usa SQLite y Streamlit para minimizar la complejidad operativa en la fase inicial. Cuando el volumen de respuestas o el número de usuarios concurrentes lo justifique, las migraciones naturales son:

- **SQLite → PostgreSQL**: cambiar `DATABASE_URL` en `.env` y ajustar el driver SQLAlchemy (`psycopg2`). El resto del código ORM no requiere cambios.
- **Streamlit → React**: reemplazar el servicio `dashboard` por una SPA consumiendo la misma API REST, que ya expone todos los endpoints necesarios en `/docs`.

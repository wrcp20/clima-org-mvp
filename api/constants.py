SURVEY_QUESTIONS = [
    {"id": "q1",  "block": "mbi",     "dimension": "exhaustion",       "scale_min": 0, "scale_max": 6, "text": "Me siento emocionalmente agotado/a por mi trabajo"},
    {"id": "q2",  "block": "mbi",     "dimension": "exhaustion",       "scale_min": 0, "scale_max": 6, "text": "Me siento 'quemado/a' al final de la jornada"},
    {"id": "q3",  "block": "mbi",     "dimension": "exhaustion",       "scale_min": 0, "scale_max": 6, "text": "Trabajar todo el día es realmente una tensión para mí"},
    {"id": "q4",  "block": "mbi",     "dimension": "exhaustion",       "scale_min": 0, "scale_max": 6, "text": "Me siento frustrado/a por mi trabajo"},
    {"id": "q5",  "block": "mbi",     "dimension": "exhaustion",       "scale_min": 0, "scale_max": 6, "text": "Me siento como si estuviera al límite de mis posibilidades"},
    {"id": "q6",  "block": "mbi",     "dimension": "depersonalization", "scale_min": 0, "scale_max": 6, "text": "Siento que trato a algunos compañeros como objetos"},
    {"id": "q7",  "block": "mbi",     "dimension": "depersonalization", "scale_min": 0, "scale_max": 6, "text": "Me he vuelto más insensible con la gente desde que ejerzo este trabajo"},
    {"id": "q8",  "block": "mbi",     "dimension": "achievement",      "scale_min": 0, "scale_max": 6, "text": "Siento que estoy influyendo positivamente en el trabajo"},
    {"id": "q9",  "block": "mbi",     "dimension": "achievement",      "scale_min": 0, "scale_max": 6, "text": "Me siento con mucha energía en mi trabajo"},
    {"id": "q10", "block": "climate", "dimension": "communication",    "scale_min": 1, "scale_max": 5, "text": "La información fluye claramente en mi equipo"},
    {"id": "q11", "block": "climate", "dimension": "recognition",      "scale_min": 1, "scale_max": 5, "text": "Mi trabajo es valorado por mis superiores"},
    {"id": "q12", "block": "climate", "dimension": "workload",         "scale_min": 1, "scale_max": 5, "text": "Mi carga de trabajo es manejable"},
    {"id": "q13", "block": "climate", "dimension": "relationships",    "scale_min": 1, "scale_max": 5, "text": "Las relaciones con mis compañeros son positivas"},
    {"id": "q14", "block": "climate", "dimension": "autonomy",         "scale_min": 1, "scale_max": 5, "text": "Tengo libertad para tomar decisiones en mi rol"},
    {"id": "q15", "block": "climate", "dimension": "leadership",       "scale_min": 1, "scale_max": 5, "text": "Mi líder me apoya cuando lo necesito"},
]

MBI_QUESTIONS = [q for q in SURVEY_QUESTIONS if q["block"] == "mbi"]
CLIMATE_QUESTIONS = [q for q in SURVEY_QUESTIONS if q["block"] == "climate"]

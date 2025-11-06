from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, scraping
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = FastAPI(
    title="Flash Elicit API",
    description="API para la herramienta Flash Elicit",
    version="1.0.0"
)

# Configuración de CORS
origins = [
    "http://localhost:4200",  # Angular development server
    "http://127.0.0.1:4200",  # Alternativa localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de orígenes permitidos
    allow_credentials=True,  # Permitir cookies y credenciales
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["scraping"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

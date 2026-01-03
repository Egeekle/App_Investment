# Guía de Inicio Rápido

## Instalación Rápida (5 minutos)

### 1. Clonar y configurar

```bash
# Clonar repositorio
git clone <repository-url>
cd App_Investment

# Crear archivo .env
cp .env.example .env
# Editar .env con tus credenciales
```

### 2. Instalar dependencias

```bash
# Opción A: Con pip
pip install -r requirements.txt

# Opción B: Con Make
make install
```

### 3. Inicializar base de conocimiento

```bash
python scripts/initialize_knowledge_base.py
```

### 4. Ejecutar aplicación

#### Opción A: Docker Compose (Recomendado)

```bash
docker-compose up
```

Accede a:
- API: http://localhost:8000
- Streamlit: http://localhost:8501
- API Docs: http://localhost:8000/docs

#### Opción B: Local

Terminal 1 - API:
```bash
make run-api
# o
uvicorn src.api.main:app --reload
```

Terminal 2 - Streamlit:
```bash
make run-streamlit
# o
streamlit run src/app/main.py
```

## Probar la Aplicación

### 1. Vía Streamlit (Interfaz Web)

1. Abre http://localhost:8501
2. Selecciona un activo (ej: BTC, SPY)
3. Haz clic en "Analizar"
4. Revisa el análisis generado

### 2. Vía API (cURL)

```bash
# Health check
curl http://localhost:8000/health

# Análisis completo
curl -X POST http://localhost:8000/v1/chat/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC",
    "query": "¿Cuál es el análisis técnico y recomendación?"
  }'

# Datos de mercado
curl http://localhost:8000/v1/market/price/BTC?days=30
```

### 3. Vía Python

```python
import requests

# Análisis
response = requests.post(
    "http://localhost:8000/v1/chat/analyze",
    json={
        "symbol": "SPY",
        "query": "¿Debería comprar o vender?"
    }
)
print(response.json())
```

## Entrenar Modelo (Opcional)

```bash
# Entrenar modelo Random Forest
make train
# o
python scripts/train_model.py
```

## Comandos Útiles

```bash
make help          # Ver todos los comandos
make setup         # Setup completo
make init-kb       # Inicializar base de conocimiento
make train         # Entrenar modelo
make test          # Ejecutar tests
make lint          # Verificar código
make format        # Formatear código
make docker-up     # Iniciar con Docker
make docker-down   # Detener Docker
```

## Solución de Problemas

### Error: "Google AI API Key not found"
- Verifica que `.env` existe y tiene `GOOGLE_AI_API_KEY`
- Obtén tu API key en: https://aistudio.google.com/apikey

### Error: "Model not found"
- Entrena el modelo: `make train`
- O crea un modelo dummy (el sistema funcionará sin él)

### Error: "ChromaDB error"
- Ejecuta: `python scripts/initialize_knowledge_base.py`
- Verifica permisos en `./data/chroma_db`

### Puerto ya en uso
- Cambia puertos en `docker-compose.yml` o usa:
  ```bash
  uvicorn src.api.main:app --port 8001
  ```

## Siguiente Paso

Lee `DEPLOYMENT.md` para desplegar en producción.


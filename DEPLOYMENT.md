# Guía de Despliegue

Esta guía explica cómo desplegar el Asistente de Inversión Inteligente.

## Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- Google AI Studio API Key (obtener en https://aistudio.google.com/apikey)
- Alpha Vantage API Key (opcional, para ETFs)
- Git

## Configuración Local

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd App_Investment
```

### 2. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y completa las variables:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
GOOGLE_AI_API_KEY=tu_clave_aqui
GOOGLE_AI_MODEL=gemini-pro
ALPHA_VANTAGE_API_KEY=tu_clave_aqui
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Inicializar base de conocimiento

```bash
python scripts/initialize_knowledge_base.py
```

### 5. Entrenar modelo (opcional)

```bash
python scripts/train_model.py
```

## Despliegue con Docker

### Opción 1: Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Esto iniciará:
- API FastAPI en `http://localhost:8000`
- Streamlit en `http://localhost:8501`

### Opción 2: Docker individual

#### Construir imagen

```bash
docker build -t investment-assistant .
```

#### Ejecutar API

```bash
docker run -d \
  --name investment-api \
  -p 8000:8000 \
  --env-file .env \
  investment-assistant \
  python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

#### Ejecutar Streamlit

```bash
docker run -d \
  --name investment-streamlit \
  -p 8501:8501 \
  -e API_BASE_URL=http://localhost:8000 \
  investment-assistant \
  streamlit run src/app/main.py --server.port 8501 --server.address 0.0.0.0
```

## Despliegue en Azure

### Azure Container Apps

1. **Crear Azure Container Registry**

```bash
az acr create --resource-group <resource-group> --name <acr-name> --sku Basic
```

2. **Autenticar Docker**

```bash
az acr login --name <acr-name>
```

3. **Construir y subir imagen**

```bash
docker build -t <acr-name>.azurecr.io/investment-assistant:latest .
docker push <acr-name>.azurecr.io/investment-assistant:latest
```

4. **Crear Container App Environment**

```bash
az containerapp env create \
  --name <env-name> \
  --resource-group <resource-group> \
  --location <location>
```

5. **Desplegar Container App**

```bash
az containerapp create \
  --name investment-assistant-api \
  --resource-group <resource-group> \
  --environment <env-name> \
  --image <acr-name>.azurecr.io/investment-assistant:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    GOOGLE_AI_API_KEY=<key> \
    GOOGLE_AI_MODEL=gemini-pro \
    ALPHA_VANTAGE_API_KEY=<key>
```

### Azure Kubernetes Service (AKS)

1. **Crear cluster AKS**

```bash
az aks create \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --node-count 2 \
  --enable-managed-identity
```

2. **Conectar al cluster**

```bash
az aks get-credentials --resource-group <resource-group> --name <cluster-name>
```

3. **Crear secretos de Kubernetes**

```bash
kubectl create secret generic app-secrets \
  --from-literal=google-ai-api-key=<key> \
  --from-literal=alpha-vantage-api-key=<key>
```

4. **Aplicar manifiestos Kubernetes**

```bash
kubectl apply -f k8s/
```

## Verificación

### Health Check

```bash
curl http://localhost:8000/health
```

### Probar análisis

```bash
curl -X POST http://localhost:8000/v1/chat/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "query": "¿Cuál es el análisis técnico?"}'
```

## Monitoreo

### MLflow

Accede a MLflow UI:

```bash
mlflow ui --backend-store-uri ./mlruns
```

Abre `http://localhost:5000` en el navegador.

### Logs

Ver logs de Docker:

```bash
docker-compose logs -f api
docker-compose logs -f streamlit
```

## Troubleshooting

### Error: "Agent not initialized"

- Verifica que las variables de entorno estén configuradas
- Revisa los logs para errores de conexión a Google AI
- Verifica que GOOGLE_AI_API_KEY esté correctamente configurada

### Error: "Model not found"

- Entrena el modelo ejecutando `python scripts/train_model.py`
- O crea un modelo dummy en `./models/random_forest_model.pkl`

### Error: ChromaDB

- Verifica permisos de escritura en `./data/chroma_db`
- Inicializa la base de conocimiento: `python scripts/initialize_knowledge_base.py`

## Producción

Para producción, considera:

1. **Seguridad**:
   - Usar Google Secret Manager o Azure Key Vault para secretos
   - Configurar CORS apropiadamente
   - Habilitar HTTPS/TLS

2. **Escalabilidad**:
   - Configurar auto-scaling en Container Apps/AKS
   - Usar Redis para caché
   - Considerar base de datos vectorial externa (Pinecone, Weaviate)

3. **Monitoreo**:
   - Integrar Application Insights o Google Cloud Monitoring
   - Configurar alertas
   - Monitorear costos de Google AI Studio

4. **CI/CD**:
   - Configurar GitHub Actions con tus credenciales
   - Automatizar despliegues en staging/producción


# Asistente de Inversión Inteligente

Sistema de análisis financiero que combina **IA Generativa (GPT-4)** con análisis técnico y sentimiento de mercado para proporcionar recomendaciones de inversión fundamentadas.

## 🚀 Características

- **Análisis Técnico Automatizado**: RSI, medias móviles, volatilidad
- **IA Generativa**: GPT-4 para análisis semántico y razonamiento
- **RAG (Retrieval-Augmented Generation)**: Base de conocimiento financiera con ChromaDB
- **Modelos ML**: Random Forest para estrategias TOP/BOTTOM
- **Arquitectura de Agentes**: LangGraph con supervisor inteligente
- **MLOps Completo**: MLflow para tracking, DVC para versionado
- **API RESTful**: FastAPI con documentación automática
- **Interfaz Web**: Streamlit para visualización interactiva
- **Containerización**: Docker y Docker Compose
- **CI/CD**: GitHub Actions para integración y despliegue continuo

## 📋 Requisitos Previos

- Python 3.10+
- Docker y Docker Compose (opcional)
- Google AI Studio API Key
- Alpha Vantage API Key (opcional, para ETFs)

## ⚡ Inicio Rápido

### 1. Configurar variables de entorno

```bash
cp env.example .env
# Editar .env con tu GOOGLE_AI_API_KEY
# Obtén tu API key en: https://aistudio.google.com/apikey
```

### 2. Instalar y ejecutar

```bash
# Opción A: Docker Compose (Recomendado)
docker-compose up

# Opción B: Local
make setup        # Instalar + inicializar
make run-api      # Terminal 1
make run-streamlit # Terminal 2
```

### 3. Acceder a la aplicación

- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

📖 Ver [QUICKSTART.md](QUICKSTART.md) para guía detallada.

## 🏗️ Arquitectura

```
┌─────────────┐
│  Streamlit  │  Frontend Interactivo
└──────┬──────┘
       │
┌──────▼──────┐
│   FastAPI   │  API REST
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   LangGraph Agent       │  Orquestación
│   ┌──────────────────┐  │
│   │  Supervisor LLM  │  │
│   └────────┬─────────┘  │
│            │            │
│   ┌────────▼─────────┐ │
│   │  Tools:          │ │
│   │  - Market Data   │ │
│   │  - RAG Search    │ │
│   │  - ML Predict    │ │
│   └──────────────────┘ │
└──────┬─────────────────┘
       │
┌──────▼──────┬──────────────┬─────────────┐
│ CoinGecko  │ Alpha Vantage│  ChromaDB   │
│   API      │     API      │  (RAG)      │
└────────────┴──────────────┴─────────────┘
```

## 📁 Estructura del Proyecto

```
App_Investment/
├── src/
│   ├── data_ingestion/    # APIs de mercado (CoinGecko, Alpha Vantage)
│   ├── models/            # Agente LangGraph + Random Forest
│   ├── rag/               # Sistema RAG con ChromaDB
│   ├── api/               # FastAPI backend
│   └── app/               # Streamlit frontend
├── scripts/               # Scripts de utilidad
├── tests/                 # Tests unitarios
├── config/                # Configuración YAML
└── docker-compose.yml     # Orquestación de servicios
```

Ver [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) para detalles completos.

## 🔌 Endpoints API

### Análisis Completo
```bash
POST /v1/chat/analyze
{
  "symbol": "BTC",
  "query": "¿Cuál es el análisis técnico?"
}
```

### Datos de Mercado
```bash
GET /v1/market/price/{symbol}?days=30
```

### Health Check
```bash
GET /health
```

## 🛠️ Comandos Útiles

```bash
make help          # Ver todos los comandos
make setup         # Setup completo
make train         # Entrenar modelo ML
make init-kb       # Inicializar base de conocimiento
make test          # Ejecutar tests
make docker-up     # Iniciar con Docker
```

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) - Guía de inicio rápido
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía de despliegue en producción
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Estructura detallada del proyecto

## 🧪 Testing

```bash
# Ejecutar tests
make test

# Con cobertura
pytest tests/ -v --cov=src
```

## 🚢 Despliegue

### Local
```bash
docker-compose up -d
```

### Azure Container Apps
Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones completas.

## 📊 MLOps

- **MLflow**: Tracking de experimentos y versionado de modelos
- **DVC**: Versionado de datos
- Monitoreo de drift y métricas en tiempo real

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es parte de un Trabajo de Fin de Programa académico.

## 🙏 Agradecimientos

- Google AI Studio (Gemini) por análisis con IA
- LangChain/LangGraph por el framework de agentes
- CoinGecko y Alpha Vantage por APIs de datos financieros


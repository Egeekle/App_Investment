# Estructura del Proyecto

## Descripción General

Este proyecto implementa un **Asistente de Inversión Inteligente** que combina:
- **IA Generativa** (Gemini de Google AI Studio) para análisis semántico
- **Análisis Técnico** con indicadores financieros (RSI, SMAs, volatilidad)
- **MLOps** con MLflow y DVC para versionado y tracking
- **RAG** (Retrieval-Augmented Generation) con ChromaDB
- **Arquitectura de Agentes** con LangGraph

## Estructura de Directorios

```
App_Investment/
├── src/                          # Código fuente principal
│   ├── data_ingestion/          # Módulos de ingesta de datos
│   │   ├── coingecko_client.py  # Cliente API CoinGecko (criptos)
│   │   ├── alpha_vantage_client.py # Cliente API Alpha Vantage (ETFs)
│   │   └── technical_indicators.py # Cálculo de indicadores técnicos
│   │
│   ├── models/                  # Modelos ML y agentes
│   │   ├── random_forest_model.py # Modelo RF para estrategias TOP/BOTTOM
│   │   ├── investment_agent.py  # Agente LangGraph principal
│   │   ├── agent_state.py       # Definición de estado del agente
│   │   └── agent_tools.py       # Herramientas del agente
│   │
│   ├── rag/                     # Sistema RAG
│   │   ├── vector_store.py      # Implementación ChromaDB
│   │   └── knowledge_base.py    # Inicialización de base de conocimiento
│   │
│   ├── api/                     # Backend FastAPI
│   │   └── main.py              # Aplicación FastAPI con endpoints
│   │
│   └── app/                     # Frontend Streamlit
│       └── main.py              # Interfaz de usuario Streamlit
│
├── scripts/                     # Scripts de utilidad
│   ├── train_model.py           # Entrenar modelo ML
│   └── initialize_knowledge_base.py # Inicializar base de conocimiento
│
├── tests/                       # Tests unitarios
│   └── test_technical_indicators.py
│
├── config/                      # Configuración
│   └── config.yaml              # Configuración YAML
│
├── data/                        # Datos (versionados con DVC)
│   └── chroma_db/               # Base de datos vectorial
│
├── models/                      # Modelos entrenados
│   └── random_forest_model.pkl
│
├── mlruns/                      # MLflow tracking
│
├── docker/                      # Configuración Docker
│
├── .github/workflows/            # CI/CD pipelines
│   ├── ci.yml                   # Pipeline de integración continua
│   └── cd.yml                   # Pipeline de despliegue continuo
│
├── Dockerfile                   # Imagen Docker
├── docker-compose.yml           # Orquestación de servicios
├── requirements.txt             # Dependencias Python
├── Makefile                     # Comandos útiles
├── README.md                    # Documentación principal
├── DEPLOYMENT.md                # Guía de despliegue
└── setup.py                     # Configuración del paquete
```

## Flujo de Datos

1. **Ingesta de Datos**:
   - CoinGecko API → Datos de criptomonedas
   - Alpha Vantage API → Datos de ETFs/acciones
   - Cálculo de indicadores técnicos (RSI, SMAs, volatilidad)

2. **Procesamiento**:
   - Enriquecimiento con indicadores técnicos
   - Almacenamiento en base vectorial (noticias/sentimiento)
   - Predicción con modelo Random Forest

3. **Análisis con IA**:
   - Agente LangGraph orquesta herramientas
   - RAG recupera contexto relevante
   - GPT-4 sintetiza análisis completo

4. **Presentación**:
   - API FastAPI expone endpoints REST
   - Streamlit muestra interfaz interactiva

## Componentes Principales

### 1. Data Ingestion (`src/data_ingestion/`)

- **CoinGeckoClient**: Obtiene precios históricos de criptomonedas
- **AlphaVantageClient**: Obtiene datos de ETFs y acciones
- **Technical Indicators**: Calcula RSI, SMAs, volatilidad, posición de precio

### 2. RAG System (`src/rag/`)

- **VectorStore**: Implementación con ChromaDB y embeddings OpenAI
- **Knowledge Base**: Base de conocimiento financiero estructurada
- Búsqueda semántica de noticias y estrategias

### 3. ML Models (`src/models/`)

- **RandomForestStrategyModel**: Clasifica estrategias TOP/BOTTOM
- **InvestmentAgent**: Agente LangGraph con supervisor
- **AgentTools**: Herramientas para obtener datos y hacer predicciones

### 4. API (`src/api/`)

- **FastAPI**: Endpoints REST
  - `POST /v1/chat/analyze`: Análisis completo
  - `GET /v1/market/price/{symbol}`: Datos técnicos
  - `GET /health`: Health check

### 5. Frontend (`src/app/`)

- **Streamlit**: Interfaz web interactiva
- Selección de activos
- Visualización de gráficos
- Análisis con IA

## MLOps

### MLflow
- Tracking de experimentos
- Versionado de modelos
- Métricas y parámetros

### DVC
- Versionado de datos
- Pipeline de datos reproducible

## Despliegue

### Local
```bash
make docker-up  # Docker Compose
```

### Cloud
- Azure Container Apps (recomendado para MVP)
- Azure Kubernetes Service (AKS) para producción
- Configuración en `DEPLOYMENT.md`

## Próximos Pasos

1. Agregar más fuentes de datos (noticias en tiempo real)
2. Implementar monitoreo de drift
3. Mejorar estrategias de trading
4. Agregar backtesting
5. Dashboard de métricas en tiempo real


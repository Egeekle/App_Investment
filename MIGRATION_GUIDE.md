# Guía de Migración: Azure OpenAI → Google AI Studio

Este documento describe los cambios realizados para migrar de Azure OpenAI a Google AI Studio.

## Cambios Principales

### 1. Dependencias

**Antes:**
```txt
langchain-openai==0.0.2
```

**Ahora:**
```txt
langchain-google-genai==1.0.0
```

### 2. Variables de Entorno

**Antes (.env):**
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Ahora (.env):**
```env
GOOGLE_AI_API_KEY=your_key
GOOGLE_AI_MODEL=gemini-pro
```

### 3. Código - LLM

**Antes:**
```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    temperature=0.7
)
```

**Ahora:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GOOGLE_AI_MODEL", "gemini-pro"),
    google_api_key=os.getenv("GOOGLE_AI_API_KEY"),
    temperature=0.7,
    convert_system_message_to_human=True
)
```

### 4. Código - Embeddings

**Antes:**
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    deployment="text-embedding-3-small"
)
```

**Ahora:**
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_AI_API_KEY")
)
```

### 5. Modelos Disponibles

**Google AI Studio:**
- `gemini-pro` - Modelo principal (recomendado)
- `gemini-pro-vision` - Para análisis con imágenes
- `models/embedding-001` - Para embeddings

## Obtener API Key

1. Visita: https://aistudio.google.com/apikey
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API key
4. Copia la key y agrégala a tu archivo `.env`

## Ventajas de Google AI Studio

1. **Gratis para desarrollo**: Generoso tier gratuito
2. **Fácil de usar**: No requiere configuración de endpoints
3. **Modelos potentes**: Gemini Pro es comparable a GPT-4
4. **Integración simple**: API key única

## Notas Importantes

- El modelo `gemini-pro` tiene un contexto de hasta 32k tokens
- Los embeddings de Google tienen 768 dimensiones (vs 1536 de OpenAI)
- Algunas funciones avanzadas pueden requerir ajustes menores
- El parámetro `convert_system_message_to_human=True` es necesario para compatibilidad

## Verificación

Después de migrar, verifica que todo funcione:

```bash
python scripts/verify_setup.py
```

Si hay errores, revisa:
1. Que `GOOGLE_AI_API_KEY` esté configurada en `.env`
2. Que hayas instalado las nuevas dependencias: `pip install -r requirements.txt`
3. Que la API key sea válida


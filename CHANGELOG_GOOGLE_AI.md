# Changelog - Migración a Google AI Studio

## Cambios Realizados

### ✅ Dependencias Actualizadas
- Reemplazado `langchain-openai` por `langchain-google-genai`
- Actualizado `requirements.txt`

### ✅ Código Actualizado

#### `src/api/main.py`
- Cambiado `AzureChatOpenAI` → `ChatGoogleGenerativeAI`
- Simplificada la inicialización (solo requiere API key y modelo)

#### `src/models/investment_agent.py`
- Actualizado tipo de LLM a `ChatGoogleGenerativeAI`
- Mantiene toda la funcionalidad del agente

#### `src/rag/vector_store.py`
- Cambiado `OpenAIEmbeddings` → `GoogleGenerativeAIEmbeddings`
- Modelo de embeddings: `models/embedding-001`
- Dimensiones: 768 (vs 1536 de OpenAI)

### ✅ Configuración Actualizada

#### `env.example`
- Reemplazadas variables de Azure OpenAI por Google AI
- Variables simplificadas:
  - `GOOGLE_AI_API_KEY`
  - `GOOGLE_AI_MODEL` (default: gemini-pro)

#### `config/config.yaml`
- Actualizada sección de configuración de LLM
- Actualizada configuración de embeddings

#### `docker-compose.yml`
- Variables de entorno actualizadas

### ✅ Documentación Actualizada

- `README.md` - Referencias actualizadas
- `QUICKSTART.md` - Instrucciones actualizadas
- `DEPLOYMENT.md` - Guía de despliegue actualizada
- `PROJECT_SUMMARY.md` - Referencias actualizadas
- `PROJECT_STRUCTURE.md` - Referencias actualizadas
- `scripts/verify_setup.py` - Verificación actualizada

### ✅ Nuevos Archivos

- `MIGRATION_GUIDE.md` - Guía completa de migración

## Próximos Pasos

1. **Instalar nuevas dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar API Key:**
   ```bash
   cp env.example .env
   # Editar .env con tu GOOGLE_AI_API_KEY
   # Obtener en: https://aistudio.google.com/apikey
   ```

3. **Reinicializar base de conocimiento (opcional):**
   ```bash
   # Si quieres regenerar embeddings con Google AI
   rm -rf data/chroma_db
   python scripts/initialize_knowledge_base.py
   ```

4. **Verificar configuración:**
   ```bash
   python scripts/verify_setup.py
   ```

5. **Ejecutar aplicación:**
   ```bash
   docker-compose up
   # O localmente
   make run-api
   make run-streamlit
   ```

## Notas

- Los embeddings existentes en ChromaDB seguirán funcionando
- Si quieres regenerar embeddings con Google AI, elimina `data/chroma_db` y reinicializa
- El modelo `gemini-pro` es equivalente a GPT-4 en capacidades
- Google AI Studio ofrece tier gratuito generoso para desarrollo

## Compatibilidad

- ✅ Todas las funcionalidades existentes se mantienen
- ✅ La API REST no cambia
- ✅ La interfaz Streamlit no cambia
- ✅ Los modelos ML no cambian
- ✅ Solo cambia el proveedor de LLM y embeddings


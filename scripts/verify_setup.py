"""Script to verify project setup"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_env_var(var_name: str) -> bool:
    """Check if environment variable is set"""
    from dotenv import load_dotenv
    load_dotenv()
    value = os.getenv(var_name)
    is_set = value is not None and value != ""
    status = "✓" if is_set else "✗"
    print(f"{status} {var_name}: {'Set' if is_set else 'Not set'}")
    return is_set

def check_import(module_name: str) -> bool:
    """Check if a Python module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name}: Importable")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("Verificando configuración del proyecto...")
    print("=" * 60)
    
    all_ok = True
    
    # Check project structure
    print("\n📁 Estructura del proyecto:")
    all_ok &= check_file_exists("requirements.txt", "requirements.txt")
    all_ok &= check_file_exists(".env", "Archivo .env")
    all_ok &= check_file_exists("docker-compose.yml", "docker-compose.yml")
    all_ok &= check_file_exists("src/api/main.py", "API FastAPI")
    all_ok &= check_file_exists("src/app/main.py", "App Streamlit")
    all_ok &= check_file_exists("src/models/investment_agent.py", "Agente LangGraph")
    all_ok &= check_file_exists("src/rag/vector_store.py", "Vector Store")
    
    # Check environment variables
    print("\n🔐 Variables de entorno:")
    all_ok &= check_env_var("GOOGLE_AI_API_KEY")
    all_ok &= check_env_var("ALPHA_VANTAGE_API_KEY")
    
    # Check Python dependencies
    print("\n📦 Dependencias Python:")
    critical_modules = [
        "fastapi",
        "streamlit",
        "langchain",
        "langgraph",
        "chromadb",
        "mlflow",
        "pandas",
        "numpy",
        "sklearn"
    ]
    
    for module in critical_modules:
        all_ok &= check_import(module)
    
    # Check data directories
    print("\n💾 Directorios de datos:")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ data/: {data_dir.exists()}")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    print(f"✓ models/: {models_dir.exists()}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Configuración completa! El proyecto está listo para usar.")
        print("\nPróximos pasos:")
        print("  1. python scripts/initialize_knowledge_base.py")
        print("  2. python scripts/train_model.py  (opcional)")
        print("  3. docker-compose up  (o make docker-up)")
    else:
        print("⚠️  Hay algunos problemas. Revisa los errores arriba.")
        print("\nSugerencias:")
        print("  - Ejecuta: pip install -r requirements.txt")
        print("  - Crea .env desde .env.example")
        print("  - Verifica tus credenciales de API")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())


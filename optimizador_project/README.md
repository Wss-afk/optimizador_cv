# 🚀 Optimizador Inteligente de Currículums

Sistema multi-agente que analiza ofertas de empleo, optimiza currículums y evalúa compatibilidad con sistemas ATS usando inteligencia artificial.

## 🎯 Características

- **Análisis de Ofertas**: Extrae requisitos, skills, keywords y responsabilidades
- **Optimización de CV**: Adapta tu currículum para la oferta específica
- **Evaluación ATS**: Verifica compatibilidad con sistemas automáticos de selección
- **Base de Conocimiento**: RAG con mejores prácticas de reclutadores
- **Multi-agente**: Flujo coordinado con LangGraph
- **IA Local**: Usa Ollama + Qwen3.8b (no requiere API)

## 🏗️ Arquitectura

```
Usuario
   │
   ▼
CV (PDF/TXT) + Oferta (PDF/TXT)
   │
   ▼
[Job Analyzer]     → Extrae requisitos y keywords
   │
   ▼
[CV Optimizer]     → Analiza y adapta CV (+ RAG context)
   │
   ▼
[ATS Reviewer]     → Evalúa compatibilidad + revisión final
   │
   ▼
Resultado: CV Optimizado + Puntuaciones ATS + Recomendaciones
```

## 🛠️ Stack Técnico

- **LLM**: Ollama + Qwen3.8b
- **Embeddings**: Nomic-embed-text
- **Vector DB**: ChromaDB
- **Orquestación**: LangGraph
- **Framework**: LangChain
- **Lenguaje**: Python 3.9+

## 📦 Requisitos Previos

### 1. Ollama Instalado

Descarga desde: https://ollama.ai

**Modelos necesarios**:
```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

**Verificar que Ollama está corriendo**:
```bash
ollama serve
```

### 2. Python 3.9+

Verifica tu versión:
```bash
python --version
```

## 🚀 Instalación

### Opción 1: Instalación Estándar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/optimizador-cv.git
cd optimizador-cv/optimizador_project

# Crear entorno virtual
python -m venv venv

# Activar entorno
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -e .
```

### Opción 2: Instalación con Dependencias de Desarrollo

```bash
pip install -e ".[dev]"
```

### Opción 3: Instalación Manual de Dependencias

```bash
pip install -r dev-requirements.txt
pip install -r <(cat pyproject.toml | grep -A 20 'dependencies')
```

## 🎮 Uso

### Ejecución Interactiva (CLI)

```bash
python -m optimizador
```

El sistema te pedirá:
1. Ruta al CV (PDF o TXT)
2. Ruta a la oferta o pega el texto directamente
3. Procesará y mostrará resultados

### Ejemplo de Uso Programático

```python
from optimizador.utils.pdf_loader import load_document
from optimizador.graph.workflow import create_workflow

# Cargar documentos
cv_text = load_document("mi_cv.pdf")
job_posting = load_document("oferta.txt")

# Crear y ejecutar workflow
workflow = create_workflow()
result = workflow.invoke(job_posting, cv_text)

# Acceder a resultados
print(f"Puntuación ATS: {result.ats_score.overall_score}")
print(f"Keywords encontradas: {result.found_keywords}")
print(f"CV Optimizado:\n{result.final_cv}")
```

## 📊 Salida Esperada

```
═══════════════════════════════════════════
  OPTIMIZADOR DE CURRÍCULUMS - RESULTADO
═══════════════════════════════════════════

📊 PUNTUACIÓN ATS: 82/100
  ├─ Keyword Match:    85%
  ├─ Formato:          90%
  └─ Completitud:      72%

✅ Keywords encontradas:
  Python, Docker, AWS, FastAPI, Git

❌ Keywords faltantes:
  Kubernetes, CI/CD

📝 Cambios realizados:
  1. Añadida sección de "Competencias técnicas"
  2. Reescrito resumen profesional
  3. Reordenadas experiencias por relevancia
  4. Añadidos verbos de acción

💡 Recomendaciones:
  - Considerar añadir experiencia con Kubernetes
  - Incluir certificaciones AWS
  - El formato es compatible con ATS
```

## 📁 Estructura del Proyecto

```
optimizador_project/
├── optimizador/
│   ├── __init__.py
│   ├── __main__.py              # CLI principal
│   ├── config.py                # Configuración global
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── job_analyzer.py      # Análisis de ofertas
│   │   ├── cv_optimizer.py      # Optimización de CV
│   │   └── ats_reviewer.py      # Evaluación ATS
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py          # Orquestación LangGraph
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic models
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   └── vector_store.py      # ChromaDB + Embeddings
│   │
│   └── utils/
│       ├── __init__.py
│       └── pdf_loader.py        # Carga de documentos
│
├── docs/                        # Base de conocimiento RAG
│   ├── ats_rules.txt
│   ├── resume_best_practices.txt
│   └── recruitment_tips.txt
│
├── data/                        # Datos de ejemplo
│   ├── sample_cv.txt
│   └── sample_job_posting.txt
│
├── tests/
│   └── test_optimizador.py
│
├── chroma_db/                   # Base de datos vectorial (auto-generada)
│
├── pyproject.toml
├── dev-requirements.txt
└── README.md
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests básicos
pytest

# Tests con cobertura
pytest --cov=optimizador

# Tests de integración (requiere Ollama)
pytest -m integration

# Tests específicos
pytest tests/test_optimizador.py::TestJobAnalyzer -v
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# RAG
RAG_REBUILD=false  # Reconstruir ChromaDB

# Logging
LOG_LEVEL=INFO
```

### Personalizar Prompts

Edita `config.py` para modificar los prompts de los agentes:

```python
PROMPTS = {
    "job_analyzer": "Tu prompt personalizado...",
    "cv_optimizer": "Tu prompt personalizado...",
    "ats_reviewer": "Tu prompt personalizado...",
}
```

## 🚨 Solución de Problemas

### "No se pudo conectar a Ollama"

```bash
# 1. Verificar que Ollama está corriendo
ollama serve

# 2. Descargar modelos
ollama pull qwen3:8b
ollama pull nomic-embed-text

# 3. Probar conexión
curl http://localhost:11434/api/tags
```

### "Modelo no descargado"

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

### "ChromaDB error"

```bash
# Reconstruir la base de conocimiento
python -c "from optimizador.rag.vector_store import get_knowledge_base; get_knowledge_base(force_rebuild=True)"
```

### "LLM devuelve JSON inválido"

- Aumentar `temperature` en `config.py` (menos restrictivo)
- Revisar el prompt y añadir ejemplos más claros
- Intentar con otro modelo: `ollama pull mistral` y cambiar en `config.py`

## 📈 Mejoras Futuras

- [ ] Soporte para más formatos (DOCX, PDF con imágenes OCR)
- [ ] Interfaz web Streamlit
- [ ] Análisis de salario basado en mercado
- [ ] Integración con LinkedIn
- [ ] Almacenamiento de histórico de optimizaciones
- [ ] Soporte para múltiples idiomas
- [ ] Dashboard de estadísticas

## 📚 Documentación Técnica

Ver archivos detallados en `docs/`:

- **ats_rules.txt**: Reglas de sistemas ATS
- **resume_best_practices.txt**: Mejores prácticas para CVs
- **recruitment_tips.txt**: Consejos de reclutadores

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💼 Autor

Matias - [GitHub](https://github.com/tu-usuario)

## 🙋 Support

Si encuentras problemas:

1. Revisa [Problemas Comunes](#-solución-de-problemas)
2. Abre un issue con detalles del error
3. Incluye logs y configuración relevante

---

**Última actualización**: Junio 2024
**Versión**: 1.0.0

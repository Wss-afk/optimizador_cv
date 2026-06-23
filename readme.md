# 🚀 Optimizador Inteligente de Currículums

Sistema multi-agente con IA que optimiza automáticamente tu CV para superar filtros ATS (Applicant Tracking Systems), usando matching inteligente de ofertas de empleo con embeddings y generación de contenido con LLM local.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)

## ✨ Características

- **Matching Automático de Ofertas**: Sube tu CV y el sistema encuentra automáticamente la oferta más compatible usando embeddings (ChromaDB + nomic-embed-text)
- **Optimización con IA**: Un agente LLM analiza la oferta, tu CV, y genera una versión optimizada con keywords ATS
- **Evaluación ATS**: Puntuación detallada de compatibilidad (keyword match, formato, completitud)
- **Base de Conocimiento RAG**: Mejores prácticas de CV integradas mediante Retrieval-Augmented Generation
- **Descarga en PDF**: Exporta tu CV optimizado directamente en formato PDF
- **Interfaz Web Moderna**: Dashboard oscuro y responsive con visualización de ofertas, resultados y métricas
- **100% Local**: Todo corre en tu máquina con Ollama — sin enviar datos a la nube

## 🏗️ Arquitectura

```
START → match_offer → review_cv → END
         (ChromaDB       (CV Reviewer Agent
          embeddings)      LLM + RAG)
```

### Componentes principales

| Módulo | Descripción |
|--------|-------------|
| `agents/cv_reviewer.py` | Agente unificado que analiza oferta, CV, optimiza, evalúa ATS y revisa |
| `rag/offer_store.py` | Indexación y matching de ofertas de empleo con ChromaDB |
| `rag/vector_store.py` | Base de conocimiento RAG (mejores prácticas de CV) |
| `graph/workflow.py` | Orquestador LangGraph StateGraph con 2 nodos |
| `models/schemas.py` | Modelos Pydantic para validación de datos |
| `api/main.py` | Backend FastAPI con endpoints REST |
| `static/index.html` | Frontend SPA con interfaz completa |

### Flujo de trabajo

1. **Startup**: Se cargan todas las ofertas de `ofertas/` en ChromaDB (collection: `job_offers`)
2. **Upload CV**: El usuario sube su CV (PDF o TXT)
3. **Match Offer**: Se calcula el embedding del CV y se busca la oferta más similar en ChromaDB
4. **CV Review**: El agente LLM (qwen3:8b) recibe la oferta matcheada + CV + contexto RAG, y devuelve:
   - Análisis de la oferta y del CV
   - CV optimizado y reescrito
   - Puntuación ATS detallada
   - Keywords encontradas y faltantes
   - Recomendaciones y mejoras aplicadas
5. **Resultado**: El usuario ve el CV optimizado y puede descargarlo en PDF

## 📋 Requisitos

- **Python** 3.9+
- **Ollama** corriendo localmente con los modelos:
  - `qwen3:8b` — LLM principal para análisis y optimización
  - `nomic-embed-text` — Modelo de embeddings
- **RAM**: Mínimo 8 GB (recomendado 16 GB para LLM)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/user/optimizador-cv.git
cd optimizador-cv/optimizador_project
```

### 2. Instalar dependencias

```bash
pip install -e .
```

Para desarrollo:

```bash
pip install -e ".[dev]"
```

### 3. Configurar Ollama

```bash
# Instalar Ollama desde https://ollama.com
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

## 🖥️ Uso

### Modo Web (recomendado)

```bash
cd optimizador_project
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Abre `http://localhost:8000` en tu navegador.

### Modo CLI

```bash
python -m optimizador
```

### Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Interfaz web |
| `GET` | `/api/health` | Estado del sistema (Ollama, embeddings) |
| `POST` | `/api/optimize` | Optimizar CV (recibe `cv_file`) |
| `GET` | `/api/offers` | Lista de ofertas indexadas con metadata |
| `GET` | `/api/offers/{filename}` | Detalle completo de una oferta |
| `POST` | `/api/download-pdf` | Generar PDF del CV optimizado |

## 📁 Estructura del proyecto

```
optimizador-cv/
├── optimizador_project/
│   ├── api/
│   │   └── main.py                 # Backend FastAPI
│   ├── optimizador/
│   │   ├── __main__.py             # CLI
│   │   ├── config.py               # Configuración global
│   │   ├── agents/
│   │   │   └── cv_reviewer.py      # Agente unificado
│   │   ├── graph/
│   │   │   └── workflow.py         # LangGraph workflow
│   │   ├── models/
│   │   │   └── schemas.py          # Modelos Pydantic
│   │   ├── rag/
│   │   │   ├── offer_store.py      # Store de ofertas (ChromaDB)
│   │   │   └── vector_store.py     # Base de conocimiento RAG
│   │   └── utils/
│   │       └── pdf_loader.py       # Cargador de documentos
│   ├── docs/                       # Documentos RAG (mejores prácticas)
│   │   ├── ats_rules.txt
│   │   ├── recruitment_tips.txt
│   │   └── resume_best_practices.txt
│   ├── ofertas/                    # Ofertas de empleo (20 archivos)
│   │   ├── 01_python_senior.txt
│   │   ├── 02_frontend_react.txt
│   │   ├── ...
│   │   └── 20_data_scientist.txt
│   ├── static/
│   │   └── index.html              # Frontend web
│   ├── tests/
│   │   └── test_optimizador.py     # Tests (16 tests)
│   └── pyproject.toml              # Dependencias y configuración
└── chroma_db/                      # Base de datos ChromaDB (generado)
```

## 🧪 Tests

```bash
cd optimizador_project
python -m pytest tests/ -v
```

> **Nota**: Los tests de integración requieren Ollama corriendo. Los tests unitarios (modelos, config, utils) funcionan sin dependencias externas.

## ⚙️ Configuración

Edita `optimizador/config.py` para personalizar:

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `LLM_CONFIG.model` | `qwen3:8b` | Modelo LLM principal |
| `RAG_CONFIG.top_k` | `3` | Documentos RAG a recuperar |
| `OFERTAS_RAG_CONFIG.top_k` | `1` | Número de ofertas a matchear |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL de Ollama (env var) |

## 📦 Tecnologías

- **[LangGraph](https://langchain-ai.github.io/langgraph/)** — Orquestación de workflow con StateGraph
- **[LangChain](https://python.langchain.com/)** — Framework de IA y RAG
- **[Ollama](https://ollama.com/)** — LLM local (qwen3:8b + nomic-embed-text)
- **[ChromaDB](https://www.trychroma.com/)** — Base de datos vectorial para embeddings
- **[FastAPI](https://fastapi.tiangolo.com/)** — Backend REST API
- **[fpdf2](https://pyfpdf.github.io/fpdf2/)** — Generación de PDFs
- **[Pydantic](https://docs.pydantic.dev/)** — Validación de datos

## 📄 Licencia

MIT

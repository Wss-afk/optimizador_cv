# Optimizador Inteligente de Currículums — Especificación Técnica Completa

## 1. Descripción del Proyecto

Sistema multi-agente que analiza una oferta de empleo, optimiza un currículum vitae para adaptarlo a dicha oferta, evalúa su compatibilidad con sistemas ATS y genera una versión final mejorada.

**Stack técnico**: Python + LangGraph + Ollama (qwen3:8b) + ChromaDB + nomic-embed-text

**Requisito mínimo**: 4 agentes coordinados mediante LangGraph StateGraph

---

## 2. Arquitectura General

```
Usuario
   │
   ▼
CV (PDF) + Oferta de Empleo (PDF/Texto)
   │
   ▼
┌─────────────────────────────────────────────┐
│           Supervisor Agent (LangGraph)       │
│           Orquesta el flujo completo         │
└─────────────────────────────────────────────┘
   │
   ├──▶ 1. Job Analyzer Agent
   │         Extrae requisitos y keywords de la oferta
   │
   ├──▶ 2. CV Optimizer Agent  (incluye análisis del CV)
   │         Analiza CV + Adapta contenido + Consulta RAG
   │
   ├──▶ 3. ATS Reviewer Agent  (incluye revisión final)
   │         Evalúa compatibilidad ATS + Pule resultado
   │
   └──▶ Output: CV Optimizado + Reporte ATS
```

---

## 3. Definición Detallada de Agentes

### 3.1 Supervisor Agent (Orquestador)

**Rol**: Coordinar el flujo entre agentes usando LangGraph StateGraph.

**Responsabilidades**:
- Recibir inputs del usuario (CV y oferta de empleo)
- Ejecutar agentes en orden
- Pasar estado entre agentes
- Manejar errores y reintentos
- Devolver resultado final

**Implementación**: `graph/workflow.py` usando `StateGraph`

```python
# Estado global del workflow
class WorkflowState(TypedDict):
    # Inputs
    job_posting_text: str          # Texto de la oferta de empleo
    cv_text: str                   # Texto del CV extraído del PDF

    # Agent 1 output
    job_analysis: dict             # Resultado del Job Analyzer

    # Agent 2 output
    cv_analysis: dict              # Análisis del CV
    optimized_cv: str              # CV optimizado

    # Agent 3 output
    ats_score: dict                # Puntuación ATS
    final_cv: str                  # CV final pulido
    report: str                    # Reporte completo

    # Control
    current_step: str              # Paso actual del workflow
    errors: list                   # Lista de errores
```

**Flujo del StateGraph**:
```
START → job_analyzer → cv_optimizer → ats_reviewer → END
```

---

### 3.2 Agente 1: Job Analyzer

**Archivo**: `agents/job_analyzer.py`

**Función**: Analizar la oferta de empleo y extraer información estructurada.

**Entrada**:
- `job_posting_text: str` — Texto completo de la oferta de empleo

**Salida** (Pydantic):
```python
class JobAnalysis(BaseModel):
    job_title: str                           # Título del puesto
    required_skills: list[str]               # Habilidades técnicas requeridas
    soft_skills: list[str]                   # Habilidades blandas
    years_experience: int                    # Años de experiencia mínimos
    seniority_level: str                     # Junior / Mid / Senior
    keywords_ats: list[str]                  # Palabras clave para ATS
    responsibilities: list[str]              # Responsabilidades del puesto
    technologies: list[str]                  # Tecnologías mencionadas
    salary_range: str | None                 # Rango salarial (si aparece)
```

**Prompt base**:
```
Eres un experto en análisis de ofertas de empleo.
Analiza la siguiente oferta y extrae la información en formato JSON estructurado.
Identifica: título del puesto, habilidades técnicas y blandas, años de experiencia,
nivel de seniority, palabras clave relevantes para ATS, responsabilidades principales
y tecnologías mencionadas.

Oferta de empleo:
{job_posting_text}
```

**Uso de LLM**: Ollama `qwen3:8b` con `temperature=0.1` (extracción precisa)

---

### 3.3 Agente 2: CV Optimizer

**Archivo**: `agents/cv_optimizer.py`

**Función**: Analizar el CV del candidato Y optimizarlo para la oferta de empleo.
(Este agente combina las funciones de CV Analyzer + CV Optimizer del diseño original)

**Entrada**:
- `cv_text: str` — Texto del CV extraído del PDF
- `job_analysis: JobAnalysis` — Resultado del Agente 1
- `rag_context: str` — Contexto relevante de la base de conocimiento RAG

**Salida** (Pydantic):
```python
class CVOptimizationResult(BaseModel):
    cv_analysis: CVAnalysis        # Análisis del CV original
    optimized_cv: str              # CV optimizado completo
    changes_made: list[str]        # Cambios realizados
    keywords_added: list[str]      # Keywords añadidas
    match_score: float             # Score de compatibilidad (0-100)
```

```python
class CVAnalysis(BaseModel):
    candidate_name: str
    current_skills: list[str]
    experience_years: int
    education: list[str]
    certifications: list[str]
    strengths: list[str]           # Puntos fuertes
    gaps: list[str]                # Huecos respecto a la oferta
```

**Lógica interna**:
1. **Analizar CV**: Extraer skills, experiencia, formación
2. **Comparar con oferta**: Identificar gaps y matches
3. **Consultar RAG**: Obtener mejores prácticas para CV
4. **Optimizar**: Reescribir descripciones, añadir keywords, destacar logros
5. **Generar resultado**: CV optimizado + resumen de cambios

**Estrategias de optimización**:
- **Keyword Matching**: Insertar keywords ATS de forma natural
- **Achievement Reframing**: Destacar logros cuantificables relevantes
- **Skills Repositioning**: Colocar skills más relevantes al inicio
- **Responsibility Alignment**: Alinear experiencia con requisitos del puesto

**Consulta RAG**: Busca en ChromaDB documentos sobre:
- Mejores prácticas para escribir CVs
- Ejemplos de CVs exitosos
- Consejos de reclutadores

**Prompt base**:
```
Eres un experto en optimización de currículums.

## Análisis de la oferta de empleo:
{job_analysis}

## CV original del candidato:
{cv_text}

## Mejores prácticas (de la base de conocimiento):
{rag_context}

## Instrucciones:
1. Analiza el CV y extrae las habilidades y experiencia del candidato
2. Compara con los requisitos de la oferta
3. Reescribe el CV optimizándolo para esta oferta específica:
   - Añade palabras clave ATS de forma natural
   - Destaca logros cuantificables
   - Reordena secciones por relevancia
   - NO inventes experiencia que el candidato no tiene
4. Devuelve el CV optimizado y una lista de cambios realizados
```

**Uso de LLM**: Ollama `qwen3:8b` con `temperature=0.4` (creatividad controlada)

---

### 3.4 Agente 3: ATS Reviewer + Final Reviewer

**Archivo**: `agents/ats_reviewer.py`

**Función**: Evaluar la compatibilidad ATS del CV optimizado Y realizar la revisión final de calidad.
(Este agente combina ATS evaluation + Final review)

**Entrada**:
- `optimized_cv: str` — CV optimizado del Agente 2
- `job_analysis: JobAnalysis` — Resultado del Agente 1
- `rag_context: str` — Contexto RAG sobre reglas ATS

**Salida** (Pydantic):
```python
class ATSReviewResult(BaseModel):
    ats_score: ATSScore            # Puntuación ATS detallada
    final_cv: str                  # CV final después de correcciones
    missing_keywords: list[str]    # Keywords que faltan
    found_keywords: list[str]      # Keywords encontradas
    recommendations: list[str]     # Recomendaciones finales
    improvements_applied: list[str] # Mejoras aplicadas en revisión final
```

```python
class ATSScore(BaseModel):
    keyword_match: float           # 0-100, coincidencia de keywords
    format_score: float            # 0-100, calidad del formato
    completeness: float            # 0-100, cobertura de requisitos
    overall_score: float           # 0-100, puntuación global
```

**Evaluación ATS (simulación)**:
1. **Keyword matching**: Comparar `job_analysis.keywords_ats` vs keywords en el CV
2. **Format check**: Verificar estructura (secciones, bullets, headers)
3. **Completeness**: ¿Cubre todos los requisitos principales?
4. **Readability**: Longitud de frases, uso de verbos de acción

**Revisión final**:
1. **Corrección gramatical**: Ortografía y gramática
2. **Eliminación de redundancias**: Quitar repeticiones
3. **Uniformidad de formato**: Consistencia visual
4. **Mejora de redacción**: Frases más impactantes

**Consulta RAG**: Busca en ChromaDB documentos sobre:
- Reglas de sistemas ATS
- Estrategias de optimización para filtros automáticos
- Formatos de CV compatibles con ATS

**Prompt base**:
```
Eres un sistema ATS (Applicant Tracking System) y revisor final de CVs.

## CV optimizado a evaluar:
{optimized_cv}

## Requisitos del puesto (keywords ATS):
{job_analysis.keywords_ats}

## Reglas ATS (de la base de conocimiento):
{rag_context}

## Tareas:
1. Evalúa la compatibilidad ATS:
   - ¿Qué keywords están presentes?
   - ¿Qué keywords faltan?
   - Puntuación global (0-100)
2. Realiza revisión final:
   - Corrige errores gramaticales
   - Elimina redundancias
   - Mejora la redacción
   - Uniformiza el formato
3. Devuelve el CV final corregido + reporte ATS
```

**Uso de LLM**: Ollama `qwen3:8b` con `temperature=0.2`

---

## 4. Base de Conocimiento RAG

### 4.1 Documentos

Se crearán versiones simplificadas de los siguientes documentos:

| Archivo | Contenido |
|---------|-----------|
| `docs/ats_rules.txt` | Reglas comunes de sistemas ATS, formatos compatibles, errores frecuentes |
| `docs/resume_best_practices.txt` | Mejores prácticas para escribir CVs, estructura recomendada, verbos de acción |
| `docs/recruitment_tips.txt` | Consejos de reclutadores, qué buscan, cómo destacar |

**Nota**: Se usarán archivos `.txt` en lugar de PDFs para simplificar. Si se quieren PDFs, se usará `PyPDFLoader`.

### 4.2 Flujo RAG

```
Archivos .txt (docs/)
    ↓
TextLoader / PyPDFLoader
    ↓
RecursiveCharacterTextSplitter
    chunk_size=500, chunk_overlap=50
    ↓
OllamaEmbeddings (nomic-embed-text)
    ↓
ChromaDB (persist_directory="./chroma_db")
    ↓
similarity_search(query, k=3)
    ↓
Contexto → Agentes
```

### 4.3 Configuración

```python
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "embedding_model": "nomic-embed-text",
    "collection_name": "cv_knowledge_base",
    "persist_directory": "./chroma_db",
    "top_k": 3,                    # Número de documentos a recuperar
}
```

### 4.4 Consultas por Agente

| Agente | Query ejemplo |
|--------|---------------|
| CV Optimizer | "mejores prácticas para escribir un currículum profesional" |
| ATS Reviewer | "reglas de sistemas ATS y formatos compatibles" |

---

## 5. Entrada de Datos

### 5.1 Formato de entrada

- **CV**: Archivo PDF → Se extrae texto con `PyPDFLoader` de LangChain
- **Oferta de empleo**: Archivo PDF o texto pegado directamente

### 5.2 Carga de archivos

```python
from langchain_community.document_loaders import PyPDFLoader

def load_pdf(file_path: str) -> str:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return "\n".join([page.page_content for page in pages])
```

---

## 6. Dependencias del Proyecto

```
langgraph>=0.2.0
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
pypdf>=5.0.0
pydantic>=2.0.0
ollama>=0.4.0
```

**Modelos Ollama necesarios** (descargar antes de ejecutar):
```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

---

## 7. Estructura de Carpetas

```
optimizador_project/
├── optimizador/
│   ├── __init__.py
│   ├── __main__.py              # Punto de entrada CLI
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── job_analyzer.py      # Agente 1: Análisis de oferta
│   │   ├── cv_optimizer.py      # Agente 2: Análisis + Optimización CV
│   │   └── ats_reviewer.py      # Agente 3: ATS + Revisión Final
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py          # LangGraph StateGraph (Supervisor)
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   └── vector_store.py      # ChromaDB + Embeddings
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic models (JobAnalysis, etc.)
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pdf_loader.py        # Utilidad para cargar PDFs
│   │
│   └── config.py                # Configuración global (modelos, RAG, etc.)
│
├── docs/                        # Documentos RAG (conocimiento)
│   ├── ats_rules.txt
│   ├── resume_best_practices.txt
│   └── recruitment_tips.txt
│
├── chroma_db/                   # Base de datos vectorial (auto-generada)
│
├── tests/
│   └── test_optimizador.py
│
├── data/                        # Datos de ejemplo
│   ├── sample_cv.pdf
│   └── sample_job_posting.txt
│
├── pyproject.toml
└── dev-requirements.txt
```

---

## 8. Flujo Completo del Sistema

```
1. Usuario ejecuta: python -m optimizador
2. Sistema solicita: ruta al CV (PDF) y oferta de empleo (PDF/texto)
3. Se cargan y extraen los textos de los PDFs

4. [Job Analyzer]
   Input:  job_posting_text
   Output: JobAnalysis (skills, keywords, seniority, etc.)

5. [CV Optimizer]
   Input:  cv_text + JobAnalysis + RAG context
   Output: CVOptimizationResult (CV optimizado + análisis + cambios)

6. [ATS Reviewer]
   Input:  optimized_cv + JobAnalysis + RAG context
   Output: ATSReviewResult (CV final + score ATS + recomendaciones)

7. Se muestra al usuario:
   - CV final optimizado
   - Puntuación ATS (keyword_match, format, overall)
   - Keywords encontradas y faltantes
   - Lista de cambios realizados
   - Recomendaciones finales
```

---

## 9. Salida Esperada (Ejemplo)

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
  1. Añadida sección de "Competencias técnicas" con keywords ATS
  2. Reescrito resumen profesional para destacar experiencia cloud
  3. Reordenadas experiencias por relevancia al puesto
  4. Añadidos verbos de acción en descripciones

💡 Recomendaciones:
  - Considerar añadir experiencia con Kubernetes
  - Incluir certificaciones AWS si las tienes
  - El formato es compatible con ATS

═══════════════════════════════════════════
  CV FINAL OPTIMIZADO
═══════════════════════════════════════════
[CV completo aquí...]
```

---

## 10. Plan de Implementación

### Fase 1: Base (Día 1-2)
- [ ] Crear estructura de carpetas
- [ ] Definir `models/schemas.py` con todos los modelos Pydantic
- [ ] Crear `config.py` con configuración global
- [ ] Crear `utils/pdf_loader.py`
- [ ] Verificar que Ollama funciona con `qwen3:8b` y `nomic-embed-text`

### Fase 2: RAG (Día 3)
- [ ] Escribir documentos simplificados en `docs/`
- [ ] Implementar `rag/vector_store.py` (carga, embedding, búsqueda)
- [ ] Probar que la búsqueda vectorial funciona

### Fase 3: Agentes (Día 4-6)
- [ ] Implementar `agents/job_analyzer.py`
- [ ] Implementar `agents/cv_optimizer.py` (con integración RAG)
- [ ] Implementar `agents/ats_reviewer.py` (con revisión final)
- [ ] Probar cada agente individualmente

### Fase 4: Orquestación (Día 7-8)
- [ ] Implementar `graph/workflow.py` con LangGraph StateGraph
- [ ] Conectar los 3 agentes en el flujo
- [ ] Implementar `__main__.py` como CLI
- [ ] Testing del pipeline completo

### Fase 5: Pulido (Día 9-10)
- [ ] Mejorar prompts según resultados
- [ ] Añadir manejo de errores
- [ ] Crear datos de ejemplo (sample_cv.pdf, sample_job_posting.txt)
- [ ] (Opcional) Interfaz Streamlit básica

---

## 11. Manejo de Errores

| Error | Acción |
|-------|--------|
| Ollama no está corriendo | Mensaje claro pidiendo `ollama serve` |
| Modelo no descargado | Mensaje pidiendo `ollama pull qwen3:8b` |
| PDF no se puede leer | Fallback a entrada de texto |
| LLM devuelve JSON inválido | Reintento con prompt más estricto (máx 2 intentos) |
| ChromaDB vacío | Advertir al usuario, ejecutar sin RAG |

---

## 12. Testing

```python
def test_full_pipeline():
    """Test del pipeline completo con datos de ejemplo"""
    job_posting = "Se busca desarrollador Python senior..."
    cv_text = "Juan García, Desarrollador con 5 años..."

    # Agente 1
    job_result = job_analyzer.analyze(job_posting)
    assert len(job_result.required_skills) > 0

    # Agente 2
    cv_result = cv_optimizer.optimize(cv_text, job_result, rag_context="")
    assert len(cv_result.optimized_cv) > len(cv_text)

    # Agente 3
    ats_result = ats_reviewer.review(cv_result.optimized_cv, job_result, rag_context="")
    assert 0 <= ats_result.ats_score.overall_score <= 100
    assert len(ats_result.final_cv) > 0
```

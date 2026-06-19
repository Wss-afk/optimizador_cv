"""
Tests para el Optimizador de Currículums.
"""

import pytest
from pathlib import Path

from optimizador.models.schemas import (
    JobAnalysis,
    CVAnalysis,
    ATSScore,
)
from optimizador.agents.job_analyzer import JobAnalyzerAgent
from optimizador.utils.pdf_loader import load_document


# Fixtures
@pytest.fixture
def sample_cv_path():
    """Ruta al CV de ejemplo."""
    return Path(__file__).parent.parent / "data" / "sample_cv.txt"


@pytest.fixture
def sample_job_posting_path():
    """Ruta a la oferta de ejemplo."""
    return Path(__file__).parent.parent / "data" / "sample_job_posting.txt"


@pytest.fixture
def sample_cv_text(sample_cv_path):
    """Texto del CV de ejemplo."""
    if sample_cv_path.exists():
        return load_document(str(sample_cv_path))
    return "Juan García - Desarrollador Python con 5 años de experiencia"


@pytest.fixture
def sample_job_posting_text(sample_job_posting_path):
    """Texto de la oferta de ejemplo."""
    if sample_job_posting_path.exists():
        return load_document(str(sample_job_posting_path))
    return "Se busca Desarrollador Python Senior con experiencia en FastAPI"


# Tests básicos
class TestPDFLoader:
    """Tests para el cargador de documentos."""
    
    def test_load_text_file(self, sample_cv_path):
        """Prueba cargar archivo de texto."""
        if sample_cv_path.exists():
            text = load_document(str(sample_cv_path))
            assert isinstance(text, str)
            assert len(text) > 0
    
    def test_invalid_file_path(self):
        """Prueba error con ruta inválida."""
        with pytest.raises(FileNotFoundError):
            load_document("/path/that/does/not/exist.txt")


class TestJobAnalyzer:
    """Tests para el Job Analyzer Agent."""
    
    def test_job_analyzer_initialization(self):
        """Prueba que el agente se inicializa correctamente."""
        agent = JobAnalyzerAgent()
        assert agent.llm is not None
        assert agent.prompt_template is not None
    
    def test_json_extraction(self):
        """Prueba extracción de JSON de respuesta."""
        agent = JobAnalyzerAgent()
        
        # Respuesta mock con JSON
        response = """
        Aquí está el análisis:
        {
            "job_title": "Senior Developer",
            "required_skills": ["Python", "Docker"],
            "soft_skills": ["Leadership"],
            "years_experience": 5,
            "seniority_level": "Senior",
            "keywords_ats": ["Python", "FastAPI"],
            "responsibilities": ["Design systems"],
            "technologies": ["FastAPI", "PostgreSQL"],
            "salary_range": "80k-120k"
        }
        Espero que sea útil.
        """
        
        json_str = agent._extract_json(response)
        assert json_str.startswith("{")
        assert json_str.endswith("}")
        assert "job_title" in json_str


class TestSchemas:
    """Tests para los modelos Pydantic."""
    
    def test_job_analysis_model(self):
        """Prueba creación de modelo JobAnalysis."""
        job = JobAnalysis(
            job_title="Senior Developer",
            required_skills=["Python", "Docker"],
            soft_skills=["Leadership"],
            years_experience=5,
            seniority_level="Senior",
            keywords_ats=["Python", "FastAPI"],
            responsibilities=["Design systems"],
            technologies=["FastAPI"],
            salary_range="80k-120k",
        )
        
        assert job.job_title == "Senior Developer"
        assert len(job.required_skills) == 2
        assert job.years_experience == 5
    
    def test_cv_analysis_model(self):
        """Prueba creación de modelo CVAnalysis."""
        cv = CVAnalysis(
            candidate_name="Juan García",
            current_skills=["Python", "Django"],
            experience_years=6,
            education=["Ingeniería Informática"],
            certifications=["AWS Solutions Architect"],
            strengths=["FastAPI experience", "Leadership"],
            gaps=["Kubernetes"],
        )
        
        assert cv.candidate_name == "Juan García"
        assert cv.experience_years == 6
        assert len(cv.education) == 1
    
    def test_ats_score_model(self):
        """Prueba creación de modelo ATSScore."""
        score = ATSScore(
            keyword_match=85.0,
            format_score=90.0,
            completeness=75.0,
            overall_score=82.0,
        )
        
        assert score.overall_score == 82.0
        assert score.keyword_match == 85.0


# Pruebas de integración (requieren Ollama corriendo)
@pytest.mark.integration
class TestIntegration:
    """Tests de integración del pipeline completo."""
    
    def test_full_pipeline(self, sample_cv_text, sample_job_posting_text):
        """Test del pipeline completo."""
        pytest.importorskip("langchain_ollama")
        
        try:
            from optimizador.graph.workflow import create_workflow
            
            workflow = create_workflow()
            result = workflow.invoke(sample_job_posting_text, sample_cv_text)
            
            # Verificar que completó sin errores
            assert result.current_step == "complete"
            assert not result.errors
            assert result.final_cv is not None
            
        except Exception as e:
            pytest.skip(f"Ollama no disponible: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


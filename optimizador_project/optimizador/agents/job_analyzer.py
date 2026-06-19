"""
Job Analyzer Agent: Analiza ofertas de empleo y extrae información estructurada.
"""

import json
import logging
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from optimizador.models.schemas import JobAnalysis
from optimizador.config import LLM_CONFIG, PROMPTS, AGENTS_CONFIG

logger = logging.getLogger(__name__)


class JobAnalyzerAgent:
    """Agente para analizar ofertas de empleo."""
    
    def __init__(self):
        """Inicializa el agente con el modelo LLM."""
        self.config = AGENTS_CONFIG["job_analyzer"]
        self.llm = ChatOllama(
            model=self.config["model"],
            temperature=self.config["temperature"],
            base_url=LLM_CONFIG["base_url"],
            request_timeout=LLM_CONFIG["request_timeout"],
        )
        self.prompt_template = PROMPTS["job_analyzer"]
    
    def analyze(self, job_posting_text: str) -> JobAnalysis:
        """
        Analiza una oferta de empleo y extrae información estructurada.
        
        Args:
            job_posting_text: Texto completo de la oferta de empleo
            
        Returns:
            JobAnalysis con la información extraída
            
        Raises:
            ValueError: Si no se puede parsear la respuesta del LLM
        """
        logger.info("Iniciando análisis de oferta de empleo...")
        
        # Preparar prompt
        prompt = self.prompt_template.format(job_posting_text=job_posting_text)
        
        try:
            # Llamar al LLM
            logger.debug(f"Enviando prompt al LLM ({self.config['model']})...")
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            response_text = response.content
            
            logger.debug(f"Respuesta del LLM recibida ({len(response_text)} chars)")
            
            # Parsear JSON de la respuesta
            job_analysis = self._parse_response(response_text)
            
            logger.info(f"Análisis completado: {job_analysis.job_title}")
            return job_analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de oferta: {str(e)}")
            raise
    
    def _parse_response(self, response_text: str) -> JobAnalysis:
        """
        Parsea la respuesta del LLM en un objeto JobAnalysis.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            JobAnalysis parseado
            
        Raises:
            ValueError: Si no se puede parsear el JSON
        """
        try:
            # Intenta extraer JSON de la respuesta
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)
            
            # Validar y crear objeto Pydantic
            job_analysis = JobAnalysis(
                job_title=data.get("job_title", "Unknown"),
                required_skills=data.get("required_skills", []),
                soft_skills=data.get("soft_skills", []),
                years_experience=int(data.get("years_experience", 0)),
                seniority_level=data.get("seniority_level", "Mid"),
                keywords_ats=data.get("keywords_ats", []),
                responsibilities=data.get("responsibilities", []),
                technologies=data.get("technologies", []),
                salary_range=data.get("salary_range"),
            )
            
            return job_analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            logger.debug(f"Respuesta del LLM: {response_text[:500]}")
            raise ValueError(f"No se pudo parsear la respuesta del LLM como JSON: {str(e)}")
    
    def _extract_json(self, text: str) -> str:
        """
        Extrae JSON de un texto que puede contener explicación.
        
        Args:
            text: Texto que contiene JSON
            
        Returns:
            String JSON válido
            
        Raises:
            ValueError: Si no encuentra JSON válido
        """
        # Intenta encontrar el JSON entre llaves
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No se encontró JSON en la respuesta")
        
        json_str = text[start_idx:end_idx]
        return json_str


def create_job_analyzer() -> JobAnalyzerAgent:
    """Factory para crear instancia del agente."""
    return JobAnalyzerAgent()

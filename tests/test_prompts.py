"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega o prompt v2 antes de cada teste."""
        data = load_prompts(PROMPT_PATH)
        self.prompt_key = list(data.keys())[0]
        self.prompt = data[self.prompt_key]
        self.system_prompt = self.prompt.get("system_prompt", "")

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' não encontrado"
        assert self.system_prompt.strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        text = self.system_prompt.lower()
        role_keywords = ["você é", "voce é", "você é um", "product manager", "especialista", "senior", "sênior"]
        has_role = any(keyword in text for keyword in role_keywords)
        assert has_role, "Prompt não define uma persona/role. Esperado palavras como 'Você é', 'Product Manager', 'especialista'"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text = self.system_prompt.lower()
        format_keywords = ["markdown", "user story", "como um", "eu quero", "para que", "critérios de aceitação", "dado que", "quando", "então"]
        matches = [kw for kw in format_keywords if kw in text]
        assert len(matches) >= 2, f"Prompt não menciona formato User Story ou Markdown suficientemente. Encontrados: {matches}"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = self.system_prompt.lower()
        example_indicators = ["exemplo", "bug report:", "bug report", "user story:", "**bug report:**", "exemplo 1", "exemplo 2"]
        matches = [kw for kw in example_indicators if kw in text]
        assert len(matches) >= 2, f"Prompt não contém exemplos Few-shot suficientes. Encontrados: {matches}"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        assert "[TODO]" not in self.system_prompt, "system_prompt ainda contém '[TODO]'"
        user_prompt = self.prompt.get("user_prompt", "")
        assert "[TODO]" not in user_prompt, "user_prompt ainda contém '[TODO]'"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)} - {techniques}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

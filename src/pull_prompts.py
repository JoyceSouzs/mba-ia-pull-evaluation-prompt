"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt bug_to_user_story_v1 do LangSmith Hub
    e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário
    """
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    try:
        print(f"   Puxando prompt: {prompt_name}")
        prompt = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso do Hub")

        # Extrair system_prompt e user_prompt do ChatPromptTemplate
        system_prompt = ""
        user_prompt = ""

        for message in prompt.messages:
            if hasattr(message, 'prompt'):
                template = message.prompt.template
            elif hasattr(message, 'content'):
                template = message.content
            else:
                continue

            msg_type = type(message).__name__.lower()
            if "system" in msg_type:
                system_prompt = template
            elif "human" in msg_type:
                user_prompt = template

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }

        if save_yaml(prompt_data, output_path):
            print(f"   ✓ Prompt salvo em: {output_path}")
            return True
        else:
            print(f"   ❌ Erro ao salvar prompt")
            return False

    except Exception as e:
        print(f"   ❌ Erro ao fazer pull: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    print("Iniciando pull de prompts...\n")

    if pull_prompts_from_langsmith():
        print("\n✅ Pull concluído com sucesso!")
        print("   Arquivo salvo: prompts/bug_to_user_story_v1.yml")
        return 0
    else:
        print("\n❌ Falha ao fazer pull dos prompts")
        return 1


if __name__ == "__main__":
    sys.exit(main())

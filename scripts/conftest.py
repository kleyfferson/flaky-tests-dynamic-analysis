import pytest
from pathlib import Path
from Analise.TestResult import TestResult

# 1. Cria os argumentos customizados na linha de comando do Pytest
def pytest_addoption(parser):
    parser.addoption("--meu-trace", action="store_true", help="Ativa o tracing hierárquico")
    parser.addoption("--output-dir", action="store", default=".", help="Diretório onde o calls.gz será salvo")
    parser.addoption("--project-root", action="store", default="", help="Pasta do projeto alvo (ex: airflow)")

# 2. Se o argumento --meu-trace for passado, ativa o plugin nativamente em memória
def pytest_configure(config):
    if config.getoption("--meu-trace"):
        plugin = TestResult(
            trace=True,
            prof=False,
            cov=False,
            outputDir=config.getoption("--output-dir"),
            project_root_dir=config.getoption("--project-root"),
            automation_root=Path('/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o')
        )
        # Registra o plugin no motor interno do Pytest
        config.pluginmanager.register(plugin, 'tracing_hierarquico_plugin')

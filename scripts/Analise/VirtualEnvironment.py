import subprocess
import os
import shutil
import sys
import time
import re
import json  # Importação crucial para ler o relatório do Pytest

class VirtualEnvironment:
    def __init__(self, venv_dir: str, repo_name: str) -> None:
        self._venv_dir = os.path.abspath(venv_dir)
        self._python_bin = os.path.join(self._venv_dir, "bin", "python")
        self._real_project_dir = os.path.dirname(self._venv_dir) 
        self._repo_name = repo_name
        
        # Descoberta dinâmica do site-packages para suportar a injeção .pth
        self._site_packages = None
        lib_dir = os.path.join(self._venv_dir, "lib")
        if os.path.exists(lib_dir):
            for py_dir in os.listdir(lib_dir):
                sp = os.path.join(lib_dir, py_dir, "site-packages")
                if os.path.exists(sp):
                    self._site_packages = sp
                    break
        if not self._site_packages:
            self._site_packages = os.path.join(self._venv_dir, "lib", "python3.8", "site-packages")

    def executePytest(self, test_node, output_base, count, analise, test_hash="unknown"):
        run_dir = os.path.join(output_base, f"Run-{count}")
        os.makedirs(run_dir, exist_ok=True)
        
        # --- TRAVA DE SEGURANÇA PARA O [ERRNO 2] ---
        if not os.path.exists(self._python_bin):
            raise FileNotFoundError(f"[Errno 2] O executável Python NÃO foi encontrado em: {self._python_bin}. Verifique o nome da pasta do ambiente virtual no PROJECT_CONFIGS!")

        # --- NOVA TRAVA: ALINHAMENTO DE REPOSITÓRIO (Corrige contaminação de caminhos no CSV) ---
        if self._real_project_dir not in test_node:
            print(f"\n[ERRO CRÍTICO DE MAPEAMENTO] Linha inválida no flaky.csv detectada!")
            print(f"O projeto informado foi '{self._repo_name}' ({self._real_project_dir})")
            print(f"Mas o caminho do teste pertence a outro lugar: '{test_node}'")
            return subprocess.CompletedProcess(
                args=[test_node],
                returncode=4,
                stdout="",
                stderr=f"Erro de consistência: O teste informado não pertence ao diretório do projeto {self._repo_name}."
            )

        repo_lower = self._repo_name.lower()

        # ==========================================================
        # INTERCEPÇÃO E CORREÇÃO AUTOMÁTICA DA CLASSE DO VERIFONE
        # ==========================================================
        if repo_lower == "verifone" and "test_verifone.py" in test_node and "::TestVerifone::" not in test_node:
            test_node = test_node.replace("test_verifone.py::", "test_verifone.py::TestVerifone::")

        test_file_name_raw = test_node.split("::")[-1].split("/")[-1].replace(".py", "")
        test_file_name = re.sub(r'[^a-zA-Z0-9_]', '_', test_file_name_raw)

        env = os.environ.copy()
        
        src_dir = os.path.join(self._real_project_dir, "src")
        env["PYTHONPATH"] = os.pathsep.join([src_dir, self._real_project_dir, os.getcwd()])
        env["VIRTUAL_ENV"] = self._venv_dir
        env["PATH"] = os.path.join(self._venv_dir, "bin") + os.pathsep + env.get("PATH", "")
        
        # Isola o arquivo de coverage
        env["COVERAGE_FILE"] = os.path.join(run_dir, ".coverage")

        # Identifica o runner original do seu framework
        if repo_lower in ["python-matlab-functions", "torch-embed-sim", "torch-layer-normalization"]:
            runner = "nose"
        elif repo_lower in ["verifone"]:
            runner = "unittest"
        else:
            runner = "pytest"

        # ==========================================================
        # SOLUÇÃO PARA O TRACING DO VERIFONE / NOSE:
        # ==========================================================
        if analise == "tracing":
            runner = "pytest"

        # --- LÓGICA INTELIGENTE DE TRADUÇÃO E LIMPEZA DOS TESTES ---
        if "::" in test_node:
            parts = test_node.split("::")
            
            if runner == "pytest":
                if len(parts) == 3:
                    file_base = os.path.basename(parts[0]).replace(".py", "")
                    if parts[1] == file_base:
                        test_node = f"{parts[0]}::{parts[2]}"

            elif runner == "nose":
                if len(parts) == 3:
                    test_node = f"{parts[0]}:{parts[1]}.{parts[2]}"
                elif len(parts) == 2:
                    test_node = f"{parts[0]}:{parts[1]}"

            elif runner == "unittest":
                module_path = parts[0].replace(self._real_project_dir + "/", "").replace(".py", "").replace("/", ".")
                if len(parts) == 3:
                    test_node = f"{module_path}.{parts[1]}.{parts[2]}"
                elif len(parts) == 2:
                    test_node = f"{module_path}.{parts[1]}"

        # Caminhos base de arquivos de saída
        coverage_file = os.path.join(run_dir, f"coverage_{count}.xml")
        prof_out = os.path.join(run_dir, f"profiling_{count}.prof")
        json_report_file = os.path.join(run_dir, f"resultado_{analise}.json")

        pth_file_path = os.path.join(self._site_packages, "auto_trace_link.pth")
        TOOL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 1. Configuração do comando para COVERAGE
        if analise == "coverage":
            if runner == "nose":
                cmd = [self._python_bin, "-m", "nose", "--with-coverage", "--cover-xml", f"--cover-xml-file={coverage_file}", test_node]
            elif runner == "unittest":
                cmd = [self._python_bin, "-m", "coverage", "run", "-m", "unittest", test_node]
            else:
                cmd = [self._python_bin, "-m", "pytest", test_node, f"--cov={self._real_project_dir}", f"--cov-report=xml:{coverage_file}", "--json-report", f"--json-report-file={json_report_file}"]

        # 2. Configuração do comando para PROFILING
        elif analise == "profiling":
            if runner == "nose":
                cmd = [self._python_bin, "-m", "cProfile", "-o", prof_out, "-m", "nose", test_node]
            elif runner == "unittest":
                cmd = [self._python_bin, "-m", "cProfile", "-o", prof_out, "-m", "unittest", test_node]
            else:
                cmd = [self._python_bin, "-m", "cProfile", "-o", prof_out, "-m", "pytest", test_node, "--json-report", f"--json-report-file={json_report_file}"]

        # 3. Configuração do comando para TRACING 
        elif analise == "tracing":
            if runner == "pytest":
                env["AUTO_TRACE"] = "True"
                env["AUTO_PROF"] = "False"
                env["AUTO_OUTPUT_DIR"] = run_dir
                env["AUTO_TEST_NAME"] = test_file_name
                env["AUTO_AUTOMATION_ROOT"] = TOOL_ROOT
                env["AUTO_PROJECT_ROOT"] = os.path.abspath(self._real_project_dir)
                
                try:
                    os.makedirs(self._site_packages, exist_ok=True)
                    with open(pth_file_path, "w", encoding="utf-8") as f_pth:
                        f_pth.write(TOOL_ROOT + "\n")
                except Exception as e:
                    print(f"[AVISO] Falha ao criar vínculo de ambiente .pth: {e}")
                
                env["PYTEST_PLUGINS"] = "Analise.tracing_plugin"

            if runner == "nose":
                cmd = [self._python_bin, "-m", "nose", test_node]
            elif runner == "unittest":
                cmd = [self._python_bin, "-m", "unittest", test_node]
            else:
                if "::" in test_node:
                    parts = test_node.split("::")
                    file_path = parts[0]
                    test_method = parts[-1]
                    cmd = [self._python_bin, "-m", "pytest", file_path, "-k", test_method, "--json-report", f"--json-report-file={json_report_file}"]
                else:
                    cmd = [self._python_bin, "-m", "pytest", test_node, "--json-report", f"--json-report-file={json_report_file}"]
        
        # Execução Padrão
        else:
            if runner == "nose":
                cmd = [self._python_bin, "-m", "nose", test_node]
            elif runner == "unittest":
                cmd = [self._python_bin, "-m", "unittest", test_node]
            else:
                cmd = [self._python_bin, "-m", "pytest", test_node, "--json-report", f"--json-report-file={json_report_file}"]

        # --- EXECUÇÃO DO PROCESSO ---
        resultado = subprocess.run(cmd, env=env, cwd=self._real_project_dir, capture_output=True, text=True)

        # Remove o link temporário após a execução para limpar o ambiente
        if analise == "tracing" and runner == "pytest" and os.path.exists(pth_file_path):
            try:
                os.remove(pth_file_path)
            except:
                pass

        # ====================================================================
        # CORREÇÃO DEFINITIVA DO FALSO POSITIVO DO PROFILING (E OUTROS)
        # ====================================================================
        
        # 1. Status inicial baseado no terminal
        status_da_run = "Passed" if resultado.returncode == 0 else "Failed"

        # 2. A VERDADE ABSOLUTA: Lendo o relatório interno gerado pelo Pytest
        comando_texto = " ".join(cmd)
        if "pytest" in comando_texto: 
            if os.path.exists(json_report_file):
                try:
                    with open(json_report_file, 'r', encoding='utf-8') as f_json:
                        relatorio = json.load(f_json)
                        resumo = relatorio.get("summary", {})
                        
                        # O Pytest diz a verdade aqui
                        if "failed" in resumo or "error" in resumo:
                            status_da_run = "Failed"
                        elif "passed" in resumo:
                            status_da_run = "Passed"
                        elif resumo.get("collected", 0) == 0:
                            # Se não achou nenhum teste, falhou
                            status_da_run = "Failed" 
                except Exception as e:
                    print(f"Aviso: Erro ao ler JSON de validação do Pytest: {e}")
                    status_da_run = "Failed"
            else:
                # Se o Pytest nem sequer gerou o JSON, o teste sofreu um crash fatal
                status_da_run = "Failed"
                
        # 3. Tratamento para Projetos legados (Unittest / Nose)
        elif runner in ["unittest", "nose"]:
            saida_completa = resultado.stdout + "\n" + resultado.stderr
            # Procura por palavras-chave de falha na saída de texto
            if "FAILED" in saida_completa or "ERROR" in saida_completa or "Traceback" in saida_completa:
                status_da_run = "Failed"
            elif "OK" in saida_completa:
                status_da_run = "Passed"

        # === GRAVAÇÃO DO STATUS REAL DA RUN EM TXT ===
        status_file_path = os.path.join(run_dir, f"status_run_{analise}.txt")
        try:
            with open(status_file_path, "w", encoding="utf-8") as f_status:
                f_status.write(status_da_run)
        except Exception as e:
            print(f"Aviso: Não foi possível gravar o log txt de status: {e}")

        # Exportação para XML caso seja unittest e Coverage
        if analise == "coverage" and runner == "unittest":
            subprocess.run([
                self._python_bin, "-m", "coverage", "xml",
                "-o", coverage_file
            ], env=env, cwd=self._real_project_dir, capture_output=True)

        # Se houver falha (mesmo que o terminal tenha dito código 0), gera log da falha
        if resultado.returncode != 0 or status_da_run == "Failed":
            evidencia_file = os.path.join(run_dir, f"evidencia_crash_{analise}.log")
            with open(evidencia_file, "w", encoding="utf-8") as f:
                f.write(f"=== EVIDÊNCIA DE FALHA NO {analise.upper()} ===\n")
                f.write(f"Projeto: {self._repo_name}\n")
                f.write(f"Comando Executado: {' '.join(cmd)}\n")
                f.write(f"Código de Saída Terminal (Return Code): {resultado.returncode}\n")
                f.write(f"Status Real Identificado: {status_da_run}\n")
                f.write(f"\n--- SAÍDA PADRÃO (STDOUT) ---\n{resultado.stdout}\n")
                f.write(f"\n--- ERROS (STDERR) ---\n{resultado.stderr}\n")

        return resultado

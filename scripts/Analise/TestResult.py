"""
Plugin Blindado do Pytest para recolher resultados (Tracing e Profiling).
Suporta concorrência agressiva, Threads e Multiprocessamento (pytest-xdist).
Versão Científica Otimizada contra estouro de memória RAM em requisições de API.
"""
from typing import List, Tuple, Any
from pathlib import Path
import pytest
import sys
import cProfile
import os
import gzip
import shutil
import threading

class TestResult:
    def __init__(self, trace: bool = False, prof: bool = False, cov: bool = False, 
                 outputDir: str = ".", testName: str = "",
                 automation_root: Path = None, project_root_dir: str = ""):
        
        self.testName = testName
        self.outputDir = outputDir
        self.cov = cov
        self.trace = trace
        self.prof = prof
        
        self.automation_root = automation_root
        # Força o diretório do projeto a ser estritamente absoluto
        self.project_root_dir = os.path.abspath(project_root_dir) if project_root_dir else ""
        
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0

        self.profiler = cProfile.Profile() if self.prof else None
        self.trace_depth = 0 
        
        self.pid = os.getpid()
        self.txt_path = os.path.join(self.outputDir, f"calls_temp_{self.pid}.txt")
        self.gz_path = os.path.join(self.outputDir, "calls.gz")
        
        self.trace_file = None
        self.lock = threading.Lock() 
        
        if self.trace:
            try:
                self.trace_file = open(self.txt_path, "a", encoding="utf-8")
            except Exception as e:
                print(f"[TRACE INIT ERROR] Processo {self.pid} falhou ao iniciar arquivo: {e}")

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        if self.prof and self.profiler:
            self.profiler.enable()
        if self.trace and self.trace_file:
            sys.settrace(self.hierarchical_trace)
            try:
                import threading
                threading.settrace(self.hierarchical_trace)
            except:
                pass
        
        yield
        
        if self.trace:
            sys.settrace(None)
            try:
                import threading
                threading.settrace(None)
            except:
                pass
        if self.prof and self.profiler:
            self.profiler.disable()

    def hierarchical_trace(self, frame, event, arg):
        if event not in ('call', 'return'):
            return self.hierarchical_trace

        # --- FILTRO JATO: Ignora libs externas ANTES de gastar CPU com abspath ---
        # Evita que chamadas internas de pacotes de rede (urllib3, requests, ssl) inundem a memória RAM
        co_filename = frame.f_code.co_filename
        if "site-packages" in co_filename or "lib/python" in co_filename or co_filename.startswith("<"):
            return None

        # Só faz o abspath (que é pesado) se o arquivo realmente passar pelo filtro inicial
        file_path = os.path.abspath(co_filename)
        
        if not self.project_root_dir or self.project_root_dir not in file_path:
            return None

        func_name = frame.f_code.co_name

        if event == 'call':
            indent = ">" * self.trace_depth
            try:
                with self.lock: 
                    self.trace_file.write(f"{indent} {func_name} in {file_path}\n")
            except:
                pass
            self.trace_depth += 1
            return self.hierarchical_trace
            
        elif event == 'return':
            self.trace_depth = max(0, self.trace_depth - 1)
            indent = "<" * self.trace_depth
            
            return_value_str = repr(arg)
            if len(return_value_str) > 50:
                return_value_str = return_value_str[:50] + "..."
                
            try:
                with self.lock:
                    self.trace_file.write(f"{indent} {func_name} returned: {return_value_str}\n")
            except:
                pass
            return self.hierarchical_trace

        return self.hierarchical_trace

    def pytest_sessionfinish(self, session, exitstatus):
        if self.trace and self.trace_file:
            try:
                self.trace_file.close()
                
                # Só consolida se o arquivo temporário realmente conter dados válidos
                if os.path.exists(self.txt_path) and os.path.getsize(self.txt_path) > 0:
                    with open(self.txt_path, 'rb') as f_in:
                        with gzip.open(self.gz_path, 'ab') as f_out: 
                            shutil.copyfileobj(f_in, f_out)
                    try:
                        os.remove(self.txt_path)
                    except:
                        pass
            except Exception as e:
                print(f"\n[TRACE] Erro crítico ao consolidar gzip: {e}")

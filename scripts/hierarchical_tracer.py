import sys
import gzip
import os
import pytest

# Captura os argumentos
output_path = os.path.abspath(sys.argv[1])
test_node = sys.argv[2]

# GARANTE QUE A PASTA EXISTE antes de tentar criar o arquivo
os.makedirs(os.path.dirname(output_path), exist_ok=True)

class SimpleTracer:
    def __init__(self, output_file):
        self.output_file = output_file
        # Abre o arquivo gzip imediatamente para testar permissão
        try:
            self.f = gzip.open(self.output_file, 'wt', encoding='utf-8')
        except Exception as e:
            print(f"ERRO CRÍTICO AO ABRIR ARQUIVO: {e}")
            sys.exit(1)

    def trace_calls(self, frame, event, arg):
        if event == 'call':
            func_name = frame.f_code.co_name
            filename = frame.f_code.co_filename
            
            # FILTRO CORRIGIDO: Garante que tem 'graphene' no caminho, mas IGNORA o 'venv' e 'site-packages'
            if "graphene" in filename and "venv" not in filename and "site-packages" not in filename:
                self.f.write(f"> {func_name} in {filename}\n")
                
        elif event == 'return':
            # Limpeza do valor de retorno para evitar lixo binário no CSV
            try:
                ret_str = str(arg).replace('\n', ' ').replace('\r', '')
                # Limita o tamanho da string para não quebrar o CSV com retornos gigantes
                if len(ret_str) > 100:
                    ret_str = ret_str[:97] + "..."
            except Exception:
                ret_str = "unserializable"
                
            self.f.write(f"< returned: {ret_str}\n")
            
        return self.trace_calls

    def close(self):
        self.f.flush()
        self.f.close()

# Inicializa o tracer
tracer = SimpleTracer(output_path)
sys.settrace(tracer.trace_calls)

try:
    # Executa o pytest
    pytest.main(['--ignore=pytest.ini', test_node])
finally:
    # FINALIZAÇÃO MANDATÓRIA
    sys.settrace(None)
    tracer.close()
    print(f"Trace finalizado e arquivo fechado em: {output_path}")

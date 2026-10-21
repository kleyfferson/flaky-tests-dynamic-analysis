import csv
import pstats
import argparse
import os

def parse_profiling_data(input_file, output_file, repo_name, test_name, run_num, status):
    if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
        print(f"Aviso: Arquivo de profiling vazio ou inexistente: {input_file}")
        return
    try:
        stats = pstats.Stats(input_file)
        stats.sort_stats('cumulative')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Cabeçalho Padronizado
            writer.writerow(['Project Name', 'Test Name', 'Run', 'Test Result', 'ncalls', 'tottime', 'percall', 'cumtime', 'percall_cum', 'filename:lineno(function)'])
            
            for func, (cc, nc, tt, ct, callers) in stats.stats.items():
                filename = f"{func[0]}:{func[1]}({func[2]})"
                
                # Prevenção de divisão por zero
                percall = tt / nc if nc > 0 else 0
                
                # CORREÇÃO MATEMÁTICA APLICADA AQUI: usando 'cc' (chamadas primitivas) em vez de 'nc'
                percall_cum = ct / cc if cc > 0 else 0
                
                writer.writerow([repo_name, test_name, run_num, status, nc, f"{tt:.9f}", f"{percall:.9f}", f"{ct:.9f}", f"{percall_cum:.9f}", filename])
    except Exception as e:
        print(f"Erro no parse de profiling: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_file", required=True)
    parser.add_argument("--repo-name", default="Unknown")
    parser.add_argument("--test-name", default="Unknown")
    parser.add_argument("--run", default="1")
    parser.add_argument("--status", default="Passed")
    args = parser.parse_args()

    parse_profiling_data(args.input_file, args.output_file, args.repo_name, args.test_name, args.run, args.status)

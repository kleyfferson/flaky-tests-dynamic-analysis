import gzip
import csv
import argparse
import os

def convert_gz_to_csv(input_gz, output_csv, repo_name, test_name, run_num, status):
    functions = {}
    
    if not os.path.exists(input_gz) or os.path.getsize(input_gz) == 0:
        print(f"Aviso: Arquivo de tracing vazio ou inexistente: {input_gz}")
        return
        
    try:
        with gzip.open(input_gz, 'rt', encoding='utf-8') as f:
            for line in f:
                # Detecta chamadas (linhas que começam com >)
                if line.strip().startswith('>'):
                    # Limpa a linha para pegar só o nome da função
                    parts = line.replace('>', '').strip().split(' in ')
                    if len(parts) > 0:
                        func_name = parts[0]
                        functions[func_name] = functions.get(func_name, 0) + 1
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Cabeçalho Padronizado
            writer.writerow(['Project Name', 'Test Name', 'Run', 'Test Result', 'Function', 'Call_Frequency'])
            
            for func, count in sorted(functions.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([repo_name, test_name, run_num, status, func, count])
        
        print(f"Sucesso: {output_csv} gerado.")
    except Exception as e:
        print(f"Erro ao converter: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_file", required=True)
    parser.add_argument("--repo-name", default="Unknown")
    parser.add_argument("--test-name", default="Unknown")
    parser.add_argument("--run", default="0")
    parser.add_argument("--status", default="Unknown")
    args = parser.parse_args()
    
    convert_gz_to_csv(args.input_file, args.output_file, args.repo_name, args.test_name, args.run, args.status)

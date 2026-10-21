import gzip
import csv
import sys
import os

def convert_gz_to_csv(input_gz, output_csv):
    data = {}
    
    try:
        if not os.path.exists(input_gz):
            print(f"Erro: Arquivo {input_gz} nao encontrado.")
            return

        with gzip.open(input_gz, 'rb') as f:
            lines_processed = 0
            for binary_line in f:
                try:
                    line = binary_line.decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    
                    lines_processed += 1
                    
                    # Se a linha tem ' in ', ela segue o formato: nome_funcao in arquivo.py
                    if ' in ' in line:
                        # Remove setas ou lixo do início
                        parts = line.split(' in ')
                        func_part = parts[0].strip()
                        # Pega apenas a última palavra (o nome da função real)
                        func_name = func_part.split()[-1].strip('>< ')
                        
                        if func_name:
                            if func_name not in data:
                                data[func_name] = {"count": 0, "returns": set()}
                            data[func_name]["count"] += 1
                            
                            # Captura o retorno se estiver na mesma linha ou tiver 'returned:'
                            if 'returned:' in line:
                                ret_val = line.split('returned:')[1].strip()
                                data[func_name]["returns"].add(ret_val)
                except:
                    continue

        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Function', 'Call_Frequency', 'Unique_Return_Values'])
            
            for func, info in sorted(data.items(), key=lambda x: x[1]["count"], reverse=True):
                rets = " | ".join(list(info["returns"])[:5])
                writer.writerow([func, info["count"], rets if rets else "None"])

        if data:
            print(f"Sucesso: {len(data)} funcoes extraidas de {lines_processed} linhas.")
        else:
            print(f"Aviso: Foram lidas {lines_processed} linhas, mas nenhuma tinha o formato 'funcao in arquivo'.")

    except Exception as e:
        print(f"Erro critico: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 converter_tracing.py <input.gz> <output.csv>")
    else:
        convert_gz_to_csv(sys.argv[1], sys.argv[2])

import argparse
import os
import csv
import xml.etree.ElementTree as ET

def main():
    parser = argparse.ArgumentParser(description="Converte arquivos XML de Cobertura em planilhas CSV individuais.")
    parser.add_argument("--xml", required=True, help="Caminho do arquivo XML de cobertura gerado pelo runner")
    parser.add_argument("--csv", required=True, help="Caminho do arquivo CSV de saída")
    parser.add_argument("--repo-name", required=True, help="Nome do projeto sob análise")
    parser.add_argument("--test-name", required=True, help="Nome do nó do teste")
    parser.add_argument("--run", required=True, help="Índice da execução (Run)")
    parser.add_argument("--status", required=True, help="Status final do teste (Passed ou Failed)")

    args = parser.parse_args()

    if not os.path.exists(args.xml):
        print(f"[ERRO] O arquivo XML especificado não existe: {args.xml}")
        return

    try:
        tree = ET.parse(args.xml)
        root = tree.getroot()

        # Captura os metadados nativos da tag raiz do relatório XML do Cobertura
        lines_valid = root.get('lines-valid', '0')
        lines_covered = root.get('lines-covered', '0')
        line_rate = root.get('line-rate', '0')

        # Converte a taxa em porcentagem real (ex: 0.9134 -> 91.34)
        try:
            percentual = float(line_rate) * 100
        except ValueError:
            percentual = 0.0

        linhas_cobertas_str = f"{lines_covered}/{lines_valid}"

        # Assegura a criação do diretório de saída caso não exista
        os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)

        # Monta a estrutura rigorosamente mapeada para leitura do main.py
        with open(args.csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho exigido pelo laço do main.py (necessário pois há o descarte via next())
            writer.writerow(['Project Name', 'Test name', 'Run', 'Test Result', 'Percentual de Cobertura (%)', 'Linhas Cobertas'])
            
            # Registro de dados processados
            writer.writerow([
                args.repo_name,
                args.test_name,
                args.run,
                args.status,
                f"{percentual:.2f}",
                linhas_cobertas_str
            ])

        print(f"[CONVERSÃO] XML processado com sucesso para: {args.csv}")

    except Exception as e:
        print(f"[ERRO] Falha crítica ao interpretar as tags do XML de coverage: {e}")

if __name__ == "__main__":
    main()

import os
import csv

def analisar_resultados_por_teste(ficheiro_caminhos):
    print("="*80)
    print(f"ANALISANDO RESULTADOS DE TRACING POR CASO DE TESTE")
    print("="*80)

    try:
        with open(ficheiro_caminhos, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{ficheiro_caminhos}' não foi encontrado.")
        return

    # Lista para guardar os dados e exportar para Excel/CSV no final
    dados_exportacao = []
    pastas_sem_csv = 0

    for linha in linhas:
        caminho = linha.strip()
        
        # Ignora linhas vazias ou palavras soltas (como nomes de projetos)
        if not caminho or not os.path.isabs(caminho):
            continue
            
        csv_path = os.path.join(caminho, "summary_execution.csv")
        
        # Extrai os últimos dois nomes da pasta para identificar o teste facilmente
        # Exemplo: Test-prefect / a46f6d0293a...
        partes = caminho.strip('/').split('/')
        if len(partes) >= 2:
            identificador_teste = f"{partes[-2]}/{partes[-1]}"
        else:
            identificador_teste = caminho

        # Verifica se o summary_execution.csv existe nesta pasta específica
        if not os.path.exists(csv_path):
            pastas_sem_csv += 1
            print(f"[-] IGNORADO: {identificador_teste} -> (CSV não encontrado)")
            continue
            
        # Zera os contadores para ESTE teste específico
        test_passed = 0
        test_failed = 0
        test_outros = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                leitor = csv.DictReader(csv_file)
                
                if leitor.fieldnames and 'Test Result' in leitor.fieldnames:
                    for linha_csv in leitor:
                        resultado = linha_csv['Test Result'].strip().lower()
                        
                        if resultado == 'passed':
                            test_passed += 1
                        elif resultado == 'failed':
                            test_failed += 1
                        else:
                            test_outros += 1
                else:
                    print(f"[!] AVISO: {identificador_teste} -> Coluna 'Test Result' não existe no ficheiro.")
                    continue
                    
            # Calcula o total de execuções deste teste
            total_runs = test_passed + test_failed + test_outros
            
            # Imprime o resultado individual no terminal
            print(f"[+] Teste: {identificador_teste} | Runs: {total_runs} | PASSED: {test_passed} | FAILED: {test_failed} | Outros: {test_outros}")
            
            # Guarda as informações para o relatório CSV final
            dados_exportacao.append({
                "Teste (Caminho)": identificador_teste,
                "Total Runs": total_runs,
                "Passed": test_passed,
                "Failed": test_failed,
                "Outros": test_outros
            })
            
        except Exception as e:
            print(f"[ERRO] Falha ao ler o ficheiro {csv_path}: {e}")

    # ==============================================================
    # GERA O FICHEIRO CSV DE RESUMO COM TODOS OS TESTES QUANTIFICADOS
    # ==============================================================
    nome_relatorio_saida = "resumo_por_teste_tracing.csv"
    if dados_exportacao:
        try:
            with open(nome_relatorio_saida, 'w', encoding='utf-8', newline='') as f_out:
                campos = ["Teste (Caminho)", "Total Runs", "Passed", "Failed", "Outros"]
                escritor = csv.DictWriter(f_out, fieldnames=campos)
                
                escritor.writeheader()
                escritor.writerows(dados_exportacao)
                
            print("="*80)
            print(f"SUCESSO! Foi gerado um ficheiro chamado '{nome_relatorio_saida}'.")
            print(f"Pode abri-lo no Excel para ver a tabela completa com a quantificação de cada teste.")
            print(f"Pastas ignoradas por não terem CSV: {pastas_sem_csv}")
            print("="*80)
        except Exception as e:
            print(f"Erro ao tentar guardar o relatório CSV final: {e}")

if __name__ == "__main__":
    analisar_resultados_por_teste("caminhos.txt")

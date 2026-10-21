import os
import pandas as pd

def verificar_falhas_profiling():
    arquivo_caminhos = 'caminhos.txt'
    
    # Verifica se o caminhos.txt existe
    if not os.path.exists(arquivo_caminhos):
        # Tenta o caminho absoluto caso não esteja na mesma pasta
        arquivo_caminhos = '/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o/FlapyRepos/caminhos.txt'
        if not os.path.exists(arquivo_caminhos):
            print("Erro: O arquivo caminhos.txt não foi encontrado.")
            return

    # Lê os caminhos ignorando linhas vazias ou nomes soltos (como 'xonsh')
    with open(arquivo_caminhos, 'r', encoding='utf-8') as f:
        caminhos_base = [linha.strip() for linha in f if '/' in linha]

    print(f"Iniciando a varredura em {len(caminhos_base)} pastas de teste...")
    print(f"Procurando por 'Failed' nos arquivos summary_profiling.csv...\n")
    
    todas_falhas = []
    testes_com_falha = 0

    for base_path in caminhos_base:
        if not os.path.exists(base_path):
            continue
            
        csv_path = os.path.join(base_path, 'summary_profiling.csv')
        
        # Se o summary existir, vamos investigar
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()
                
                # Verifica se a coluna de status existe
                if 'Test Result' in df.columns:
                    # Filtra as linhas onde o resultado é Failed (ignorando maiúsculas/minúsculas)
                    df_failed = df[df['Test Result'].astype(str).str.strip().str.lower() == 'failed']
                    
                    if not df_failed.empty:
                        testes_com_falha += 1
                        # Adiciona o caminho da pasta para você saber exatamente de onde veio
                        df_failed['Caminho_Origem'] = base_path
                        todas_falhas.append(df_failed)
                        
            except Exception as e:
                print(f"[Erro] Falha ao ler {csv_path}: {e}")

    # Se encontrou falhas, junta tudo num relatório final
    if todas_falhas:
        df_relatorio_final = pd.concat(todas_falhas, ignore_index=True)
        
        # Salva o relatório consolidado
        nome_relatorio = 'relatorio_runs_failed.csv'
        df_relatorio_final.to_csv(nome_relatorio, index=False, sep=',', decimal='.')
        
        print(f"{'='*60}")
        print(f" VARREDURA CONCLUÍDA: FALHAS ENCONTRADAS!")
        print(f"{'='*60}")
        print(f"- Casos de teste que apresentaram pelo menos 1 falha: {testes_com_falha}")
        print(f"- Total absoluto de Runs que falharam: {len(df_relatorio_final)}")
        print(f"\nUm relatório completo foi salvo em: {nome_relatorio}")
        print(f"Abra este arquivo para ver os detalhes (Nome do Projeto, Teste, Run exata e Tempo).")
        
    else:
        print(f"{'='*60}")
        print(f" VARREDURA CONCLUÍDA: NENHUMA FALHA ENCONTRADA.")
        print(f"{'='*60}")
        print("Ótima notícia! Nenhum arquivo summary_profiling.csv possui runs com o status 'Failed'.")

if __name__ == "__main__":
    verificar_falhas_profiling()

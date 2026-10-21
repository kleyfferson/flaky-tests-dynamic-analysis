import os
import glob
import pandas as pd

def analisar_variacao_flaky_tests_corrigido():
    flaky_csv_path = '/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o/flaky_profiling.csv'
    arquivo_caminhos = '/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o/FlapyRepos/caminhos.txt'
    output_csv = '/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o/flaky_tests_variation_analysis.csv'

    print("1. Lendo a classificação dos testes (flaky_profiling.csv)...")
    try:
        df_flaky = pd.read_csv(flaky_csv_path, skiprows=3)
        df_flaky.columns = ['Project Name', 'Test Name', 'Hash', '#Passed', '#Failed', 'Result']
        
        df_flaky = df_flaky.dropna(subset=['Test Name'])
        df_flaky_only = df_flaky[df_flaky['Result'] == 'Observed Flaky Test'].copy()
        
        # Cria um conjunto (set) de todos os nomes de testes Flaky para busca rápida
        testes_flaky_lista = set(df_flaky_only['Test Name'].astype(str).str.strip().unique())
        print(f"   -> Encontrados {len(testes_flaky_lista)} testes marcados como Flaky.")
    except Exception as e:
        print(f"Erro ao ler {flaky_csv_path}: {e}")
        return

    print("\n2. Coletando todas as métricas detalhadas (summary_top20_funcoes_por_run.csv)...")
    if not os.path.exists(arquivo_caminhos):
        print(f"Erro: {arquivo_caminhos} não encontrado.")
        return

    with open(arquivo_caminhos, 'r', encoding='utf-8') as f:
        caminhos_base = [linha.strip() for linha in f if '/' in linha]

    df_metricas_list = []
    
    for base_path in caminhos_base:
        if not os.path.exists(base_path):
            continue
        
        detalhado_csv = os.path.join(base_path, 'summary_top20_funcoes_por_run.csv')
        if os.path.exists(detalhado_csv):
            try:
                df_temp = pd.read_csv(detalhado_csv)
                df_metricas_list.append(df_temp)
            except:
                pass
                
    if not df_metricas_list:
        print("Nenhum arquivo de métricas detalhadas foi encontrado.")
        return
        
    df_all_metrics = pd.concat(df_metricas_list, ignore_index=True)
    print(f"   -> Carregadas {len(df_all_metrics)} linhas de profiling.")

    print("\n3. Fazendo o cruzamento inteligente dos nomes (Substring Match)...")
    
    # Função para encontrar o nome do flaky test dentro do caminho completo do profiling
    def encontrar_nome_flaky(profiling_name):
        profiling_name_clean = str(profiling_name).strip()
        for f_name in testes_flaky_lista:
            if f_name in profiling_name_clean:
                return f_name # Retorna o nome padronizado para agrupamento
        return None

    # Aplica a busca e guarda numa nova coluna
    df_all_metrics['Matched_Flaky_Name'] = df_all_metrics['Test name'].apply(encontrar_nome_flaky)
    
    # Filtra mantendo apenas as linhas onde houve um match positivo
    df_analise = df_all_metrics[df_all_metrics['Matched_Flaky_Name'].notna()].copy()
    
    print(f"   -> Restaram {len(df_analise)} registros mapeados APENAS aos Flaky Tests.")
    if len(df_analise) == 0:
        print("Erro: Nenhum teste cruzou. Verifique se os arquivos de métricas pertencem aos mesmos projetos.")
        return

    print("\n4. Calculando o Coeficiente de Variação (CV) entre as execuções (Runs)...")
    
    # Agora agrupamos usando o nome padronizado 'Matched_Flaky_Name'
    groupby_cols = ['Matched_Flaky_Name', 'Test Result', 'filename:lineno(function)']
    
    def calculate_cv(x):
        mean = x.mean()
        std = x.std(ddof=1) if len(x) > 1 else 0.0
        return (std / mean * 100) if mean > 0 else 0.0

    agregado = df_analise.groupby(groupby_cols).agg(
        Ocorrencias_no_Top20=('Run', 'count'),
        Media_ncalls=('ncalls', 'mean'),
        CV_ncalls_pct=('ncalls', calculate_cv),
        Media_tottime=('tottime', 'mean'),
        CV_tottime_pct=('tottime', calculate_cv),
        Media_cumtime=('cumtime', 'mean'),
        CV_cumtime_pct=('cumtime', calculate_cv)
    ).reset_index()

    # Arredondando e renomeando a coluna final para ficar elegante
    cols_to_round = ['Media_ncalls', 'CV_ncalls_pct', 'Media_tottime', 'CV_tottime_pct', 'Media_cumtime', 'CV_cumtime_pct']
    agregado[cols_to_round] = agregado[cols_to_round].round(2)
    agregado.rename(columns={'Matched_Flaky_Name': 'Test Name'}, inplace=True)

    agregado = agregado.sort_values(by=['Test Name', 'CV_tottime_pct'], ascending=[True, False])

    agregado.to_csv(output_csv, index=False)
    print(f"\n5. Análise concluída! Arquivo com dados reais salvo em:\n -> {output_csv}")

if __name__ == "__main__":
    analisar_variacao_flaky_tests_corrigido()

import os
import glob
import pandas as pd
import numpy as np

def calcular_somas_robusto(file_path):
    """
    Lê o arquivo de profiling linha por linha filtrando pela string de status.
    Ignora linhas corrompidas e calcula a soma de todas as métricas do cProfile.
    """
    somas = {'ncalls': 0.0, 'tottime': 0.0, 'percall': 0.0, 'cumtime': 0.0, 'percall_cum': 0.0}
    status_run = 'Unknown'
    project_name = 'Unknown'
    test_name = 'Unknown'
    run_name = 'Unknown'
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Descarta o cabeçalho
        f.readline()
        
        for line in f:
            line_lower = line.lower()
            status_atual = None
            split_term = None
            
            # Identifica se a linha é um registro de profiling válido
            if ',passed,' in line_lower:
                status_atual = 'Passed'
                split_term = ',Passed,' if ',Passed,' in line else ',passed,'
            elif ',failed,' in line_lower:
                status_atual = 'Failed'
                split_term = ',Failed,' if ',Failed,' in line else ',failed,'
                
            if status_atual:
                status_run = status_atual
                parts = line.split(split_term)
                
                # Lado esquerdo: Project Name, Test Name, Run
                esquerdo = parts[0].split(',')
                if len(esquerdo) >= 3:
                    # O split()[-1] limpa qualquer lixo de texto que sobrou da linha quebrada anterior
                    project_name = esquerdo[-3].strip().split()[-1] if esquerdo[-3].strip() else 'Unknown'
                    test_name = esquerdo[-2].strip()
                    run_name = esquerdo[-1].strip()
                
                # Lado direito: ncalls, tottime, percall, cumtime, percall_cum
                direito = parts[1].split(',')
                if len(direito) >= 5:
                    try:
                        # Trata ncalls que pode vir no formato "15/3"
                        ncalls_str = direito[0].strip().split('/')[0].replace(',', '.')
                        somas['ncalls'] += float(ncalls_str)
                        
                        somas['tottime'] += float(direito[1].strip().replace(',', '.'))
                        somas['percall'] += float(direito[2].strip().replace(',', '.'))
                        somas['cumtime'] += float(direito[3].strip().replace(',', '.'))
                        somas['percall_cum'] += float(direito[4].strip().replace(',', '.'))
                    except ValueError:
                        pass
                        
    return project_name, test_name, run_name, status_run, somas

def processar_profiling_local():
    # Caminho do caminhos.txt do seu ambiente
    arquivo_caminhos = '/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o/FlapyRepos/caminhos.txt'
    
    if not os.path.exists(arquivo_caminhos):
        arquivo_caminhos = 'caminhos.txt'
        if not os.path.exists(arquivo_caminhos):
            print("Erro: caminhos.txt não encontrado.")
            return

    with open(arquivo_caminhos, 'r', encoding='utf-8') as f:
        caminhos_base = [linha.strip() for linha in f if '/' in linha]

    print(f"Encontrados {len(caminhos_base)} casos de teste. Iniciando processamento robusto...\n")

    colunas_metricas = ['ncalls', 'tottime', 'percall', 'cumtime', 'percall_cum']

    for base_path in caminhos_base:
        if not os.path.exists(base_path):
            continue
            
        search_pattern = os.path.join(base_path, '**', '*-profiling.csv')
        arquivos_profiling = glob.glob(search_pattern, recursive=True)
        
        if not arquivos_profiling:
            continue
            
        resultados_locais = []
        
        for file_path in arquivos_profiling:
            try:
                # Executa o cálculo ultrarrobusto linha por linha
                project_name, test_name, run_name, test_result, somas = calcular_somas_robusto(file_path)
                
                # Fallback de segurança: se o arquivo estava limpo e não achou via texto, usa o Pandas clássico
                if test_result == 'Unknown' or somas['tottime'] == 0.0:
                    try:
                        df_temp = pd.read_csv(file_path)
                        df_temp.columns = df_temp.columns.str.strip()
                        if 'tottime' in df_temp.columns and not df_temp.empty:
                            project_name = df_temp['Project Name'].iloc[0] if 'Project Name' in df_temp.columns else project_name
                            test_name = df_temp['Test Name'].iloc[0] if 'Test Name' in df_temp.columns else test_name
                            run_name = df_temp['Run'].iloc[0] if 'Run' in df_temp.columns else run_name
                            test_result = df_temp['Test Result'].iloc[0] if 'Test Result' in df_temp.columns else test_result
                            
                            for col in colunas_metricas:
                                if col in df_temp.columns:
                                    # Limpa strings de fração e formata para converter corretamente
                                    df_temp[col] = df_temp[col].astype(str).apply(lambda x: x.split('/')[0] if '/' in x else x)
                                    df_temp[col] = df_temp[col].str.replace(',', '.', regex=False)
                                    df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce').fillna(0)
                                    somas[col] = float(df_temp[col].sum())
                    except:
                        pass
                
                # Armazena todas as somas
                resultado_linha = {
                    'Project Name': project_name,
                    'Test name': test_name,
                    'Run': run_name,
                    'Test Result': test_result
                }
                for col in colunas_metricas:
                    resultado_linha[f'sum_{col}'] = round(somas[col], 6)
                    
                resultados_locais.append(resultado_linha)
                
            except Exception as e:
                print(f"[Erro] Falha ao processar {file_path}: {e}")
        
        if resultados_locais:
            df_final = pd.DataFrame(resultados_locais)
            
            # Ordenação numérica inteligente das Runs (Run-1 a Run-100)
            def extract_run_num(r):
                try:
                    return int(str(r).lower().replace('run-', '').strip())
                except:
                    return 9999
            df_final['Run_Num'] = df_final['Run'].apply(extract_run_num)
            
            # Ordena separando por Test Result (Passed primeiro, dps Failed) e depois por número da Run
            df_final = df_final.sort_values(by=['Test Result', 'Run_Num']).drop(columns=['Run_Num'])
            
            # 1. Salva a listagem organizada por status na pasta do caso de teste
            output_file = os.path.join(base_path, 'summary_profiling.csv')
            df_final.to_csv(output_file, index=False, sep=',', decimal='.')
            print(f"Salvo detalhado por Status: {output_file} ({len(resultados_locais)} runs)")
            
            # 2. SEPARAÇÃO ESPECÍFICA SOLICITADA: Gera totais separados por Passed e Failed para TODAS AS MÉTRICAS
            df_passed = df_final[df_final['Test Result'].str.lower() == 'passed']
            df_failed = df_final[df_final['Test Result'].str.lower() == 'failed']
            
            summary_stats_file = os.path.join(base_path, 'summary_profiling_totals.csv')
            with open(summary_stats_file, 'w', encoding='utf-8') as sf:
                # Criando o cabeçalho estendido com CV
                header = ["Test Result", "Quantidade_Runs"]
                for col in colunas_metricas:
                    header.extend([f"Soma_{col}", f"Media_{col}", f"Desvio_Padrao_{col}", f"CV_{col}_pct"])
                sf.write(",".join(header) + "\n")
                
                # Função auxiliar para gravar as linhas (Passed / Failed) com cálculo de CV
                def escrever_metricas(df_subset, label):
                    linha = [label, str(len(df_subset))]
                    for col in colunas_metricas:
                        col_sum_name = f'sum_{col}'
                        total = df_subset[col_sum_name].sum() if not df_subset.empty else 0.0
                        avg = df_subset[col_sum_name].mean() if not df_subset.empty else 0.0
                        sd = df_subset[col_sum_name].std(ddof=1) if len(df_subset) > 1 else 0.0
                        
                        # Cálculo do Coeficiente de Variação (CV em %)
                        # Prevenção contra divisão por zero
                        cv = (sd / avg * 100) if avg > 0 else 0.0
                        
                        linha.extend([
                            str(round(total, 6)), 
                            str(round(avg, 6)), 
                            str(round(sd, 6)),
                            str(round(cv, 2))  # Adicionando o CV arredondado para 2 casas
                        ])
                    
                    sf.write(",".join(linha) + "\n")
                
                # Escreve as métricas
                escrever_metricas(df_passed, "Passed")
                escrever_metricas(df_failed, "Failed")
            
            print(f"Salvo totais agregados com CV: {summary_stats_file}")

    print("\nProcesso concluído! Arquivos gerados e somas das 5 métricas blindadas com sucesso.")

if __name__ == "__main__":
    processar_profiling_local()

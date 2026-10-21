import os

def limpar_arquivos_summary():
    # Caminho do seu caminhos.txt
    arquivo_caminhos = '/home/kleyfferson/Documentos/projetos_mestrado/projetos-TT-Jo-o/FlapyRepos/caminhos.txt'
    
    # Fallback caso execute na mesma pasta
    if not os.path.exists(arquivo_caminhos):
        arquivo_caminhos = 'caminhos.txt'
        if not os.path.exists(arquivo_caminhos):
            print("Erro: O arquivo caminhos.txt não foi encontrado.")
            return

    # Lê os caminhos válidos do txt
    with open(arquivo_caminhos, 'r', encoding='utf-8') as f:
        caminhos_base = [linha.strip() for linha in f if '/' in linha]

    print(f"Iniciando a varredura em {len(caminhos_base)} pastas para exclusão...")
    
    contador_deletados = 0
    
    for base_path in caminhos_base:
        if not os.path.exists(base_path):
            continue
            
        # Define o caminho exato do arquivo detalhado que você quer apagar
        arquivo_alvo = os.path.join(base_path, 'summary_profiling.csv')
        
        # Verifica se o arquivo realmente existe antes de tentar deletar
        if os.path.exists(arquivo_alvo):
            try:
                os.remove(arquivo_alvo)
                print(f"[Removido] {arquivo_alvo}")
                contador_deletados += 1
            except Exception as e:
                print(f"[Erro] Não foi possível deletar {arquivo_alvo}: {e}")

    print(f"\nLimpeza concluída com sucesso!")
    print(f"Total de arquivos 'summary_profiling.csv' excluídos: {contador_deletados}")

if __name__ == "__main__":
    limpar_arquivos_summary()

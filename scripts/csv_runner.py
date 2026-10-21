import subprocess
import csv
import argparse
import os
import concurrent.futures

# O Mapeamento Absoluto e Confiável (Todos os 61 projetos com seus caminhos originais exatos)
PROJECT_CONFIGS = {
    "airflow": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/airflow/", "venv": "venv-airflow"},
    "flexget": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/Flexget/", "venv": "venv-flexget"},
    "fonttools": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/fonttools/", "venv": "venv-fonttools"},
    "hypothesis": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/hypothesis/hypothesis-python/", "venv": "venv-hypothesis"},
    "ipython": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/ipython/", "venv": "venv-ipython"},
    "kombu": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/kombu/", "venv": "venv-kombu"},
    "libcloud": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/libcloud/", "venv": "venv-libcloud"},
    "loguru": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/loguru/", "venv": "venv-loguru"},
    "prefect": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/prefect/", "venv": "venv-prefect"},
    "requests": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/requests/", "venv": "venv-requests"},
    "seaborn": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/seaborn/", "venv": "venv-seaborn"},
    "setuptools": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/setuptools/", "venv": "venv-setuptools"},
    "urllib3": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/urllib3/", "venv": "venv-urllib3"},
    "xonsh": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/xonsh/", "venv": "venv-xonsh"},
    "amphipathic": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/amphipathic/", "venv": "venv-amphipathic"},
    "analytic_shrinkage": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/analytic_shrinkage/", "venv": "venv-analytic_shrinkage"},
    "cuckoopy": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/cuckoopy/", "venv": "venv-cuckoopy"},
    "darkchess": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/darkchess/", "venv": "venv-darkchess"},
    "data-partitioner": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/data_partitioner/", "venv": "venv-data_partitioner"},
    "dockerfile_bakery": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/dockerfile_bakery/", "venv": "venv-dockerfile_bakery"},
    "fistro": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/fistro/", "venv": "venv-fistro"},
    "forex-python": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/forex-python/", "venv": "venv-forex-python"},
    "supportdata": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/supportdata/", "venv": "venv-supportdata"},
    "fossor": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/fossor/", "venv": "venv-fossor"},
    "ftpsync": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/ftpsync/", "venv": "venv-ftpsync"},
    "gamble_git": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/gamble_git/", "venv": ".venv-gamble"},
    "hotwing-core": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/hotwing-core/", "venv": ".venv-hotwing"},
    "jinja2-github": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/jinja2-github/", "venv": ".venv-jinja2github"},
    "kb_python": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/kb_python/", "venv": ".venv-kbpython"},
    "keplertools": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/keplertools/", "venv": ".venv-keplertools"},
    "kevinarpe-rambutan3": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/kevinarpe-rambutan3/", "venv": ".venv-rambutan3"},
    "kindle-maker": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/kindle_maker/", "venv": ".venv-kindlemaker"},
    "langsplit": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/langsplit/", "venv": ".venv-langsplit"},
    "layouts-python": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/layouts-python/", "venv": ".venv-layoutspython"},
    "levitate": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/levitate/", "venv": ".venv-levitate"},
    "nnweaver": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/nnweaver/", "venv": ".venv-nnweaver"},
    "override": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/override/", "venv": ".venv-override"},
    "packeteer": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/packeteer/", "venv": ".venv-packeteer"},
    "piripherals": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/piripherals/", "venv": ".venv-piripherals"},
    "pybnn": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pybnn/", "venv": ".venv-pybnn"},
    "pycco": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pycco/", "venv": ".venv-pycco"},
    "pylabeledrf": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pylabeledrf/", "venv": ".venv-pylabeledrf"},
    "pymannkendall": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pymannkendall/", "venv": ".venv-pymannkendall"},
    "pymemorydb": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pymemorydb/", "venv": ".venv-pymemorydb"},
    "pypfm": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pypfm/", "venv": ".venv-pypfm"},
    "pyquery": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pyquery/", "venv": ".venv-pyquery"},
    "pyss3": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pyss3/", "venv": ".venv-pyss3"},
    "pysshutil": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/pysshutil/", "venv": ".venv-pysshutil"},
    "python-matlab-functions": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/python-matlab-functions/", "venv": ".venv-pymlfunc"},
    "python-timemarker": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/python-timemarker/", "venv": ".venv-timemarker"},
    "r_map": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/r_map/", "venv": ".venv-rmap"},
    "rs3clans_py": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/rs3clans_py/", "venv": ".venv-rs3clans"},
    "service-manager": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/service-manager/", "venv": ".venv-servicemanager"},
    "setigen": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/setigen/", "venv": ".venv-setigen"},
    "spreading_dye_sampler": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/spreading_dye_sampler/", "venv": ".venv-spreadingdye"},
    "textdistance": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/textdistance/", "venv": ".venv-textdistance"},
    "torch-embed-sim": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/torch-embed-sim/", "venv": ".venv-torchembed"},
    "torch-layer-normalization": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/torch-layer-normalization/", "venv": ".venv-torchnorm"},
    "uhashring": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/uhashring/", "venv": ".venv-uhashring"},
    "verifone": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/Verifone/", "venv": ".venv-verifone"},
    "wiki-futures": {"path": "/home/kleyfferson/Documentos/projetos_mestrado/wiki-futures/", "venv": ".venv-wikifutures"}
}

def processa_linha(row, analise):
    repo_name_raw = row['repo_name']
    repo_name = repo_name_raw.lower()
    test_path = row['test_path']
    test_hash = row['test_hash']
    no_runs = row['no_runs']
    
    if repo_name not in PROJECT_CONFIGS:
        return f"[AVISO] Projeto {repo_name_raw} nao esta mapeado no PROJECT_CONFIGS."
    
    config = PROJECT_CONFIGS[repo_name]
    repo_path = config["path"]
    venv_name = config["venv"]
    
    venv_path = os.path.join(repo_path, venv_name)
    
    # Comandos originais preservados perfeitamente (--repo-name, --test-path, etc.)
    cmd = [
        "python3", "main.py",
        "--repo-name", repo_name,
        "--test-path", test_path,
        "--test-hash", test_hash,
        "--no-runs", str(no_runs),
        "--venv-path", venv_path,
        "--include-test-profiling", "True" if analise == "profiling" else "False",
        "--include-test-coverage", "True" if analise == "coverage" else "False",
        "--include-test-tracing", "True" if analise == "tracing" else "False",
        "--workers", "1"
    ]
    
    # Execução livre, sem travas de tempo (timeout de 20 min foi removido)
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return f"[AVISO] Falha na execucao do teste {test_hash} no projeto {repo_name}.\nErro: {result.stderr}"
    
    return f"[SUCESSO] {repo_name} | {test_hash} finalizado com {no_runs} runs."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--analise", choices=["profiling", "coverage", "tracing", "none"], required=True)
    parser.add_argument("--workers", type=int, default=1, help="Numero de workers para processamento em paralelo")
    args = parser.parse_args()

    csv_path = "FlapyRepos/flaky.csv"

    if not os.path.exists(csv_path):
        print(f"ERRO: Arquivo {csv_path} nao encontrado!")
        exit(1)

    tarefas = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            
            cabecalho = row[0].strip().lower()
            if cabecalho in ["repo_name", "project name", "name"]:
                continue
            
            num_runs = row[2].strip() if len(row) > 2 else "100"

            tarefas.append({
                'repo_name': row[0].strip(),
                'test_path': row[1].strip(),
                'no_runs': num_runs,
                'test_hash': row[-1].strip()
            })

    print(f"Iniciando processamento com {args.workers} workers...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futuros = {executor.submit(processa_linha, row, args.analise): row for row in tarefas}
        
        for futuro in concurrent.futures.as_completed(futuros):
            try:
                resultado = futuro.result()
                print(resultado)
            except Exception as exc:
                row = futuros[futuro]
                projeto = row.get('repo_name', 'Desconhecido')
                hash_teste = row.get('test_hash', 'Desconhecido')
                print(f"Exceção gerada no teste {hash_teste} do projeto {projeto}: {exc}")

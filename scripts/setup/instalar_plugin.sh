#!/bin/bash

# Lista de todos os caminhos dos ambientes virtuais
ambientes=(
    "/home/kleyfferson/Documentos/projetos_mestrado/airflow/venv-airflow"
    "/home/kleyfferson/Documentos/projetos_mestrado/Flexget/venv-flexget"
    "/home/kleyfferson/Documentos/projetos_mestrado/fonttools/venv-fonttools"
    "/home/kleyfferson/Documentos/projetos_mestrado/hypothesis/hypothesis-python/venv-hypothesis"
    "/home/kleyfferson/Documentos/projetos_mestrado/ipython/venv-ipython"
    "/home/kleyfferson/Documentos/projetos_mestrado/kombu/venv-kombu"
    "/home/kleyfferson/Documentos/projetos_mestrado/libcloud/venv-libcloud"
    "/home/kleyfferson/Documentos/projetos_mestrado/loguru/venv-loguru"
    "/home/kleyfferson/Documentos/projetos_mestrado/prefect/venv-prefect"
    "/home/kleyfferson/Documentos/projetos_mestrado/requests/venv-requests"
    "/home/kleyfferson/Documentos/projetos_mestrado/seaborn/venv-seaborn"
    "/home/kleyfferson/Documentos/projetos_mestrado/setuptools/venv-setuptools"
    "/home/kleyfferson/Documentos/projetos_mestrado/urllib3/venv-urllib3"
    "/home/kleyfferson/Documentos/projetos_mestrado/xonsh/venv-xonsh"
    "/home/kleyfferson/Documentos/projetos_mestrado/amphipathic/venv-amphipathic"
    "/home/kleyfferson/Documentos/projetos_mestrado/analytic_shrinkage/venv-analytic_shrinkage"
    "/home/kleyfferson/Documentos/projetos_mestrado/cuckoopy/venv-cuckoopy"
    "/home/kleyfferson/Documentos/projetos_mestrado/darkchess/venv-darkchess"
    "/home/kleyfferson/Documentos/projetos_mestrado/data_partitioner/venv-data_partitioner"
    "/home/kleyfferson/Documentos/projetos_mestrado/dockerfile_bakery/venv-dockerfile_bakery"
    "/home/kleyfferson/Documentos/projetos_mestrado/fistro/venv-fistro"
    "/home/kleyfferson/Documentos/projetos_mestrado/forex-python/venv-forex-python"
    "/home/kleyfferson/Documentos/projetos_mestrado/supportdata/venv-supportdata"
    "/home/kleyfferson/Documentos/projetos_mestrado/fossor/venv-fossor"
    "/home/kleyfferson/Documentos/projetos_mestrado/ftpsync/venv-ftpsync"
    "/home/kleyfferson/Documentos/projetos_mestrado/gamble_git/.venv-gamble"
    "/home/kleyfferson/Documentos/projetos_mestrado/hotwing-core/.venv-hotwing"
    "/home/kleyfferson/Documentos/projetos_mestrado/jinja2-github/.venv-jinja2github"
    "/home/kleyfferson/Documentos/projetos_mestrado/kb_python/.venv-kbpython"
    "/home/kleyfferson/Documentos/projetos_mestrado/keplertools/.venv-keplertools"
    "/home/kleyfferson/Documentos/projetos_mestrado/kevinarpe-rambutan3/.venv-rambutan3"
    "/home/kleyfferson/Documentos/projetos_mestrado/kindle_maker/.venv-kindlemaker"
    "/home/kleyfferson/Documentos/projetos_mestrado/langsplit/.venv-langsplit"
    "/home/kleyfferson/Documentos/projetos_mestrado/layouts-python/.venv-layoutspython"
    "/home/kleyfferson/Documentos/projetos_mestrado/levitate/.venv-levitate"
    "/home/kleyfferson/Documentos/projetos_mestrado/nnweaver/.venv-nnweaver"
    "/home/kleyfferson/Documentos/projetos_mestrado/override/.venv-override"
    "/home/kleyfferson/Documentos/projetos_mestrado/packeteer/.venv-packeteer"
    "/home/kleyfferson/Documentos/projetos_mestrado/piripherals/.venv-piripherals"
    "/home/kleyfferson/Documentos/projetos_mestrado/pybnn/.venv-pybnn"
    "/home/kleyfferson/Documentos/projetos_mestrado/pycco/.venv-pycco"
    "/home/kleyfferson/Documentos/projetos_mestrado/pylabeledrf/.venv-pylabeledrf"
    "/home/kleyfferson/Documentos/projetos_mestrado/pymannkendall/.venv-pymannkendall"
    "/home/kleyfferson/Documentos/projetos_mestrado/pymemorydb/.venv-pymemorydb"
    "/home/kleyfferson/Documentos/projetos_mestrado/pypfm/.venv-pypfm"
    "/home/kleyfferson/Documentos/projetos_mestrado/pyquery/.venv-pyquery"
    "/home/kleyfferson/Documentos/projetos_mestrado/pyss3/.venv-pyss3"
    "/home/kleyfferson/Documentos/projetos_mestrado/pysshutil/.venv-pysshutil"
    "/home/kleyfferson/Documentos/projetos_mestrado/python-matlab-functions/.venv-pymlfunc"
    "/home/kleyfferson/Documentos/projetos_mestrado/python-timemarker/.venv-timemarker"
    "/home/kleyfferson/Documentos/projetos_mestrado/r_map/.venv-rmap"
    "/home/kleyfferson/Documentos/projetos_mestrado/rs3clans_py/.venv-rs3clans"
    "/home/kleyfferson/Documentos/projetos_mestrado/service-manager/.venv-servicemanager"
    "/home/kleyfferson/Documentos/projetos_mestrado/setigen/.venv-setigen"
    "/home/kleyfferson/Documentos/projetos_mestrado/spreading_dye_sampler/.venv-spreadingdye"
    "/home/kleyfferson/Documentos/projetos_mestrado/textdistance/.venv-textdistance"
    "/home/kleyfferson/Documentos/projetos_mestrado/torch-embed-sim/.venv-torchembed"
    "/home/kleyfferson/Documentos/projetos_mestrado/torch-layer-normalization/.venv-torchnorm"
    "/home/kleyfferson/Documentos/projetos_mestrado/uhashring/.venv-uhashring"
    "/home/kleyfferson/Documentos/projetos_mestrado/Verifone/.venv-verifone"
    "/home/kleyfferson/Documentos/projetos_mestrado/wiki-futures/.venv-wikifutures"
)

echo "Iniciando a instalação do pytest-json-report em todos os 61 ambientes..."

for venv in "${ambientes[@]}"; do
    # Remove qualquer barra extra no final do caminho
    venv=$(echo "$venv" | sed 's:/*$::')
    
    pip_exec="$venv/bin/pip"
    
    if [ -f "$pip_exec" ] || [ -L "$pip_exec" ]; then
        echo -e "\n Instalando no projeto: $(basename $(dirname $venv))"
        "$pip_exec" install pytest-json-report -q  # -q deixa a saída mais limpa
    else
        echo -e "\n  ERRO: O executável do pip não foi encontrado em $pip_exec"
    fi
done

echo -e "\n Instalação concluída em todos os projetos!"

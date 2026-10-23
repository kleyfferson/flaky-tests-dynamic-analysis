# A Dynamic Behavior Perspective on Flaky Tests

**Replication artifact** for the paper *"A Dynamic Behavior Perspective on Flaky Tests"*.

[![Data on Zenodo](https://img.shields.io/badge/data-Zenodo-blue)](https://zenodo.org/records/23484158)

This repository contains the code, data pointers, and replication protocol of an empirical study that analyzes **247 flaky tests** from **61 open-source Python projects** through their dynamic behavior.

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start](#2-quick-start)
3. [Repository Structure](#3-repository-structure)
4. [Data Availability](#4-data-availability)
5. [System Requirements](#5-system-requirements)
6. [Replication Protocol](#6-replication-protocol)
7. [Subject Projects](#7-subject-projects)
8. [Troubleshooting](#8-troubleshooting)
9. [Citation](#9-citation)

---

## 1. Overview

The study examines flaky tests from three dynamic-analysis perspectives, plus a baseline:

| Perspective | `--analise` flag | Executions per test | Parallelism |
|---|---|---|---|
| Code coverage | `coverage` | 100 | none (16 cores reserved) |
| Profiling | `profiling` | 100 | none (16 cores reserved) |
| Function-level tracing | `tracing` | 100 | none (16 cores reserved) |
| Baseline (no dynamic analysis) | `none` | 100 | none (16 cores reserved) |

The baseline records, for each of the 247 flaky tests, how many runs passed and how many failed.

## 2. Quick Start

Choose the path that fits your goal:

| Goal | What to do |
|---|---|
| **Reproduce the statistics and figures** from the published data | Download the data ([Section 4](#4-data-availability)), then go directly to [Step 3](#step-3-data-analysis). Steps 1 and 2 are **not** needed. |
| **Re-collect the data from scratch** | Follow Steps 0 to 3 in order ([Section 6](#6-replication-protocol)). This is long-running. |

## 3. Repository Structure

```text
flaky-tests-dynamic-analysis/
├── README.md
├── analysis/                  # Statistics and figures (Step 3)
│   ├── *.py                   # Analysis scripts
│   ├── *.csv / *.xlsx         # Derived intermediate tables
│   └── pictures/              # Figures used in the paper
├── data/
│   ├── download_data.md       # How to download the raw data from Zenodo
│   └── projects_list.csv      # The 61 projects (repository link, commit hash, test path, test command, venv path, results path)
├── docs/
│   ├── environment.md         # Hardware and software specifications
│   └── Organização_projeto_NOD.docx   # Working document: test/venv/results paths, test commands, 247 test names ↔ hashes
├── paper/
│   └── dynamic_analysis_in_flaky_tests.pdf
└── scripts/                   # Data-collection harness (Step 2)
    ├── csv_runner.py          # Main harness: runs each flaky test N times per analysis
    ├── main.py, conftest.py
    ├── parse_coverage.py, parse_profiling.py, parse_tracing.py
    ├── converter_tracing.py, hierarchical_tracer.py
    ├── diff_finder.py
    ├── Analise/               # Analysis engine (tracing plugin, venv handling, results)
    ├── FlapyRepos/            # Flaky-test list (flaky.csv) and repo utilities
    └── setup/
        └── instalar_plugin.sh # Installs pytest-json-report in every project venv
```

<details>
<summary>Full list of files in <code>analysis/</code></summary>

| File | Purpose |
|---|---|
| `cv_violin.py` | Coefficient-of-variation profiling violin plot → `pictures/cv_violin_reordered_v2.1.png` |
| `histograma.py` | Coverage-specific histograms (avg/sd) → `pictures/*.png` |
| `histograma_tracing.py` | Tracing-specific histograms (avg/sd) → `pictures/histograms_tracing_*.png` |
| `imagem.py` | Figure composition helper (e.g., `pictures/grafico_artigo.png`) |
| `gerador_estatisticas_final_coverage.py` | Coverage statistics (avg, sd, CV) → `Estatisticas_Cobertura_Final.xlsx` |
| `gerador_profiling.py` | Profiling aggregation → `Profiling_preenchido.xlsx` |
| `filtro_profiling.py` | Profiling filtering/cleanup (input for `gerador_profiling.py`) |
| `relatorio_tracing.py` | Tracing report |
| `limpar_summaries.py` | Cleans intermediate summary files |

Tracked intermediate tables: `boxplot.csv`, `boxplot_tracing.csv`, `reproducedTests_Classificado_Profissional_100.xlsx`, `resultado_testes_por_projeto.csv`, `Estatisticas_Cobertura_Final.xlsx`, `Profiling_preenchido.xlsx`. They can be regenerated from the raw data with the scripts above.

</details>

> `data/results/` is **not** committed. You create it when downloading the Zenodo dataset or when re-collecting the data.

## 4. Data Availability

The raw data is publicly available on Zenodo: <https://zenodo.org/records/23484158>

It contains **100 executions** of each dynamic analysis (`coverage`, `profiling`, `tracing`) for all 247 flaky tests, i.e., **300 executions per test** in total.

Download it and place it in `data/results/` (create the directory). See [`data/download_data.md`](data/download_data.md) for detailed instructions.

## 5. System Requirements

The experiments ran on the machine below. Other Linux machines work, but absolute timings will differ.

| Component | Specification |
|---|---|
| CPU | Intel Core i9-14900KF (3.2 GHz base clock) |
| RAM | 64 GB DDR5 (5600 MHz) |
| Storage | 1 TB NVMe SSD |
| OS | Linux Mint 22.1 (Ubuntu 24.04 based), kernel 6.8.0-110-generic, x86-64 |
| Python | 3.12 |

Notes:

- **Linux is required** (setup scripts are Bash and paths use `/`).
- Full re-collection is long-running (3 analyses × 247 tests × 100 executions, plus the baseline). Use `tmux`, `screen`, or `nohup`.
- Reserve ample disk space for the 61 cloned projects, their 61 virtual environments, and the raw results. Some projects (e.g., Airflow, Prefect) have large dependency trees.

## 6. Replication Protocol

Everything needed to set up each project (repository link, pinned commit, test path, test command, venv location, and results folder) is in [`data/projects_list.csv`](data/projects_list.csv). The original working document, [`docs/Organização_projeto_NOD.docx`](docs/Organização_projeto_NOD.docx), holds the paths and commands plus the list of the 247 flaky tests.

### Step 0: Sanity check (optional, recommended)

Verify the toolchain on one small project (`loguru`) after completing Step 1 for it:

```bash
cd "$PROJECTS_ROOT/loguru"
source .venv-loguru/bin/activate      # exact path: see data/projects_list.csv
python -m pytest --json-report --json-report-file=/tmp/loguru_report.json -q
deactivate
```

If `/tmp/loguru_report.json` is written, the environment works.

### Step 1: Environment setup

#### 1.1 Install system packages

On Ubuntu/Debian-based systems:

```bash
sudo apt update
sudo apt install -y git build-essential python3.12 python3.12-venv python3.12-dev python3-pip
python3.12 --version    # expected: Python 3.12.x
```

Some projects compile native extensions or need extra system libraries. If an install fails, check that project's own documentation.

#### 1.2 Clone this repository

```bash
git clone https://github.com/kleyfferson/flaky-tests-dynamic-analysis.git
cd flaky-tests-dynamic-analysis
```

#### 1.3 Choose a projects directory

All 61 subject projects are cloned into one directory. The paths in `data/projects_list.csv` are the **absolute paths of the original machine** (`/home/kleyfferson/Documentos/projetos_mestrado/...`); on your machine, the same layout lives under `$PROJECTS_ROOT`.

```bash
export PROJECTS_ROOT="$HOME/flaky_projects"
mkdir -p "$PROJECTS_ROOT"
```

> **Important:** the original experiments used `/home/kleyfferson/Documentos/projetos_mestrado/`. If any script in `scripts/` has a hard-coded base path, replace it with your `$PROJECTS_ROOT` (search for `projetos_mestrado`).

#### 1.4 Clone the 61 subject projects

Each row of `data/projects_list.csv` gives the upstream repository (`repository_link`) and the exact commit used in the study (`commit_hash`). Each project is cloned into `$PROJECTS_ROOT/<folder>`, where `<folder>` is the first directory after `projetos_mestrado/` in `test_path` (e.g., `.../Flexget/flexget/tests/` → `Flexget`; `kindle-maker` → `kindle_maker`).

> **The folder comes from `test_path`, not from the repository name.** For example, `gamble_git` is cloned from `jpetrucciani/gamble`, and `rs3clans_py` from `johnvictorfs/rs3clans.py`.

Run this from the repository root to clone and pin all 61 projects:

```bash
python3 - <<'EOF'
import csv, os, subprocess

root = os.environ["PROJECTS_ROOT"]
prefix = "/home/kleyfferson/Documentos/projetos_mestrado/"

with open("data/projects_list.csv") as f:
    for row in csv.DictReader(f):
        folder = row["test_path"].removeprefix(prefix).split("/")[0]
        dest = os.path.join(root, folder)
        if not os.path.isdir(dest):
            subprocess.run(["git", "clone", row["repository_link"], dest], check=True)
        subprocess.run(["git", "-C", dest, "checkout", row["commit_hash"]], check=True)
EOF
```

The checkout leaves each project in a detached-HEAD state at the study's commit, which is expected.

#### 1.5 Create one virtual environment per project

Each project has its own venv at the `venv_path` given in `data/projects_list.csv` (e.g., `$PROJECTS_ROOT/airflow/venv-airflow/`, `$PROJECTS_ROOT/loguru/venv-loguru/`, `$PROJECTS_ROOT/gamble_git/.venv-gamble/`).

```bash
cd "$PROJECTS_ROOT/loguru"
python3.12 -m venv .venv-loguru
source .venv-loguru/bin/activate
pip install --upgrade pip
pip install -e .          # install the project and its test dependencies (varies per project)
pip install pytest
deactivate
```

Repeat for all 61 projects, following each project's own documentation (`requirements*.txt`, `pyproject.toml`, `setup.py`, `tox.ini`, or `CONTRIBUTING`). Keep venv names and locations **exactly** as in `data/projects_list.csv`.

Run each project's test command exactly as listed in the `test_command` column. Special cases:

| Project | Detail |
|---|---|
| `override` | Uses the venv interpreter directly: `./.venv-override/bin/python -m pytest` |
| `darkchess` | Runs the installed package: `pytest --pyargs darkchess` |
| `python-matlab-functions` | Uses `nosetests --nocapture -v` |
| `torch-embed-sim`, `torch-layer-normalization` | Use `python -m nose` |
| `Verifone` | Uses `python -m unittest discover` |
| `hypothesis` | Venv lives in `hypothesis/hypothesis-python/`; command is `python -m pytest hypothesis-python` |

#### 1.6 Install `pytest-json-report` in every venv

The harness collects per-run results through this plugin.

```bash
cd scripts/setup
chmod +x instalar_plugin.sh
./instalar_plugin.sh
```

Verify a given venv:

```bash
"$PROJECTS_ROOT/loguru/.venv-loguru/bin/pip" show pytest-json-report
```

<!-- TODO: if instalar_plugin.sh uses a hard-coded base path, document how to point it to $PROJECTS_ROOT. -->

#### 1.7 Check that every project's tests run

```bash
cd "$PROJECTS_ROOT/<folder>"
source <venv_path>/bin/activate
python -m pytest --collect-only -q | tail -n 3
deactivate
```

### Step 2: Data collection

Run one command at a time from `scripts/`, using Python 3.12. Output is redirected to one log file per run:

```bash
cd scripts

python3 csv_runner.py --analise coverage  > output_coverage.txt  2>&1
python3 csv_runner.py --analise profiling > output_profiling.txt 2>&1
python3 csv_runner.py --analise tracing   > output_tracing.txt   2>&1
python3 csv_runner.py --analise none      > output_puro.txt      2>&1
```

| Flag | Meaning |
|---|---|
| `--analise {coverage,profiling,tracing,none}` | Dynamic analysis applied during test runs (`none` = baseline, no analysis) |

Recommendations:

- Run the configurations **sequentially, never concurrently**; concurrent runs compete for CPU and distort execution-time measurements.
- Avoid other heavy workloads on the machine during collection.
- For long runs, use `nohup` or `tmux`:

  ```bash
  nohup python3 csv_runner.py --analise coverage > output_coverage.txt 2>&1 &
  tail -f output_coverage.txt
  ```

Per-project results are written to one folder per project (e.g., `Test-airflow/`, `Test-loguru/`; exact names in the `results_path` column of `data/projects_list.csv`). Move or copy them under `data/results/` before running the analysis scripts.

### Step 3: Data analysis

The scripts in `analysis/` compute the statistics (average, standard deviation, coefficient of variation) and generate the paper's figures (boxplots, histograms, bar charts, violin plots).

```bash
# from the repository root
python3.12 -m venv .venv-analysis
source .venv-analysis/bin/activate
pip install pandas numpy matplotlib seaborn scipy openpyxl
cd analysis
python3 <script>.py
```

See the file list in [Section 3](#3-repository-structure) for what each script does.

## 7. Subject Projects

`data/projects_list.csv` has one row per project (61 rows) with these columns:

| Column | Content |
|---|---|
| `project_name` | Project name |
| `test_path` | Directory with the project's tests |
| `venv_path` | Project's virtual environment |
| `test_command` | Command used to run the tests |
| `results_path` | Folder where the harness wrote the results |
| `repository_link` | Upstream GitHub repository |
| `commit_hash` | Exact commit used in the study |

All paths are **absolute paths from the original machine**, under `/home/kleyfferson/Documentos/projetos_mestrado/`. In that setup, the harness repository (`projetos-TT-Jo-o/`) lived inside the same directory and wrote results to `projetos-TT-Jo-o/Test-<project>/`. To use the file on another machine, replace that prefix with your `$PROJECTS_ROOT`, e.g.:

```bash
sed "s#/home/kleyfferson/Documentos/projetos_mestrado#$PROJECTS_ROOT#g" data/projects_list.csv > projects_list.local.csv
```

The 247 flaky tests are those covered by the raw data ([Section 4](#4-data-availability)). They are listed in the last table of `docs/Organização_projeto_NOD.docx` (test name ↔ hash), and the list can also be reconstructed from `scripts/FlapyRepos/flaky.csv` together with the pass/fail information in the Zenodo dataset. The same document is the original working document from which `projects_list.csv` was derived: it holds each project's test path, test command, venv path, and results path (the repository links and commit hashes were added later, in the CSV only).

<details>
<summary>The 61 projects</summary>

airflow, Flexget, fonttools, hypothesis, ipython, kombu, libcloud, loguru, prefect, requests, seaborn, setuptools, urllib3, xonsh, amphipathic, analytic_shrinkage, cuckoopy, darkchess, data-partitioner, dockerfile_bakery, fistro, forex-python, supportdata, fossor, ftpsync, gamble_git, hotwing-core, jinja2-github, kb_python, keplertools, kevinarpe-rambutan3, kindle-maker, langsplit, layouts-python, levitate, nnweaver, override, packeteer, piripherals, pybnn, pycco, pylabeledrf, pymannkendall, pymemorydb, pypfm, pyquery, pyss3, pysshutil, python-matlab-functions, python-timemarker, r_map, rs3clans_py, service-manager, setigen, spreading_dye_sampler, textdistance, torch-embed-sim, torch-layer-normalization, uhashring, Verifone, wiki-futures

</details>

## 8. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `python3.12: command not found` | Install Python 3.12 (see 1.1). |
| `No module named venv` | `sudo apt install python3.12-venv`. |
| `pip install` fails building a wheel | Install system headers (`build-essential`, `python3.12-dev`, plus any library named in the error); see that project's own documentation. |
| `No such file or directory` for a project path | `PROJECTS_ROOT` is not set in the current shell, the folder name differs from `test_path` in `data/projects_list.csv`, or the CSV paths still point to the original `/home/kleyfferson/...` prefix. |
| Harness cannot find the project/venv | Hard-coded base path in the scripts; update it to your `$PROJECTS_ROOT`. |
| `unrecognized arguments: --json-report` | `pytest-json-report` is missing in that venv (rerun 1.6). |
| `ModuleNotFoundError` although the package is installed in the venv | The shell leaked to the global interpreter; use `python -m pytest` and re-activate the venv. |
| Pass/fail results differ from the paper | Legacy projects may need old dependency versions; follow each project's own requirements files and documentation. |
| A test hits a live API and fails with 403/429/timeouts | Some tests depend on live external services; failures from rate limits or timeouts may reflect the environment, so check network access. |
| Execution times differ from the paper | Expected on different hardware; compare relative overheads between analyses, not absolute times. |
| A test does not behave as flaky | Flakiness is non-deterministic; it shows up across repeated executions, not necessarily in a single run. |

## 9. Citation

<!-- TODO: fill in authors, venue, year, and DOI once available. -->

```bibtex
@inproceedings{TODO_key,
  title  = {A Dynamic Behavior Perspective on Flaky Tests},
  author = {TODO},
  year   = {TODO},
  note   = {Artifact: https://github.com/kleyfferson/flaky-tests-dynamic-analysis, data: https://zenodo.org/records/23484158}
}
```

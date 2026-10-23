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
7. [Per-Project Test Execution Guide](#7-per-project-test-execution-guide)
8. [Subject Projects](#8-subject-projects)
9. [Troubleshooting](#9-troubleshooting)
10. [Citation](#10-citation)

---

## 1. Overview

The study examines flaky tests from three dynamic-analysis perspectives, plus a baseline:

| Perspective | `--analise` flag | Executions per test | Parallelism |
|---|---|---|---|
| Code coverage | `coverage` | 300 | 16 workers |
| Profiling | `profiling` | 300 | 16 workers |
| Function-level tracing | `tracing` | 300 | 16 workers |
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
│   └── projects_list.csv      # The 61 projects (test path, test command, venv path, results path)
├── docs/
│   ├── environment.md         # Hardware and software specifications
│   └── Organização_projeto_NOD.docx   # Per-project execution guide
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
| `cv_violin.py` | Coefficient-of-variation violin plot → `pictures/cv_violin_reordered_v2.1.png` |
| `histograma.py` | Passed/failed histograms (general) → `pictures/*.png` |
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

It contains:

- **300 executions** of each dynamic analysis (`coverage`, `profiling`, `tracing`) for all 247 flaky tests.
- **100 executions** of the baseline (`none`): pass/fail counts per test, without dynamic analysis and without parallelism.

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
- Full re-collection is long-running (3 analyses × 247 tests × 300 executions, plus the baseline). Use `tmux`, `screen`, or `nohup`.
- Reserve ample disk space for the 61 cloned projects, their 61 virtual environments, and the raw results. Some projects (e.g., Airflow, Prefect) have large dependency trees.

Full details: [`docs/environment.md`](docs/environment.md).

## 6. Replication Protocol

Per-project setup details (commits, Python versions, pinned dependencies, workarounds) are in [Section 7](#7-per-project-test-execution-guide).

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

Some projects compile native extensions or need extra system libraries. If an install fails, check the per-project notes in Section 7.

#### 1.2 Clone this repository

```bash
git clone https://github.com/kleyfferson/flaky-tests-dynamic-analysis.git
cd flaky-tests-dynamic-analysis
```

#### 1.3 Choose a projects directory

All 61 subject projects are cloned into one directory. Paths in `data/projects_list.csv` are relative to it.

```bash
export PROJECTS_ROOT="$HOME/flaky_projects"
mkdir -p "$PROJECTS_ROOT"
```

> **Important:** the original experiments used `/home/kleyfferson/Documentos/projetos_mestrado/`. If any script in `scripts/` has a hard-coded base path, replace it with your `$PROJECTS_ROOT` (search for `projetos_mestrado`).

#### 1.4 Clone the 61 subject projects

Each row of `data/projects_list.csv` identifies a project whose upstream repository must be cloned into `$PROJECTS_ROOT/<folder>`, where `<folder>` is the first component of `test_path` (e.g., `Flexget/flexget/tests/` → `Flexget`; `kindle-maker` → `kindle_maker`).

```bash
cd "$PROJECTS_ROOT"
git clone <upstream-url> <folder>
cd <folder>
git checkout <commit>       # pin to the version used in the study
```

Upstream URLs and exact commit hashes per project are listed in the [per-project guide](#7-per-project-test-execution-guide).

<!-- TODO: add `repo_url` and `commit` columns to data/projects_list.csv so this step can be fully scripted. -->

#### 1.5 Create one virtual environment per project

Each project has its own venv at the `venv_path` given in `data/projects_list.csv` (e.g., `airflow/venv-airflow/`, `loguru/venv-loguru/`, `gamble_git/.venv-gamble/`).

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

Run all commands from `scripts/` with Python 3.12. Output is redirected to one log file per run:

```bash
cd scripts

python3 csv_runner.py --analise coverage  --workers 16 > output_coverage_i9.txt  2>&1
python3 csv_runner.py --analise profiling --workers 16 > output_profiling_i9.txt 2>&1
python3 csv_runner.py --analise tracing   --workers 16 > output_tracing_i9.txt   2>&1
python3 csv_runner.py --analise none                   > output_puro_i9.txt      2>&1
```

| Flag | Meaning |
|---|---|
| `--analise {coverage,profiling,tracing,none}` | Dynamic analysis applied during test runs (`none` = baseline, no analysis, no parallelism) |
| `--workers N` | Number of parallel workers (16 in the experiments; dynamic analyses only) |

Recommendations:

- Run the configurations **sequentially, never concurrently**; concurrent runs compete for CPU and distort execution-time measurements.
- Avoid other heavy workloads during collection and keep the same `--workers` value across the three dynamic-analysis runs.
- For long runs, use `nohup` or `tmux`:

  ```bash
  nohup python3 csv_runner.py --analise coverage --workers 16 > output_coverage_i9.txt 2>&1 &
  tail -f output_coverage_i9.txt
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

## 7. Per-Project Test Execution Guide

[`docs/Organização_projeto_NOD.docx`](docs/Organização_projeto_NOD.docx) (the *"Guia de Execução de Testes Locais"*) consolidates the setup notes gathered while reproducing each of the 61 projects. It is the practical complement to Step 1, especially when a project's own instructions are outdated (common in legacy code).

For each project it documents:

- **Repository and commit:** upstream URL and the exact commit hash used.
- **Python version:** the one that worked (often 3.8 for legacy projects, 3.10+ for newer ones).
- **Commands:** venv creation and exact test invocation (`python -m pytest`, `nosetests`, `python -m nose`, `python -m unittest discover`).
- **Dependency pinning** for projects that break on modern versions (e.g., `Cython<3.0`, `numpy==1.21.6`, `pytest==5.4.3`, `prompt-toolkit<3.0.29`, `tornado<6.0`, `Pillow==8.2.0`, `scipy<1.6.0`, `scikit-image<0.18`, `asdf<2.8.0`, `sqlalchemy<1.4`, `hypothesis<6.0`).
- **System dependencies** that Python packages silently assume (e.g., `pandoc` for pypfm; `mpd` for piripherals; `openssh-server` + SSH agent for pysshutil; `libjpeg-dev`/`zlib1g-dev` for Pillow; `default-java` for service-manager).
- **Network isolation** via `conftest.py`, fixtures, or monkeypatching for projects whose tests hit live APIs (forex-python, supportdata, fossor, rs3clans.py, layouts-python, pyquery).
- **Venv placement:** some projects scan the working tree, so the venv must live outside the project folder (e.g., ftpsync) or start with a dot (e.g., `.venv-gamble`, `.venv-keplertools`).
- **`python -m pytest` as default:** module invocation avoids leaking to a global interpreter when a venv silently fails to install pytest.
- **Known issues** that matter when interpreting results: failures from environment coupling (service-manager; kindle_maker, since kindlegen was discontinued), locale-dependent doctests (pysshutil, pt-BR vs. en-US), flaky network tests, and `FutureWarning`/`DeprecationWarning` from modern frameworks on legacy code.

> When reproducing a specific project, treat the guide as the authoritative source and fall back to the project's own README only where the guide is silent.

## 8. Subject Projects

`data/projects_list.csv` has one row per project (61 rows) with the columns `id`, `project`, `test_path`, `test_command`, `venv_path`, `results_path`. All paths are relative to `$PROJECTS_ROOT`. In the original setup, the harness repository (`projetos-TT-Jo-o/`) lived inside that directory and wrote results to `projetos-TT-Jo-o/Test-<project>/`.

The 247 flaky tests are those covered by the raw data ([Section 4](#4-data-availability)) and the per-project guide. The list can be reconstructed from `scripts/FlapyRepos/flaky.csv` together with the pass/fail information in the Zenodo dataset. `docs/Organização_projeto_NOD.docx` is the original working document from which `projects_list.csv` was derived.

<details>
<summary>The 61 projects</summary>

airflow, Flexget, fonttools, hypothesis, ipython, kombu, libcloud, loguru, prefect, requests, seaborn, setuptools, urllib3, xonsh, amphipathic, analytic_shrinkage, cuckoopy, darkchess, data-partitioner, dockerfile_bakery, fistro, forex-python, supportdata, fossor, ftpsync, gamble_git, hotwing-core, jinja2-github, kb_python, keplertools, kevinarpe-rambutan3, kindle-maker, langsplit, layouts-python, levitate, nnweaver, override, packeteer, piripherals, pybnn, pycco, pylabeledrf, pymannkendall, pymemorydb, pypfm, pyquery, pyss3, pysshutil, python-matlab-functions, python-timemarker, r_map, rs3clans_py, service-manager, setigen, spreading_dye_sampler, textdistance, torch-embed-sim, torch-layer-normalization, uhashring, Verifone, wiki-futures

</details>

## 9. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `python3.12: command not found` | Install Python 3.12 (see 1.1). |
| `No module named venv` | `sudo apt install python3.12-venv`. |
| `pip install` fails building a wheel | Install system headers (`build-essential`, `python3.12-dev`, plus any library named in the error); see Section 7. |
| `No such file or directory` for a project path | `PROJECTS_ROOT` is not set in the current shell, or the folder name differs from `test_path` in `data/projects_list.csv`. |
| Harness cannot find the project/venv | Hard-coded base path in the scripts; update it to your `$PROJECTS_ROOT`. |
| `unrecognized arguments: --json-report` | `pytest-json-report` is missing in that venv (rerun 1.6). |
| `ModuleNotFoundError` although the package is installed in the venv | The shell leaked to the global interpreter; use `python -m pytest` and re-activate the venv. |
| Pass/fail results differ from the paper | Legacy projects pin old dependency versions; check the exact versions in Section 7. |
| A test hits a live API and fails with 403/429/timeouts | The guide documents `conftest.py`/fixtures that mock these calls (Section 7). |
| Execution times differ from the paper | Expected on different hardware; compare relative overheads between analyses, not absolute times. |
| A test does not behave as flaky | Flakiness is non-deterministic; it shows up across repeated executions, not necessarily in a single run. |

## 10. Citation

<!-- TODO: fill in authors, venue, year, and DOI once available. -->

```bibtex
@inproceedings{TODO_key,
  title  = {A Dynamic Behavior Perspective on Flaky Tests},
  author = {TODO},
  year   = {TODO},
  note   = {Artifact: https://github.com/kleyfferson/flaky-tests-dynamic-analysis, data: https://zenodo.org/records/23484158}
}
```

# Artifact: A Dynamic Behavior Perspective on Flaky Tests

This repository (<https://github.com/kleyfferson/flaky-tests-dynamic-analysis>) contains the code, data pointers, and replication protocol for the paper **"A Dynamic Behavior Perspective on Flaky Tests"**. It is intended as a complete, reproducible artifact for researchers and practitioners.

## Table of Contents

1. [Overview](#1-overview)
2. [Repository Structure](#2-repository-structure)
3. [Data Availability](#3-data-availability)
4. [System Requirements](#4-system-requirements)
5. [Replication Protocol](#5-replication-protocol)
   - [Step 0: Quick sanity check](#step-0-quick-sanity-check-optional-but-recommended)
   - [Step 1: Environment setup](#step-1-environment-setup)
   - [Step 2: Data collection](#step-2-data-collection)
   - [Step 3: Data analysis](#step-3-data-analysis)
6. [Subject Projects and Flaky Tests](#6-subject-projects-and-flaky-tests)
7. [Troubleshooting](#7-troubleshooting)
8. [Citation](#8-citation)

---

## 1. Overview

This artifact supports an empirical study of the **dynamic behavior of flaky tests** from three perspectives:

| Perspective | Analysis flag (`--analise`) |
|---|---|
| Code coverage | `coverage` |
| Profiling | `profiling` |
| Function-level tracing | `tracing` |
| Baseline (no dynamic analysis) | `none` |

The study analyzes **247 flaky tests** from **61 open-source Python projects**. Each flaky test is executed **400 times** under each of the four configurations.

## 2. Repository Structure

```
.
├── paper/                       # Submitted version of the paper
├── scripts/
│   ├── csv_runner.py            # Main harness: runs each flaky test N times per analysis
│   └── setup/
│       └── instalar_plugin.sh   # Installs pytest-json-report in every project venv
├── data/
│   ├── projects_list.csv        # The 61 projects: test path, test command, venv path, results path
│   ├── flaky_tests_hashes.csv   # The 247 flaky tests (test name -> hash)
│   ├── download_data.md         # How to download the raw data from Zenodo
│   └── results/                 # (created by you) raw data from Zenodo or from your own runs
├── analysis/                    # Scripts for statistics (average, std. deviation, CV) and plots
└── docs/
    ├── environment.md           # Hardware and software specifications
    └── replication_protocol.md  # Extended step-by-step guide
```

## 3. Data Availability

The raw data (300 executions for each of the three dynamic analyses and for the baseline without analysis, for all 247 flaky tests) is publicly available on Zenodo:

- **Zenodo:** <https://zenodo.org/records/23484158>

Download the dataset and place it in `data/results/`. Detailed instructions are in [`data/download_data.md`](data/download_data.md).

> **You can skip Steps 1 and 2** and go straight to [Step 3](#step-3-data-analysis) if you only want to reproduce the statistics and figures from the published raw data. Steps 1 and 2 are needed only to re-collect the data from scratch.

## 4. System Requirements

The experiments were executed on the machine below. Other Linux machines work, but absolute timings will differ.

| Component | Specification |
|---|---|
| CPU | Intel Core i9-14900KF (3.2 GHz base clock) |
| RAM | 64 GB DDR5 (5600 MHz) |
| Storage | 1 TB NVMe SSD |
| OS | Linux Mint 22.1, kernel 6.8.0-110-generic, x86-64 |
| Python | 3.12 |
| Parallelism | 16 workers (`--workers 16`) |

Additional notes:

- **Linux is required** (the setup scripts are Bash; paths use `/`).
- Re-collecting all data is long-running (4 configurations × 247 tests × 400 executions). Plan for a machine you can leave running; use `tmux`/`screen` or `nohup`.
- Reserve enough disk space for the 61 cloned projects, their 61 virtual environments, and the raw results. Some projects (e.g., Airflow, Prefect) have large dependency trees.

See [`docs/environment.md`](docs/environment.md) for full details.

## 5. Replication Protocol

A condensed version is given here; the extended guide is in [`docs/replication_protocol.md`](docs/replication_protocol.md).

### Step 0: Quick sanity check (optional but recommended)

Before the full run, verify the toolchain on a single small project (here, `loguru`) using the steps in Step 1, then run the project's tests once by hand:

```bash
cd "$PROJECTS_ROOT/loguru"
source .venv-loguru/bin/activate      # see data/projects_list.csv for the exact venv path
python -m pytest --json-report --json-report-file=/tmp/loguru_report.json -q
deactivate
```

If this runs and writes `/tmp/loguru_report.json`, the environment is working.

### Step 1: Environment setup

#### 1.1 Install system packages

On Ubuntu/Debian-based systems (the experiments used Linux Mint 22.1, which is Ubuntu 24.04-based):

```bash
sudo apt update
sudo apt install -y git build-essential python3.12 python3.12-venv python3.12-dev python3-pip
python3.12 --version    # expected: Python 3.12.x
```

Some projects compile native extensions or need system libraries; if a project's dependency install fails, check that project's own documentation (see [Troubleshooting](#7-troubleshooting)).

#### 1.2 Clone this repository

```bash
git clone https://github.com/kleyfferson/flaky-tests-dynamic-analysis.git
cd flaky-tests-dynamic-analysis
```

#### 1.3 Choose a projects directory

All 61 subject projects are cloned into a single directory. In the original experiments this was `/home/kleyfferson/Documentos/projetos_mestrado/`. The paths in `data/projects_list.csv` are **relative to this directory**:

```bash
export PROJECTS_ROOT="$HOME/flaky_projects"
mkdir -p "$PROJECTS_ROOT"
```

> **Note:** the original runs used the absolute paths above. If `scripts/csv_runner.py` has the base path hard-coded, update it to your `$PROJECTS_ROOT` before running (search for `projetos_mestrado`).

#### 1.4 Clone the 61 subject projects

Each row of `data/projects_list.csv` has a `project` name, whose upstream repository must be cloned into `$PROJECTS_ROOT/<folder>`, where `<folder>` is the first component of `test_path` (e.g., `Flexget/flexget/tests/` → folder `Flexget`; `kindle-maker` → folder `kindle_maker`).

<!-- TODO: add the upstream repository URL and the exact commit/tag for every project (e.g., in data/projects_list.csv columns `repo_url` and `commit`), so this step can be fully scripted. -->

```bash
cd "$PROJECTS_ROOT"
git clone <upstream-url> <folder>
cd <folder>
git checkout <commit>       # pin to the version used in the study
```

#### 1.5 Create one virtual environment per project

Each project has its **own isolated virtual environment**, located at the `venv_path` given in `data/projects_list.csv` (e.g., `airflow/venv-airflow/`, `loguru/venv-loguru/`, `gamble_git/.venv-gamble/`). Example for one project:

```bash
cd "$PROJECTS_ROOT/loguru"
python3.12 -m venv .venv-loguru
source .venv-loguru/bin/activate
pip install --upgrade pip
# install the project and its test dependencies (varies per project, e.g.):
pip install -e .
pip install pytest
deactivate
```

Repeat for all 61 projects. Install each project's dependencies following its own documentation (`requirements*.txt`, `pyproject.toml`, `setup.py`, `tox.ini`, or `CONTRIBUTING`). Keep the venv names and locations exactly as in `data/projects_list.csv`.

Special cases to be aware of (see the `test_command` column):

| Project | Detail |
|---|---|
| `override` | Test command uses the venv interpreter directly: `./.venv-override/bin/python -m pytest` |
| `darkchess` | Runs the installed package: `pytest --pyargs darkchess` |
| `python-matlab-functions` | Uses `nosetests --nocapture -v` |
| `torch-embed-sim`, `torch-layer-normalization` | Use `python -m nose` |
| `Verifone` | Uses `python -m unittest discover` |
| `hypothesis` | Venv lives inside `hypothesis/hypothesis-python/`; command is `python -m pytest hypothesis-python` |

Run each project's test command **exactly** as listed in `data/projects_list.csv`.

#### 1.6 Install `pytest-json-report` in every virtual environment

The harness collects per-run results through the `pytest-json-report` plugin. Install it in every venv with the provided script:

```bash
cd scripts/setup
chmod +x instalar_plugin.sh
./instalar_plugin.sh
```

To verify that a given venv has the plugin:

```bash
"$PROJECTS_ROOT/loguru/.venv-loguru/bin/pip" show pytest-json-report
```

<!-- TODO: if instalar_plugin.sh uses a hard-coded base path, document how to point it to $PROJECTS_ROOT. -->

#### 1.7 Check that every project's tests run

Before the long experiment, confirm that each project's test suite can be collected without errors (a quick `--collect-only` per project):

```bash
cd "$PROJECTS_ROOT/<folder>"
source <venv_path>/bin/activate
python -m pytest --collect-only -q | tail -n 3
deactivate
```

### Step 2: Data collection

All commands are run from the `scripts/` directory, with the Python used to run the harness being `python3` (3.12). Each flaky test is executed **400 times** per analysis technique, with 16 parallel workers. Redirect output to a log file for each run:

```bash
cd scripts

python3 csv_runner.py --analise coverage  --workers 16 > output_coverage_i9.txt  2>&1
python3 csv_runner.py --analise profiling --workers 16 > output_profiling_i9.txt 2>&1
python3 csv_runner.py --analise tracing   --workers 16 > output_tracing_i9.txt   2>&1
python3 csv_runner.py --analise none      --workers 16 > output_puro_i9.txt      2>&1
```

Recommendations:

- **Run the four configurations sequentially, never concurrently.** Running them at the same time competes for CPU and distorts the execution-time measurements.
- Avoid running other heavy workloads on the machine during collection, and keep the same `--workers` value across the four runs so they are comparable.
- For long runs, wrap the commands with `nohup` or run them inside `tmux`:

  ```bash
  nohup python3 csv_runner.py --analise coverage --workers 16 > output_coverage_i9.txt 2>&1 &
  tail -f output_coverage_i9.txt
  ```

- Per-project results are written to one results folder per project (e.g., `Test-airflow/`, `Test-loguru/`; the exact names are in the `results_path` column of `data/projects_list.csv`). Move or copy them under `data/results/` before running the analysis scripts.

| Flag | Meaning |
|---|---|
| `--analise {coverage,profiling,tracing,none}` | Dynamic analysis applied during the test runs (`none` = baseline, no analysis) |
| `--workers N` | Number of parallel workers (16 in the experiments) |

### Step 3: Data analysis

Use the scripts in `analysis/` to compute the statistics (average, standard deviation, and coefficient of variation) and to generate the figures presented in the paper (boxplots, histograms, bar charts, and violin plots).

```bash
# from the repository root
python3.12 -m venv .venv-analysis
source .venv-analysis/bin/activate
pip install pandas numpy matplotlib seaborn scipy   # adjust to the imports used in analysis/
cd analysis
python3 <script>.py                          # see the list of scripts below
```

<!-- TODO: list each script in analysis/ with a one-line description, its input (data/results/...) and its output (figure/table of the paper it reproduces). -->

## 6. Subject Projects and Flaky Tests

- [`data/projects_list.csv`](data/projects_list.csv) has one row per project (61 rows) with the columns `id`, `project`, `test_path`, `test_command`, `venv_path`, `results_path`. All paths are relative to `$PROJECTS_ROOT`. In the original setup, the harness repository (`projetos-TT-Jo-o/`) lived inside that directory and wrote the results to `projetos-TT-Jo-o/Test-<project>/`.
- [`data/flaky_tests_hashes.csv`](data/flaky_tests_hashes.csv) lists the 247 flaky tests with the hash used to identify each one in the raw data.
- [`docs/Organizacao_projeto_NOD.docx`](docs/Organizacao_projeto_NOD.docx) is the original working document from which both CSV files were derived.

The 61 projects are: airflow, Flexget, fonttools, hypothesis, ipython, kombu, libcloud, loguru, prefect, requests, seaborn, setuptools, urllib3, xonsh, amphipathic, analytic_shrinkage, cuckoopy, darkchess, data-partitioner, dockerfile_bakery, fistro, forex-python, supportdata, fossor, ftpsync, gamble_git, hotwing-core, jinja2-github, kb_python, keplertools, kevinarpe-rambutan3, kindle-maker, langsplit, layouts-python, levitate, nnweaver, override, packeteer, piripherals, pybnn, pycco, pylabeledrf, pymannkendall, pymemorydb, pypfm, pyquery, pyss3, pysshutil, python-matlab-functions, python-timemarker, r_map, rs3clans_py, service-manager, setigen, spreading_dye_sampler, textdistance, torch-embed-sim, torch-layer-normalization, uhashring, Verifone, wiki-futures.

## 7. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `python3.12: command not found` | Install Python 3.12 (see 1.1). |
| `No module named venv` | `sudo apt install python3.12-venv`. |
| `pip install` fails building a wheel | Install system headers (`build-essential`, `python3.12-dev`, plus any library named in the error). |
| `No such file or directory` for a project path | `PROJECTS_ROOT` is not set in the current shell, or the project folder name differs from `test_path` in `data/projects_list.csv`. |
| Harness cannot find the project/venv | Hard-coded base path in the scripts; update it to your `$PROJECTS_ROOT`. |
| `unrecognized arguments: --json-report` | `pytest-json-report` is missing in that venv (rerun 1.6). |
| Execution times differ from the paper | Expected on different hardware; compare relative overheads between analyses, not absolute times. |
| A test does not behave as flaky | Flakiness is non-deterministic; it appears across the 400 executions, not necessarily in a single run. |

## 8. Citation

<!-- TODO: fill in authors, venue, year, and DOI once available. -->

```bibtex
@inproceedings{TODO_key,
  title  = {A Dynamic Behavior Perspective on Flaky Tests},
  author = {TODO},
  year   = {TODO},
  note   = {Artifact: https://github.com/kleyfferson/flaky-tests-dynamic-analysis, data: https://zenodo.org/records/23484158}
}
```

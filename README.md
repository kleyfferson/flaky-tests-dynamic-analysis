# A Dynamic Behavior Perspective on Flaky Tests

Replication package for the paper *"A Dynamic Behavior Perspective on Flaky Tests"*.

Data: <https://zenodo.org/records/23484158>

We took 247 flaky tests from 61 open-source Python projects and ran each one 100 times under four setups: code coverage, profiling, function-level tracing, and a baseline with no instrumentation. This repository has the harness that runs the tests, the scripts that turn the raw results into the paper's numbers and figures, and notes on how each project was set up.

## What do you want to do?

- **Only reproduce the statistics and figures.** Download the data from Zenodo (see [Data](#data)) and jump to [Analysis](#analysis). You don't need to clone any of the 61 projects.
- **Collect everything again.** Follow the setup, collection and analysis sections in order. It takes a long time (3 analyses x 247 tests x 100 runs, plus the baseline).

## Layout

```text
analysis/    scripts, derived tables, and the figures used in the paper
data/        projects_list.csv and instructions for downloading the raw data
docs/        environment.md, the original working document, and the per-project guide
paper/       the PDF of the paper
scripts/     the harness (csv_runner.py and its helpers)
```

A few files worth knowing about:

- `data/projects_list.csv` has one row per project: repository, pinned commit, test path, test command, venv path and results folder. The paths are absolute and come from the machine where the study ran, where all projects lived under a single base directory. See [Setting up the projects](#setting-up-the-projects) for how to point them to your own.
- `docs/project_setup_guide.md` explains, project by project, what it took to get the tests running (patches, pinned versions, system packages) and what result we got.
- `scripts/csv_runner.py` runs each flaky test N times for a given analysis.
- `scripts/setup/instalar_plugin.sh` installs `pytest-json-report` in every project venv.
- `analysis/` holds one script per statistic or figure (`cv_violin.py`, `histograma.py`, `histograma_tracing.py`, `gerador_estatisticas_final_coverage.py`, `gerador_profiling.py`, and a few helpers). The intermediate tables (`boxplot.csv`, `Estatisticas_Cobertura_Final.xlsx`, `Profiling_preenchido.xlsx`, ...) are committed, but you can regenerate them from the raw data.

`data/results/` is not in the repository. It appears when you unpack the Zenodo data or run the collection yourself.

## Data

The Zenodo record has the 100 runs of coverage, profiling and tracing for all 247 tests, so 300 runs per test. Unpack it into `data/results/` (create the folder). More detail in `data/download_data.md`.

## Requirements

We ran everything on Linux Mint 22.1 (Ubuntu 24.04 base, kernel 6.8) with an Intel Core i9-14900KF, 64 GB of RAM and a 1 TB NVMe disk. Other Linux machines should work, but absolute timings will differ. Windows is not supported (the setup scripts are Bash).

The harness and the analysis use Python 3.12. Most subject projects only work on older interpreters, so you also need Python 3.8 (and 3.10 for `setigen`). On Ubuntu 24.04 the older versions come from the deadsnakes PPA:

```bash
sudo apt update
sudo apt install -y git build-essential python3.12 python3.12-venv python3.12-dev python3-pip
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3.10 python3.10-venv
```

Leave plenty of disk space: 61 clones, 61 virtual environments and the raw results add up, and projects like Airflow and Prefect have very large dependency trees.

## Setting up the projects

Everything per-project is in `data/projects_list.csv`. The steps below are the general recipe; for the quirks of individual projects see `docs/project_setup_guide.md`.

**1. Pick a projects directory and adapt the CSV.** All 61 projects go under one base directory of your choice:

```bash
export PROJECTS_ROOT="$HOME/flaky_projects"
mkdir -p "$PROJECTS_ROOT"
```

The paths in `data/projects_list.csv` start with the base directory of the original machine. This script finds that prefix and writes `projects_list.local.csv` with it replaced by your `$PROJECTS_ROOT`:

```bash
python3 - <<'EOF'
import csv, os

root = os.environ["PROJECTS_ROOT"]
with open("data/projects_list.csv", newline="") as f:
    rows = list(csv.DictReader(f))

old = os.path.commonpath([r["test_path"] for r in rows])
print("original base path:", old)

for r in rows:
    for col in ("test_path", "venv_path", "results_path"):
        if col in r:
            r[col] = r[col].replace(old, root, 1)

with open("projects_list.local.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
EOF
```

Some scripts in `scripts/` may also hard-code the original base path. Search them for the prefix printed above and replace it with your `$PROJECTS_ROOT`.

**2. Clone and pin the projects.** The folder name is the first directory under the base path in `test_path`, not the repository name (for example `gamble_git` is cloned from `jpetrucciani/gamble`):

```bash
python3 - <<'EOF'
import csv, os, subprocess

root = os.environ["PROJECTS_ROOT"]

with open("projects_list.local.csv", newline="") as f:
    for row in csv.DictReader(f):
        folder = os.path.relpath(row["test_path"], root).split(os.sep)[0]
        dest = os.path.join(root, folder)
        if not os.path.isdir(dest):
            subprocess.run(["git", "clone", row["repository_link"], dest], check=True)
        subprocess.run(["git", "-C", dest, "checkout", row["commit_hash"]], check=True)
EOF
```

Each project ends up in detached HEAD at the commit we studied. That's expected.

**3. Create one virtualenv per project** at the `venv_path` from `projects_list.local.csv`, install the project and its test dependencies, and make sure its tests run. Keep the venv names and locations exactly as in the CSV; the harness relies on them. Install steps differ a lot between projects, so follow `docs/project_setup_guide.md`.

A few projects use a different runner than plain `pytest`: `override` calls the venv interpreter directly, `darkchess` runs `pytest --pyargs darkchess`, `python-matlab-functions` uses `nosetests`, `torch-embed-sim` and `torch-layer-normalization` use `python -m nose`, `Verifone` uses `python -m unittest discover`, and `hypothesis` runs from its `hypothesis-python/` subfolder. The CSV has the exact command for each.

**4. Install `pytest-json-report` in every venv.** The harness reads per-run results from it.

```bash
cd scripts/setup
chmod +x instalar_plugin.sh
./instalar_plugin.sh
```

If the script has a hard-coded base path, point it to `$PROJECTS_ROOT`. To check one venv:

```bash
"$PROJECTS_ROOT/loguru/.venv-loguru/bin/pip" show pytest-json-report
```

**5. Quick sanity check.** `loguru` is small, so it's a good first project:

```bash
cd "$PROJECTS_ROOT/loguru"
source .venv-loguru/bin/activate
python -m pytest --json-report --json-report-file=/tmp/loguru_report.json -q
deactivate
```

If `/tmp/loguru_report.json` shows up, the toolchain works.

## Collecting data

From `scripts/`, run the four configurations one after another:

```bash
cd scripts
python3 csv_runner.py --analise coverage  > output_coverage.txt  2>&1
python3 csv_runner.py --analise profiling > output_profiling.txt 2>&1
python3 csv_runner.py --analise tracing   > output_tracing.txt   2>&1
python3 csv_runner.py --analise none      > output_puro.txt      2>&1
```

`none` is the baseline: it only records how many runs of each test passed and how many failed. The other three run each test 100 times with the corresponding analysis. Nothing runs in parallel, and the harness reserves 16 cores for the run.

Results go to one folder per project (`Test-airflow/`, `Test-loguru/`, ...; the exact names are in the `results_path` column). Copy or move them into `data/results/` before the analysis.

## Analysis

```bash
python3.12 -m venv .venv-analysis
source .venv-analysis/bin/activate
pip install pandas numpy matplotlib seaborn scipy openpyxl
cd analysis
python3 <script>.py
```

The script names tell you what they produce. For example, `cv_violin.py` writes the coefficient-of-variation violin plot to `pictures/`, and `gerador_estatisticas_final_coverage.py` writes the coverage statistics (average, standard deviation, CV) to `Estatisticas_Cobertura_Final.xlsx`.

## The 247 tests

The list of flaky tests (test name and hash) is in the last table of `docs/Organização_projeto_NOD.docx`. That document is also where `projects_list.csv` came from; the repository links and commit hashes were added to the CSV later. You can rebuild the list from `scripts/FlapyRepos/flaky.csv` plus the pass/fail data in the Zenodo record.

## The 61 projects

airflow, Flexget, fonttools, hypothesis, ipython, kombu, libcloud, loguru, prefect, requests, seaborn, setuptools, urllib3, xonsh, amphipathic, analytic_shrinkage, cuckoopy, darkchess, data-partitioner, dockerfile_bakery, fistro, forex-python, supportdata, fossor, ftpsync, gamble_git, hotwing-core, jinja2-github, kb_python, keplertools, kevinarpe-rambutan3, kindle-maker, langsplit, layouts-python, levitate, nnweaver, override, packeteer, piripherals, pybnn, pycco, pylabeledrf, pymannkendall, pymemorydb, pypfm, pyquery, pyss3, pysshutil, python-matlab-functions, python-timemarker, r_map, rs3clans_py, service-manager, setigen, spreading_dye_sampler, textdistance, torch-embed-sim, torch-layer-normalization, uhashring, Verifone, wiki-futures.

## Troubleshooting

- **`python3.8: command not found`** (or 3.10): add the deadsnakes PPA, see [Requirements](#requirements).
- **`No module named venv`**: `sudo apt install python3.8-venv` (or the matching version).
- **A `pip install` fails while building a wheel**: you are probably missing system headers (`build-essential`, `pythonX.Y-dev`, or a library named in the error). The project guide lists the ones we needed.
- **`No such file or directory` for a project path**: `PROJECTS_ROOT` isn't set in this shell, the folder name differs from what `test_path` says, or you are still using `data/projects_list.csv` instead of `projects_list.local.csv`, whose paths point to the original machine.
- **`unrecognized arguments: --json-report`**: that venv lacks `pytest-json-report`. Rerun the plugin script.
- **`ModuleNotFoundError` even though the package is in the venv**: the shell is probably using the global Python. Use `python -m pytest` and reactivate the venv.
- **Pass/fail counts differ from the paper**: old projects can need old dependency versions. See the project guide.
- **A test fails with 403, 429 or a timeout**: some tests call live services. Rate limits and network problems can cause this, and the services themselves may have changed since we ran them.
- **A test doesn't look flaky**: it may just not fail in your runs. Flakiness is non-deterministic and only shows up over many executions.
- **Timings don't match the paper**: expected on other hardware. Compare the relative overhead between analyses, not absolute times.

## Citation

<!-- TODO: fill in authors, venue, year, and DOI once available. -->

```bibtex
@inproceedings{TODO_key,
  title  = {A Dynamic Behavior Perspective on Flaky Tests},
  author = {TODO},
  year   = {TODO},
  note   = {Artifact: https://github.com/kleyfferson/flaky-tests-dynamic-analysis, data: https://zenodo.org/records/23484158}
}
```

Artifact: A Dynamic Behavior Perspective on Flaky Tests

This repository (https://github.com/kleyfferson/flaky-tests-dynamic-analysis) contains the code, documentation, and replication protocol for the paper "A Dynamic Behavior Perspective on Flaky Tests". The goal is to provide a complete, reproducible artifact for researchers and practitioners.

1. Overview

This artifact supports the empirical study that investigates the dynamic behavior of flaky tests from three perspectives: (i) code coverage, (ii) profiling, and (iii) function-level tracing. The study analyzes 247 flaky tests from 61 open-source Python projects.

2. Repository Structure

paper/: The submitted version of the paper.

scripts/: Core scripts for data collection (csv_runner.py) and environment setup.

data/:

projects_list.csv: List of the 61 projects (test paths, venv paths, test commands, results paths).

download_data.md: Instructions for downloading the raw data from Zenodo.

analysis/: Scripts for generating statistics and plots.

docs/:

environment.md: Hardware and software specifications.

replication_protocol.md: Step-by-step guide to replicate the experiment.

Organizacao_projeto_NOD.docx: Original document with the complete list of test paths, virtual environment paths, and test commands for all 61 projects.

3. Data Availability

The raw data (400 executions for each of the three dynamic analyses and the baseline without analysis, for all 247 flaky tests) is publicly available on Zenodo:

Zenodo DOI: https://zenodo.org/records/23484158

Download the dataset and place it in the data/results/ directory. For detailed instructions, see data/download_data.md.

4. System Requirements

The experiments were executed on a machine with the following specifications:

CPU: Intel Core i9-14900KF (3.2 GHz base clock)

RAM: 64 GB DDR5 (5600 MHz)

Storage: 1 TB NVMe SSD

OS: Linux Mint 22.1, kernel 6.8.0-110-generic, x86-64

Python: 3.12

See docs/environment.md for full environment details.

5. Replication Protocol

See docs/replication_protocol.md for the comprehensive step-by-step guide. A brief summary is provided below:

Step 1: Environment Setup

Install Python 3.12.

Create isolated virtual environments for each of the 61 projects. The complete list of paths and commands is available in data/projects_list.csv and in the original document docs/Organizacao_projeto_NOD.docx.

Install the pytest-json-report plugin in every virtual environment:

cd scripts/setup
chmod +x instalar_plugin.sh
./instalar_plugin.sh


Step 2: Data Collection

From the scripts/ directory, run each analysis. Each test is executed 400 times per analysis technique:

python3 csv_runner.py --analise coverage --workers 16 > output_coverage_i9.txt 2>&1
python3 csv_runner.py --analise profiling --workers 16 > output_profiling_i9.txt 2>&1
python3 csv_runner.py --analise tracing --workers 16 > output_tracing_i9.txt 2>&1
python3 csv_runner.py --analise none --workers 16 > output_puro_i9.txt 2>&1


Step 3: Data Analysis

Use the scripts located in the analysis/ directory to compute the statistics and generate the figures presented in the paper.

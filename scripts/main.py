import argparse
import os
import csv
import traceback
import re
import subprocess
import time
import json

def str_to_bool(value):
    return str(value).lower() in ("true", "1", "t")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-name")
    parser.add_argument("--test-path")
    parser.add_argument("--test-hash")
    parser.add_argument("--no-runs", type=int)
    parser.add_argument("--venv-path")
    parser.add_argument("--include-test-profiling", type=str_to_bool, default=False)
    parser.add_argument("--include-test-coverage", type=str_to_bool, default=False)
    parser.add_argument("--include-test-tracing", type=str_to_bool, default=False)
    parser.add_argument("--workers", type=int, default=1) 
    
    args = parser.parse_args()

    output_base = os.path.join(os.getcwd(), f"Test-{args.repo_name}", args.test_hash)
    os.makedirs(output_base, exist_ok=True)
    
    error_log_file = os.path.join(output_base, f"erros_execucao_{args.test_hash}.log")
    errors_found = []

    try:
        from Analise.VirtualEnvironment import VirtualEnvironment
        venv = VirtualEnvironment(args.venv_path, args.repo_name)
    except Exception as e:
        print(f"Erro crítico ao inicializar VirtualEnvironment: {e}")
        with open(error_log_file, "w", encoding="utf-8") as f:
            f.write(f"Erro crítico ao inicializar VirtualEnvironment:\n{traceback.format_exc()}\n")
        return

    test_file_name_raw = args.test_path.split("::")[-1].split("/")[-1].replace(".py", "")
    test_file_name = re.sub(r'[^a-zA-Z0-9_]', '_', test_file_name_raw)

    print(f"\n============================================================")
    print(f" Iniciando Framework para o Hash: {args.test_hash[:8]}")
    print(f" Projeto: {args.repo_name} | Qtd Runs: {args.no_runs}")
    print(f"============================================================\n")

    for i in range(1, args.no_runs + 1):
        print(f"\n--- [RUN {i}/{args.no_runs}] Iniciando execuções ---")
        
        # ===== PROFILING =====
        if args.include_test_profiling:
            try:
                resultado = venv.executePytest(args.test_path, output_base, i, "profiling", args.test_hash)
                
                run_dir = os.path.join(output_base, f"Run-{i}")
                prof_out = os.path.join(run_dir, f"profiling_{i}.prof")
                csv_out = os.path.join(run_dir, f"{test_file_name}-profiling.csv")
                
                # NOME ESPECÍFICO PARA O PROFILING
                json_report = os.path.join(run_dir, "resultado_profiling.json")
                
                # Tenta ler o status robusto em txt gerado pelo VirtualEnvironment
                status_txt_path = os.path.join(run_dir, "status_run_profiling.txt")
                if os.path.exists(status_txt_path):
                    with open(status_txt_path, "r", encoding="utf-8") as f_txt:
                        status_teste = f_txt.read().strip()
                else:
                    status_teste = "Passed" if resultado.returncode == 0 else "Failed"
                
                if os.path.exists(json_report):
                    try:
                        with open(json_report, 'r') as f_json:
                            dados = json.load(f_json)
                            status_teste = dados.get('summary', {}).get('outcome', status_teste).capitalize()
                    except:
                        pass
                
                if os.path.exists(prof_out):
                    subprocess.run([
                        "python3", "parse_profiling.py",
                        "--input_file", prof_out,
                        "--output_file", csv_out,
                        "--repo-name", args.repo_name,
                        "--test-name", args.test_path,
                        "--run", str(i),
                        "--status", status_teste
                    ])
                else:
                    errors_found.append(f"[Run {i}] Arquivo .prof não foi gerado.")
            except Exception as e:
                errors_found.append(f"[Run {i}] Profiling falhou com exceção: {e}")

        # ===== COVERAGE =====
        if args.include_test_coverage:
            try:
                resultado = venv.executePytest(args.test_path, output_base, i, "coverage", args.test_hash)
                
                run_dir = os.path.join(output_base, f"Run-{i}")
                xml_input = os.path.join(run_dir, f"coverage_{i}.xml")
                csv_output = os.path.join(run_dir, f"{test_file_name}-coverage.csv")
                
                # NOME ESPECÍFICO PARA O COVERAGE
                json_report = os.path.join(run_dir, "resultado_coverage.json")
                
                # Tenta ler o status robusto em txt gerado pelo VirtualEnvironment
                status_txt_path = os.path.join(run_dir, "status_run_coverage.txt")
                if os.path.exists(status_txt_path):
                    with open(status_txt_path, "r", encoding="utf-8") as f_txt:
                        status_teste = f_txt.read().strip()
                else:
                    status_teste = "Passed" if resultado.returncode == 0 else "Failed"
                
                if os.path.exists(json_report):
                    try:
                        with open(json_report, 'r') as f_json:
                            dados = json.load(f_json)
                            status_teste = dados.get('summary', {}).get('outcome', status_teste).capitalize()
                    except:
                        pass
                
                if os.path.exists(xml_input):
                    subprocess.run([
                        "python3", "parse_coverage.py",
                        "--xml", xml_input,
                        "--csv", csv_output,
                        "--repo-name", args.repo_name,
                        "--test-name", args.test_path,
                        "--run", str(i),
                        "--status", status_teste
                    ], capture_output=True, text=True)
                else:
                    errors_found.append(f"[Run {i}] Arquivo XML de coverage não foi encontrado.")
            except Exception as e:
                errors_found.append(f"[Run {i}] Coverage falhou com exceção: {e}")

        # ===== TRACING =====
        if args.include_test_tracing:
            try:
                resultado = venv.executePytest(args.test_path, output_base, i, "tracing", args.test_hash)
                time.sleep(1) # Aguarda o filesystem escrever o gz
                
                run_dir = os.path.join(output_base, f"Run-{i}")
                csv_out = os.path.join(run_dir, f"{test_file_name}-tracing.csv")
                
                # NOME ESPECÍFICO PARA O TRACING
                json_report = os.path.join(run_dir, "resultado_tracing.json")
                
                # Salva calls.gz diretamente na pasta da Run
                calls_gz = os.path.join(run_dir, "calls.gz")
                
                # Tenta ler o status robusto em txt gerado pelo VirtualEnvironment
                status_txt_path = os.path.join(run_dir, "status_run_tracing.txt")
                if os.path.exists(status_txt_path):
                    with open(status_txt_path, "r", encoding="utf-8") as f_txt:
                        status_teste = f_txt.read().strip()
                else:
                    status_teste = "Passed" if resultado.returncode == 0 else "Failed"
                
                if os.path.exists(json_report):
                    try:
                        with open(json_report, 'r') as f_json:
                            dados = json.load(f_json)
                            status_teste = dados.get('summary', {}).get('outcome', status_teste).capitalize()
                    except:
                        pass
                
                if os.path.exists(calls_gz) and os.path.getsize(calls_gz) > 0:
                    subprocess.run([
                        "python3", "parse_tracing.py", 
                        "--input_file", calls_gz,
                        "--output_file", csv_out,
                        "--repo-name", args.repo_name,
                        "--test-name", args.test_path,
                        "--run", str(i),
                        "--status", status_teste
                    ])
                else:
                    errors_found.append(f"[Run {i}] Arquivo calls.gz não gerado ou vazio em {run_dir}.")
            except Exception as e:
                errors_found.append(f"[Run {i}] Tracing falhou com exceção: {e}")

    # ===== GERAÇÃO DO SUMMARY PARA COVERAGE =====
    if args.include_test_coverage:
        summary_file = os.path.join(output_base, "summary_coverage.csv")
        summary_data = []
        
        for i in range(1, args.no_runs + 1):
            run_dir = os.path.join(output_base, f"Run-{i}")
            run_csv = os.path.join(run_dir, f"{test_file_name}-coverage.csv")
            
            if os.path.exists(run_csv):
                try:
                    with open(run_csv, newline='', encoding='utf-8') as f_in:
                        reader = csv.reader(f_in)
                        header = next(reader)
                        for row in reader:
                            if row:
                                summary_data.append(row)
                except Exception as e:
                    errors_found.append(f"[Run {i}] Erro ao ler CSV individual: {e}")
            else:
                errors_found.append(f"[Run {i}] Coverage falhou silenciosamente (CSV não gerado).")
        
        if summary_data:
            try:
                with open(summary_file, 'w', newline='', encoding='utf-8') as fout:
                    writer = csv.writer(fout)
                    writer.writerow(['Project Name', 'Test name', 'Run', 'Test Result', 'Percentual de Cobertura (%)', 'Linhas Cobertas'])
                    writer.writerows(summary_data)
                print(f"\n>>> Sumário gerado em: {summary_file}")
            except Exception as e:
                errors_found.append(f"Erro ao salvar sumário de coverage: {e}")

    # ===== GERAÇÃO DO SUMMARY GERAL DE EXECUÇÃO (CONTAGEM PASS/FAIL) =====
    summary_file_exec = os.path.join(output_base, "summary_execution.csv")
    summary_data_exec = []
    
    total_passed = 0
    total_failed = 0
    
    # Determina qual análise usar como base para contar o status principal
    analise_principal = "tracing" if args.include_test_tracing else "coverage" if args.include_test_coverage else "profiling"
    
    for i in range(1, args.no_runs + 1):
        run_dir = os.path.join(output_base, f"Run-{i}")
        status_txt_path = os.path.join(run_dir, f"status_run_{analise_principal}.txt")
        
        status = "Unknown"
        if os.path.exists(status_txt_path):
            with open(status_txt_path, "r", encoding="utf-8") as f_txt:
                status = f_txt.read().strip()
                if status == "Passed":
                    total_passed += 1
                elif status == "Failed":
                    total_failed += 1
        
        summary_data_exec.append([args.repo_name, args.test_path, i, status])

    try:
        with open(summary_file_exec, 'w', newline='', encoding='utf-8') as fout:
            writer = csv.writer(fout)
            writer.writerow(['Project Name', 'Test name', 'Run', 'Test Result'])
            writer.writerows(summary_data_exec)
    except Exception as e:
        errors_found.append(f"Erro ao salvar sumário de execução: {e}")

    # === EXIBIÇÃO NO CONSOLE DA CONTAGEM ===
    print("\n" + "="*60)
    print(f"   RESUMO DO TESTE: {args.test_hash[:8]}")
    print(f"   Total Runs: {args.no_runs}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    print("="*60)

    if errors_found:
        print("\n" + "="*60)
        print(f"   ATENÇÃO: ERROS REGISTRADOS NO HASH {args.test_hash[:8]}...")
        print("="*60)
        
        with open(error_log_file, "a", encoding="utf-8") as f:
            f.write(f"Relatório de Erros - Teste: {args.test_path}\n")
            f.write("="*60 + "\n")
            for err in errors_found:
                print(f"[-] {err}")
                f.write(f"{err}\n")
                
        print("="*60)
    else:
        print(f"\n>>> [SUCESSO] O hash {args.test_hash[:8]} finalizou perfeitamente.")

if __name__ == "__main__":
    main()

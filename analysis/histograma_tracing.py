import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# 1. Leitura e Preparação dos Dados (Tracing)
# ==========================================================
ARQUIVO = "Cópia de reproducedTests_Classificado_Profissional_100.xlsx"
ABA = "Paper - Table 2"

df = pd.read_excel(
    ARQUIVO,
    sheet_name=ABA,
    header=None,
    skiprows=3,
    usecols="AH,AI,AJ,AK,AL,AN,AO",
    names=["NPassed", "NFailed", "Result", "Passed AVG", "Passed SD", "Failed AVG", "Failed SD"],
)

# Converter valores numéricos
for coluna in ["Passed AVG", "Passed SD", "Failed AVG", "Failed SD"]:
    df[coluna] = df[coluna].astype(str).str.replace(",", ".", regex=False)
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

df = df.dropna(how="all")

# Filtrar estritamente os 104 "Observed Flaky Test"
observados = df[df["Result"] == "Observed Flaky Test"].copy()

# Dados do Boxplot (AVG) - Excluindo os 0.0
passed_avg = observados[observados["Passed AVG"] > 0]["Passed AVG"].dropna()
failed_avg = observados[observados["Failed AVG"] > 0]["Failed AVG"].dropna()

# Dados do Histograma (SD) - Todos os 104 testes (incluindo 0.0)
passed_sd = observados["Passed SD"].dropna()
failed_sd = observados["Failed SD"].dropna()

# ==========================================================
# 2. Configurações Globais de Gráfico (Nível Mestrado/Paper)
# ==========================================================
plt.rcParams.update({
    "font.size": 11,
    "font.family": "sans-serif",
    "axes.titleweight": "bold",
    "axes.labelweight": "bold"
})

# ==========================================================
# FUNÇÃO 1: BOXPLOT (AVG)
# ==========================================================
def plot_boxplot_log(ax, dado, titulo, cor, ylim=None):
    ax.boxplot(
        dado,
        patch_artist=True,
        widths=0.5,
        showmeans=True,
        meanline=False,
        boxprops=dict(facecolor=cor, linewidth=1.5),
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker='o', markerfacecolor='red', markeredgecolor='black', markersize=4, alpha=0.6),
        meanprops=dict(marker='D', markerfacecolor='yellow', markeredgecolor='black', markersize=6),
    )
    ax.set_title(titulo, fontweight="bold", fontsize=13)
    ax.set_xticks([])
    ax.set_yscale("log")
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

# ==========================================================
# FUNÇÃO 2: HISTOGRAMA COM EIXO X FORMATADO (SD)
# ==========================================================
def plot_scientific_histogram(ax, dado, titulo, cor):
    vmax = dado.max()
    
    # Bins: 1ª caixa reservada unicamente para o [0, 0.25], e as demais em logarítmica de 0.5 até vmax
    bins = [0, 0.25] + list(np.logspace(np.log10(0.5), np.log10(vmax), 13))
    
    contagens, bordas, patches = ax.hist(
        dado, bins=bins, color=cor, edgecolor="black", linewidth=1.2, alpha=0.9
    )
    
    # Escala SymLog ajustada com linthresh=1.0 para evitar frações/expoentes negativos como 10^-1
    ax.set_xscale('symlog', linthresh=1.0, linscale=1.0)
    
    # Rótulos explícitos e limpos do eixo X
    ticks = [0, 1, 10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8]
    tick_labels = ["0", "$10^0$", "$10^1$", "$10^2$", "$10^3$", "$10^4$", "$10^5$", "$10^6$", "$10^7$", "$10^8$"]
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels, fontsize=11, fontweight='bold')
    
    # Exibir a contagem exata no topo de cada coluna
    for count, patch in zip(contagens, patches):
        if count > 0:
            x_center = patch.get_x() + patch.get_width() / 2
            ax.text(x_center, count + 1.0, f"{int(count)}",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Média e Mediana
    ax.axvline(dado.median(), color="black", linewidth=2.0, linestyle="-", label=f"Median = {dado.median():,.2g}")
    ax.axvline(dado.mean(), color="red", linewidth=2.0, linestyle="--", label=f"Mean = {dado.mean():,.2g}")

    # Títulos e Eixos
    ax.set_title(titulo, pad=15, fontsize=14, fontweight="bold")
    ax.set_ylabel("Number of Tests", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tracing Size (Bytes) - SymLog Scale", fontsize=12, fontweight="bold")
    
    ax.set_ylim(0, max(contagens) * 1.25)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.9)

    # Anotação de Zeros Exatos
    pct_zero = 100 * (dado == 0).sum() / len(dado)
    ax.text(0.22, 0.88, f"Exact Zeros: {int((dado == 0).sum())} ({pct_zero:.1f}%)", 
            transform=ax.transAxes, ha="left", va="top",
            fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="black", alpha=0.9))

# ==========================================================
# 3. Geração da FIGURA 1: AVG (Boxplot)
# ==========================================================
fig_avg, axs_avg = plt.subplots(1, 2, figsize=(10, 5))

vmin_avg = min(passed_avg.min(), failed_avg.min())
vmax_avg = max(passed_avg.max(), failed_avg.max())
ylim_avg = (10 ** np.floor(np.log10(vmin_avg)), 10 ** np.ceil(np.log10(vmax_avg)))

plot_boxplot_log(axs_avg[0], passed_avg, "Passing Executions", "#AEC7E8", ylim=ylim_avg)
plot_boxplot_log(axs_avg[1], failed_avg, "Failing Executions", "#FF9896", ylim=ylim_avg)

axs_avg[0].set_ylabel("Tracing Size (Bytes) - Log Scale", fontsize=12, fontweight="bold")
axs_avg[1].set_ylabel("Tracing Size (Bytes) - Log Scale", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig("histograms_tracing_avg_passed_failed.png", dpi=600, bbox_inches="tight")
print("Figura 1 Salva: histograms_tracing_avg_passed_failed.png")

# ==========================================================
# 4. Geração da FIGURA 2: SD (Histograma SymLog)
# ==========================================================
fig_sd, axs_sd = plt.subplots(1, 2, figsize=(14, 6))

plot_scientific_histogram(axs_sd[0], passed_sd, "Passing Executions", "#AEC7E8")
plot_scientific_histogram(axs_sd[1], failed_sd, "Failing Executions", "#FF9896")

plt.tight_layout()
plt.savefig("histograms_tracing_sd_scientific.png", dpi=600, bbox_inches="tight")
print("Figura 2 Salva: histograms_tracing_sd_scientific.png")

plt.show()

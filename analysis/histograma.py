import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Ler o arquivo XLSX Original (Coverage) direto da planilha
# ==========================================================

ARQUIVO = "Cópia de reproducedTests_Classificado_Profissional_100.xlsx"
ABA = "Paper - Table 2"

# Colunas na aba "Paper - Table 2" (Code Coverage):
#   G = #Passed   H = #Failed   I = Result
#   J = Passed AVG   K = Passed SD
#   M = Failed AVG   N = Failed SD
df = pd.read_excel(
    ARQUIVO,
    sheet_name=ABA,
    header=None,
    skiprows=3,
    usecols="G,H,I,J,K,M,N",
    names=["NPassed", "NFailed", "Result",
           "Passed AVG", "Passed SD", "Failed AVG", "Failed SD"],
)

# ==========================================================
# Converter para numero
# ==========================================================

for coluna in ["Passed AVG", "Passed SD", "Failed AVG", "Failed SD"]:
    df[coluna] = (
        df[coluna]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

df = df.dropna(how="all")

# ==========================================================
# AVG: BOXPLOT, apenas os Observed Flaky Test (93 testes)
# SD : HISTOGRAMA EXATO, apenas os Observed Flaky Test (93 testes)
# ==========================================================

observados = df[df["Result"] == "Observed Flaky Test"].copy()
print("Observed Flaky Test (linhas):", len(observados))

passed_avg = observados[observados["Passed AVG"] > 0]["Passed AVG"].dropna()
failed_avg = observados[observados["Failed AVG"] > 0]["Failed AVG"].dropna()

passed_sd = observados["Passed SD"].dropna()
failed_sd = observados["Failed SD"].dropna()

print("--------------------------------")
print("Valores utilizados")
print("--------------------------------")
print("Total de linhas lidas:", len(df))
print("Passed AVG (so' Observed, >0):", len(passed_avg))
print("Failed AVG (so' Observed, >0):", len(failed_avg))
print("Passed SD  (so' Observed, incl. 0.0):", len(passed_sd),
      "| zeros:", (passed_sd == 0).sum())
print("Failed SD  (so' Observed, incl. 0.0):", len(failed_sd),
      "| zeros:", (failed_sd == 0).sum())
print("--------------------------------")

# ==========================================================
# Configuracao do grafico
# ==========================================================

plt.rcParams.update({
    "font.size": 12,
    "font.weight": "bold",
    "axes.titleweight": "bold",
    "axes.labelweight": "bold"
})

# ==========================================================
# FUNCAO PARA PLOTAR UM BOXPLOT (usada para o AVG)
# ==========================================================

def plot_boxplot(ax, dado, titulo, cor, ylim=None):
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
        flierprops=dict(marker='o', markerfacecolor='red',
                         markeredgecolor='black', markersize=4, alpha=0.6),
        meanprops=dict(marker='D', markerfacecolor='yellow',
                        markeredgecolor='black', markersize=6),
    )
    ax.set_title(titulo, fontweight="bold")
    ax.set_xticks([])
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.grid(axis="y", linestyle="--", alpha=0.4)


# ==========================================================
# FUNCAO PARA PLOTAR UM HISTOGRAMA EXATO (usada para o SD)
# ==========================================================

def plot_histogram(ax, dado, titulo, cor, xlim=None, ylim=None, pct_zero=None):
    media = dado.mean()
    mediana = dado.median()

    # Contagem exata de cada valor individual unico da planilha
    val_counts = dado.value_counts().sort_index()
    largura = (xlim[1] - xlim[0]) * 0.015 if xlim else 0.02

    ax.bar(val_counts.index, val_counts.values, width=largura,
           color=cor, edgecolor="black", linewidth=0.5, align="center")

    # Exibe a contagem no topo de todas as colunas que existem
    for x_val, count in val_counts.items():
        if count > 0:
            ax.text(x_val, count + (ylim[1] * 0.01 if ylim else 0.5), f"{int(count)}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.axvline(mediana, color="black", linewidth=2.0, linestyle="-",
               label=f"Median = {mediana:.3g}")
    ax.axvline(media, color="red", linewidth=2.0, linestyle="--",
               label=f"Mean = {media:.3g}")

    ax.set_title(titulo, fontweight="bold")
    ax.set_ylabel("Number of tests")

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(fontsize=9, loc="upper right")

    if pct_zero is not None:
        ax.text(
            0.12, 0.97, f"{pct_zero:.1f}% = 0.0",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="black", alpha=0.85)
        )


# ==========================================================
# FIGURA 1: AVG -- Boxplot (93 testes)
# ==========================================================

fig_avg, axs_avg = plt.subplots(1, 2, figsize=(10, 5))

vmax_avg = max(passed_avg.max(), failed_avg.max())
vmin_avg = min(passed_avg.min(), failed_avg.min())
margem = (vmax_avg - vmin_avg) * 0.08
ylim_avg = (max(0, vmin_avg - margem), vmax_avg + margem)

plot_boxplot(axs_avg[0], passed_avg, "Passing Executions", "#AEC7E8", ylim=ylim_avg)
plot_boxplot(axs_avg[1], failed_avg, "Failing Executions", "#FF9896", ylim=ylim_avg)

axs_avg[0].set_ylabel("Coverage Percentage (%)")
axs_avg[1].set_ylabel("Coverage Percentage (%)")

plt.tight_layout()
plt.savefig("boxplots_avg_passed_failed.png", dpi=600, bbox_inches="tight")
plt.show()


# ==========================================================
# FIGURA 2: SD -- Histograma Exato (93 testes)
# ==========================================================

fig_sd, axs_sd = plt.subplots(1, 2, figsize=(10, 5))

pct_zero_passed = 100 * (passed_sd == 0).sum() / len(passed_sd)
pct_zero_failed = 100 * (failed_sd == 0).sum() / len(failed_sd)

vmax = max(passed_sd.max(), failed_sd.max())
vmax_count = max(passed_sd.value_counts().max(), failed_sd.value_counts().max())

ylim_sd = (0, vmax_count * 1.15)
xlim_sd = (-0.1, vmax + 0.2)

plot_histogram(axs_sd[0], passed_sd, "Passing Executions", "#AEC7E8",
               xlim=xlim_sd, ylim=ylim_sd, pct_zero=pct_zero_passed)
plot_histogram(axs_sd[1], failed_sd, "Failing Executions", "#FF9896",
               xlim=xlim_sd, ylim=ylim_sd, pct_zero=pct_zero_failed)

axs_sd[0].set_xlabel("Coverage Percentage (%)")
axs_sd[1].set_xlabel("Coverage Percentage (%)")

plt.tight_layout()
plt.savefig("boxplots_sd_passed_failed.png", dpi=600, bbox_inches="tight")
plt.show()

import matplotlib.pyplot as plt
import numpy as np

# Dados extraídos do documento RQ4.pdf
projects = ['analytic_shrinkage', 'keplertools', 'langsplit', 'service-manager', 'setigen']
passed_calls = [399786, 401548, 723807, 487595, 3274157]
failed_calls = [506529, 522313, 807400, 988251, 3285746]

x = np.arange(len(projects))
width = 0.35

# Cores mais suaves (tons pastéis/acadêmicos)
color_passed = '#8DA0CB' # Azul/Lilás suave
color_failed = '#FC8D62' # Laranja/Salmão suave

# Configuração do gráfico
fig, ax = plt.subplots(figsize=(11, 6.5))
rects1 = ax.bar(x - width/2, passed_calls, width, label='Passed', color=color_passed, edgecolor='black', linewidth=0.8)
rects2 = ax.bar(x + width/2, failed_calls, width, label='Failed', color=color_failed, edgecolor='black', linewidth=0.8)

# Adicionando rótulos e título
ax.set_ylabel('Total Function Calls (ncalls)', fontsize=12)
ax.set_title('Profiling Divergence: Passed vs. Failed Executions', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(projects, rotation=15, ha="right", fontsize=11)
ax.legend(fontsize=12)

# Usando escala logarítmica
ax.set_yscale('log')

# Adicionando os valores no topo das barras
ax.bar_label(rects1, padding=3, fmt='%d', fontsize=9)
ax.bar_label(rects2, padding=3, fmt='%d', fontsize=9)

# Aumentar um pouco o limite superior do eixo Y para que os números não fiquem cortados pela borda
ax.set_ylim(bottom=100000, top=max(failed_calls) * 5)

# Salvando a figura em PNG
plt.tight_layout()
plt.savefig('rq4_profiling_suave.png', format='png', bbox_inches='tight', dpi=300)
plt.show()

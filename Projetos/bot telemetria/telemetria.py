import pandas as pd
import matplotlib.pyplot as plt
import os

def analisar_log(arquivo_csv):
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo '{arquivo_csv}' não encontrado!")
        return

    print(f"🔍 Lendo telemetria do arquivo: {arquivo_csv}...")
    
    try:
        # Lê o CSV. Usamos sep=';' porque exportações de injeção costumam vir com ponto e vírgula
        df = pd.read_csv(arquivo_csv, sep=';')
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo: {e}")
        return
        
    # Criação do Gráfico (3 painéis empilhados compartilhando a mesma linha de tempo)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle('Análise de Telemetria - Dinâmica do Motor', fontsize=16, fontweight='bold')

    # Painel 1: Rotação (RPM)
    ax1.plot(df['Tempo(s)'], df['RPM'], color='blue', linewidth=2)
    ax1.set_ylabel('RPM', fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Painel 2: Pressão de Turbo (MAP)
    ax2.plot(df['Tempo(s)'], df['Pressao_Turbo(bar)'], color='red', linewidth=2)
    ax2.set_ylabel('Pressão (bar)', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.7)

    # Painel 3: Sonda Lambda (Mistura Ar/Combustível)
    ax3.plot(df['Tempo(s)'], df['Sonda_Lambda'], color='green', linewidth=2)
    ax3.set_ylabel('Lambda', fontweight='bold')
    ax3.set_xlabel('Tempo (segundos)', fontweight='bold')
    
    # Adiciona uma linha tracejada laranja indicando a mistura alvo segura (ex: 0.85)
    ax3.axhline(y=0.85, color='orange', linestyle='--', label='Alvo Seguro (0.85)')
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.7)

    # Ajusta o layout para não cortar os textos
    plt.tight_layout()
    
    # Salva o gráfico como imagem na mesma pasta
    nome_saida = arquivo_csv.replace('.csv', '_grafico.png')
    plt.savefig(nome_saida, dpi=300) # dpi=300 garante alta resolução
    
    print(f"✅ Análise concluída! Gráfico de alta resolução gerado: {nome_saida}")

if __name__ == "__main__":
    analisar_log("logtst.csv")
import re
import sys
import argparse
import statistics
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

def parse_line(line):
    """
    Faz o parse de uma linha do log, extraindo os pares chave=valor.
    Valores entre aspas (que podem conter espaços) são tratados corretamente.
    """
    pattern = r'(\w+)=("[^"]*"|\S+)'
    matches = re.findall(pattern, line)
    data = {}
    for key, value in matches:
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        data[key] = value
    return data

def parse_timestamp(ts_str):
    """
    Converte a string de timestamp (no formato ISO com offset) para um objeto datetime.
    """
    try:
        # Python 3.7+ aceita o formato ISO com offset
        return datetime.fromisoformat(ts_str)
    except Exception as e:
        # Se houver problema, tenta remover o ':' do offset
        if ts_str[-3] == ":":
            ts_str = ts_str[:-3] + ts_str[-2:]
        return datetime.fromisoformat(ts_str)

def parse_duration(duration_str):
    """
    Converte uma string de duração (ex.: "10s") para segundos (float).
    Atualmente, apenas durações em segundos são tratadas.
    """
    if duration_str.endswith("s"):
        try:
            return float(duration_str[:-1])
        except:
            return None
    return None

# graficos

def gerar_grafico_tempo_processamento(cycles, output_file):
    times = [cycle["processing_time"] for cycle in cycles]
    indices = list(range(1, len(times)+1))
    plt.figure(figsize=(14, 8))
    plt.bar(indices, times, color='skyblue', label="Tempo de Processamento")
    plt.xlabel("Ciclo")
    plt.ylabel("Tempo de Processamento (ms)")
    plt.title("Tempo de Processamento por Ciclo")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def gerar_grafico_intervalos(intervals, output_file):
    if not intervals:
        return
    indices = list(range(1, len(intervals)+1))
    plt.figure(figsize=(14, 8))
    plt.plot(indices, intervals, marker='o', linestyle='-', color='orange', label="Intervalo entre ciclos")
    plt.xlabel("Entre Ciclos")
    plt.ylabel("Intervalo (ms)")
    plt.title("Intervalos entre Inícios dos Ciclos")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def gerar_grafico_tags(total_lidas, total_falhas, output_file):
    """Gráfico de pizza para o desempenho na leitura OPC-UA (estrutura modificada)."""
    sizes = [total_lidas, total_falhas]
    labels = ['Tags Lidas', 'Tags Falhas']
    colors = ['green', 'red']
    total = total_lidas + total_falhas
    percents = [s / total * 100 for s in sizes] if total > 0 else [0, 0]
    # Para a pizza, mantém-se uma figura que preserve o formato circular.
    plt.figure(figsize=(10, 8))
    # Removido o autopct para não mostrar strings sobre os pedaços.
    wedges, _ = plt.pie(sizes, colors=colors, startangle=90)
    plt.title("Desempenho na Leitura OPC-UA")
    plt.axis('equal')
    # Cria a legenda com as informações (valor absoluto e porcentagem).
    legend_labels = [f"{label}: {size} ({percent:.1f}%)" for label, size, percent in zip(labels, sizes, percents)]
    plt.legend(wedges, legend_labels, title="Resultados", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório de Performance - Análise de Log', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(config, cycles, intervals, output_filename):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    #Configuração
    pdf.cell(0, 10, 'Configuração da Coleta Cíclica:', ln=True)
    pdf.cell(0, 10, f"  Duração do ciclo: {config.get('duracao_ciclo', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"  Amostras por ciclo: {config.get('amostras_por_ciclo', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"  Intervalo de amostragem: {config.get('intervalo_amostragem', 'N/A')}", ln=True)
    pdf.ln(5)
    
    #Detalhes dos ciclos
    pdf.cell(0, 10, f"Total de ciclos de leitura OPC-UA: {len(cycles)}", ln=True)
    pdf.ln(5)
    
    # Tabela 1: Tempos de processamento de cada ciclo (em ms)
    pdf.cell(0, 10, 'Tempos de Processamento de Cada Ciclo (ms):', ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(30, 10, "Ciclo", border=1)
    pdf.cell(50, 10, "Início", border=1)
    pdf.cell(50, 10, "Fim", border=1)
    pdf.cell(50, 10, "T. Processamento", border=1)
    pdf.ln()
    
    for i, cycle in enumerate(cycles, start=1):
        inicio = cycle.get("start").strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        fim = cycle.get("end").strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        processing_time = cycle.get("processing_time", 0)
        pdf.cell(30, 10, str(i), border=1)
        pdf.cell(50, 10, inicio, border=1)
        pdf.cell(50, 10, fim, border=1)
        pdf.cell(50, 10, f"{processing_time:.3f}", border=1)
        pdf.ln()
    
    pdf.ln(5)
    
    # Tabela 2: Intervalos entre inícios dos ciclos
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, 'Intervalos Entre Inícios de Ciclos (ms):', ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, "Entre Ciclos", border=1)
    pdf.cell(40, 10, "Intervalo (ms)", border=1)
    intervalo_amostragem = config.get('intervalo_amostragem', 'N/A')
    intervalo_amostragem_corrigido = float(intervalo_amostragem.replace("ms", ""))
    expected_cycle_interval_ms = intervalo_amostragem_corrigido
    pdf.cell(40, 10, "Esperado (ms)", border=1)
    pdf.cell(40, 10, "Diferença (ms)", border=1)
    pdf.ln()
    
    for i, interval in enumerate(intervals, start=1):
        diff_ms = interval - expected_cycle_interval_ms
        pdf.cell(40, 10, f"{i} - {i+1}", border=1)
        pdf.cell(40, 10, f"{interval:.3f}", border=1)
        pdf.cell(40, 10, f"{expected_cycle_interval_ms:.3f}", border=1)
        pdf.cell(40, 10, f"{diff_ms:.3f}", border=1)
        pdf.ln()
    
    pdf.ln(5)
    
    # Cálculos analíticos
    processing_times = [cycle["processing_time"] for cycle in cycles]
    avg_proc = statistics.mean(processing_times)
    min_proc = min(processing_times)
    max_proc = max(processing_times)
    stdev_proc = statistics.stdev(processing_times) if len(processing_times) > 1 else 0

    if intervals:
        avg_interval = statistics.mean(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
    else:
        avg_interval = min_interval = max_interval = stdev_interval = 0

    total_lidas = sum(cycle.get("tags_lidas", 0) for cycle in cycles)
    total_falhas = sum(cycle.get("tags_falhas", 0) for cycle in cycles)
    total_tags = total_lidas + total_falhas
    success_rate = (total_lidas / total_tags * 100) if total_tags > 0 else 0

    #Dados dos Ciclos
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Dados dos Ciclos", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(80, 10, "Total de ciclos analisados:", border=0)
    pdf.cell(0, 10, f"{len(cycles)}", ln=True)
    pdf.ln(2)

    #Tempo de Processamento (ms)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Tempo de Processamento (ms)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(80, 10, "Média:", border=0)
    pdf.cell(0, 10, f"{avg_proc:.2f} ms ({avg_proc/1000:.3f} s)", ln=True)
    pdf.cell(80, 10, "Mínimo:", border=0)
    pdf.cell(0, 10, f"{min_proc:.2f} ms ({min_proc/1000:.3f} s)", ln=True)
    pdf.cell(80, 10, "Máximo:", border=0)
    pdf.cell(0, 10, f"{max_proc:.2f} ms ({max_proc/1000:.3f} s)", ln=True)
    pdf.cell(80, 10, "Desvio Padrão:", border=0)
    pdf.cell(0, 10, f"{stdev_proc:.2f} ms ({stdev_proc/1000:.3f} s)", ln=True)
    pdf.ln(2)

    #Intervalos entre Ciclos (ms)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Intervalos entre Ciclos (ms)", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(80, 10, "Média:", border=0)
    pdf.cell(0, 10, f"{avg_interval:.2f} ms ({avg_interval/1000:.3f} s)", ln=True)
    pdf.cell(80, 10, "Mínimo:", border=0)
    pdf.cell(0, 10, f"{min_interval:.2f} ms ({min_interval/1000:.3f} s)", ln=True)
    pdf.cell(80, 10, "Máximo:", border=0)
    pdf.cell(0, 10, f"{max_interval:.2f} ms ({max_interval/1000:.3f} s)", ln=True)
    pdf.cell(80, 10, "Desvio Padrão:", border=0)
    pdf.cell(0, 10, f"{stdev_interval:.2f} ms ({stdev_interval/1000:.3f} s)", ln=True)
    pdf.ln(2)

    #Comparação com Intervalo Esperado
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "4. Comparação com Intervalo Esperado", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(80, 10, "Intervalo esperado (ms):", border=0)
    pdf.cell(0, 10, f"{expected_cycle_interval_ms:.2f} ms ({expected_cycle_interval_ms/1000:.3f} s)", ln=True)
    if intervals:
        avg_diff = avg_interval - expected_cycle_interval_ms
        pdf.cell(80, 10, "Diferença média (ms):", border=0)
        pdf.cell(0, 10, f"{avg_diff:.2f} ms ({avg_diff/1000:.3f} s)", ln=True)
    else:
        pdf.cell(0, 10, "Sem dados de intervalos para comparação.", ln=True)
    pdf.ln(2)

    #Desempenho na Leitura OPC-UA
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "5. Desempenho na Leitura OPC-UA", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(80, 10, "Taxa de sucesso (%):", border=0)
    pdf.cell(0, 10, f"{success_rate:.2f}%", ln=True)
    pdf.cell(80, 10, "Total de lidas:", border=0)
    pdf.cell(0, 10, f"{total_lidas}", ln=True)
    pdf.cell(80, 10, "Total de falhas:", border=0)
    pdf.cell(0, 10, f"{total_falhas}", ln=True)
    pdf.ln(5)
    
    #Gráficos
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "6. Gráficos", ln=True)
    pdf.ln(5)
    
    caminho_grafico1 = "grafico_tempo_processamento.png"
    gerar_grafico_tempo_processamento(cycles, caminho_grafico1)
    pdf.cell(0, 10, "6.1 Tempo de Processamento por Ciclo", ln=True)
    pdf.image(caminho_grafico1, x=10, w=pdf.w - 20)
    pdf.ln(10)
    
    caminho_grafico2 = "grafico_intervalos.png"
    gerar_grafico_intervalos(intervals, caminho_grafico2)
    pdf.cell(0, 10, "6.2 Intervalos entre Inícios dos Ciclos", ln=True)
    try:
        pdf.image(caminho_grafico2, x=10, w=pdf.w - 20)
    except Exception as e:
        pdf.cell(0, 10, "Sem dados suficientes para gerar o gráfico de intervalos.", ln=True)
    pdf.ln(10)
    
    caminho_grafico3 = "grafico_tags.png"
    gerar_grafico_tags(total_lidas, total_falhas, caminho_grafico3)
    pdf.cell(0, 10, "6.3 Desempenho na Leitura OPC-UA", ln=True)
    pdf.image(caminho_grafico3, x=pdf.w/2 - 40, w=100)
    
    pdf.output(output_filename)
    print(f"Relatório PDF gerado: {output_filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Analisador de log e gerador de relatório PDF com insights analíticos de performance."
    )
    parser.add_argument("logfile", help="Arquivo de log a ser analisado")
    parser.add_argument("--output", help="Nome do arquivo PDF de saída", default="relatorio.pdf")
    args = parser.parse_args()
    
    config = {}
    cycles = []        
    current_cycle = {} 
    
    with open(args.logfile, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = parse_line(line)
            if "time" not in data:
                continue
            try:
                timestamp = parse_timestamp(data["time"])
            except Exception as e:
                print(f"Erro ao interpretar timestamp: {data['time']}")
                continue
            
            if data.get("msg") == "Iniciando coleta cíclica":
                config = data
            
            if data.get("msg") == "Iniciando leitura de tags OPC-UA":
                current_cycle = {
                    "start": timestamp,
                    "total_tags": int(data.get("total_tags", 0))
                }
            elif data.get("msg") == "Leitura OPC-UA concluída" and current_cycle:
                current_cycle["end"] = timestamp
                current_cycle["tags_lidas"] = int(data.get("tags_lidas", 0))
                current_cycle["tags_falhas"] = int(data.get("tags_falhas", 0))
                processing_time = (current_cycle["end"] - current_cycle["start"]).total_seconds() * 1000
                current_cycle["processing_time"] = processing_time
                cycles.append(current_cycle)
                current_cycle = {}
    
    if not cycles:
        print("Nenhum ciclo de leitura OPC-UA encontrado no log.")
        sys.exit(1)
    
    intervals = []
    for i in range(1, len(cycles)):
        interval_ms = (cycles[i]["start"] - cycles[i-1]["start"]).total_seconds() * 1000
        intervals.append(interval_ms)
    
    generate_pdf_report(config, cycles, intervals, args.output)

if __name__ == "__main__":
    main()

import tkinter as tk
import psutil
import socket
import datetime
import threading
import time

# Variáveis globais
ip_alvo = ""
limite_memoria = 0
limite_cpu = 0
porta_alvo = 5060  # Substitua pela porta desejada
thread_ativa = None
thread_ativa_running = False  # Flag para indicar que a thread está em execução
cor_botao_iniciar = "SystemButtonFace" 

# Função para capturar o uso de memória
def obter_percentual_uso_memoria():
    estatisticas_memoria = psutil.virtual_memory()
    percentual_uso_memoria = estatisticas_memoria.percent
    return percentual_uso_memoria

# Função para capturar o uso de processador 
def obter_soma_uso_processador():
    # Obtém as estatísticas de uso da CPU para cada núcleo com intervalo de 3 segundos. 
    #Foi optado este cálculo porque o mesmo trás um resultado mais real
    per_cpu = psutil.cpu_percent(interval=3, percpu=True)
    soma_uso_cpu = 0
    for idx, usage in enumerate(per_cpu):
        soma_uso_cpu += usage
        #print("CORE_{}: {}%".format(idx+1, usage)) Descomentar caso queira ver núcleo por núcleo printado no terminal 
    return soma_uso_cpu

# Função para checar a conexão com o IP alvo a partir de um protocolo (Default SIP 5060). conexão socket
def verificar_conexao(ip, porta, protocolo):
    try:
        sock = socket.socket(socket.AF_INET if protocolo == 'tcp' else socket.AF_INET6, 
                             socket.SOCK_STREAM if protocolo == 'tcp' else socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.connect((ip, porta) if protocolo == 'tcp' else (ip, porta))
        print("Conexão bem-sucedida para {}:{} ({})".format(ip, porta, protocolo.upper()))
    except socket.error as e:
        print("Falha ao conectar a {}:{} ({}): {}".format(ip, porta, protocolo.upper(), e))
        with open(r"C:\auditoria.log", "a") as log_file:
            log_file.write("{} - Falha ao conectar a {}:{} ({}): {}\n".format(datetime.datetime.now(), ip, porta, protocolo.upper(), e))
    finally:
        sock.close()

# Loop quando o botão iniciar for precionado
def auditoria_loop():
    global thread_ativa_running
    while thread_ativa_running:
        soma_cpu_total = obter_soma_uso_processador()
        if soma_cpu_total > limite_cpu:
            with open(r"C:\auditoria.log", "a") as log_file:
                log_file.write("{} - Limite de CPU atingido ({}%)\n".format(datetime.datetime.now(), soma_cpu_total))

        percentual_memoria = obter_percentual_uso_memoria()
        if percentual_memoria > limite_memoria:
            with open(r"C:\auditoria.log", "a") as log_file:
                log_file.write("{} - Limite de memória atingido ({}%)\n".format(datetime.datetime.now(), percentual_memoria))

        verificar_conexao(ip_alvo, porta_alvo, 'tcp')

        time.sleep(4)

# Gatilho
def iniciar_auditoria():
    global ip_alvo, limite_memoria, limite_cpu, porta_alvo, thread_ativa, thread_ativa_running, cor_botao_iniciar

    ip_alvo = entrada_ip.get()
    limite_memoria = float(entrada_memoria.get())
    limite_cpu = float(entrada_cpu.get())
    porta_alvo = 5060  

    if not thread_ativa_running:
        cor_botao_iniciar = "green"  
        thread_ativa_running = True
        thread_ativa = threading.Thread(target=auditoria_loop)
        thread_ativa.start()

    botao_iniciar.config(bg=cor_botao_iniciar) 

# Função para parar o loop
def parar_auditoria():
    global thread_ativa_running, cor_botao_iniciar
    if thread_ativa_running:
        cor_botao_iniciar = "SystemButtonFace" 
        thread_ativa_running = False
        thread_ativa.join()

    botao_iniciar.config(bg=cor_botao_iniciar)  

# Fecha a interface e para os processos da mesma de forma correta
def fechar_janela():
    parar_auditoria()
    app.destroy()

# Interface gráfica
app = tk.Tk()
app.title("Auditoria de Sistema")
app.geometry("300x200")

tk.Label(app, text="IP:").grid(row=0, column=0)
tk.Label(app, text="% Memória:").grid(row=1, column=0)
tk.Label(app, text="% CPU:").grid(row=2, column=0)

entrada_ip = tk.Entry(app)
entrada_memoria = tk.Entry(app)
entrada_cpu = tk.Entry(app)

entrada_ip.grid(row=0, column=1)
entrada_memoria.grid(row=1, column=1)
entrada_cpu.grid(row=2, column=1)

botao_iniciar = tk.Button(app, text="Iniciar Auditoria", command=iniciar_auditoria)
botao_iniciar.grid(row=3, column=0, columnspan=2)

botao_parar = tk.Button(app, text="Parar Auditoria", command=parar_auditoria)
botao_parar.grid(row=4, column=0, columnspan=2)

app.protocol("WM_DELETE_WINDOW", fechar_janela)

app.mainloop()

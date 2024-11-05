import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import BooleanVar
from tkinter import ttk  # Importando o módulo ttk para widgets mais avançados
import logging
import socket
import ctypes
import shutil

# Importa funções para bloquear no firewall e sites específicos
from functions.firewall import bloquear_no_firewall
from functions.blocker import bloquear_sites

# Configuração de log para registrar erros e ações
logging.basicConfig(level=logging.DEBUG, filename='bloqueador.log', 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Caminho do arquivo de blacklist
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
sites_file = os.path.join(diretorio_atual, "blacklist.txt")

# Definição de cores da interface para facilitar o ajuste visual
co0 = "#f0f3f5"  # Cinza claro
co1 = "#feffff"  # Branco
co2 = "#3fb5a3"  # Verde
co3 = "#f25f5c"  # Vermelho
co4 = "#403d3d"  # Preto

azul_color = "#3f9dfb"    # Azul para o botão
green_color = "#3fb5a3"   # Verde para o botão
white_color = "#ffffff"   # Branco para o texto
orange_color = "orange"   # Laranja para o botão

# Configuração da janela principal
janela = tk.Tk()
janela.title("Bloqueador de Apostas")
janela.geometry("410x460")
janela.configure(background=co1)
janela.resizable(width=False, height=False)

# Função para solicitar permissão de administrador
def solicitar_permissao():
    """Verifica e solicita permissão de administrador se necessário."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        # Solicita permissão de administrador caso o programa não esteja com privilégios elevados
        ctypes.windll.shell32.ShellExecuteW(None, "runas", os.sys.executable, " ".join(os.sys.argv), None, 1)
        return False

# Função para copiar arquivo hosts
def copiar_hosts():
    """Copia o arquivo hosts para o diretório do sistema."""
    if solicitar_permissao():
        try:
            origem = os.path.join(diretorio_atual, "hosts")
            destino = r"C:\Windows\System32\drivers\etc\hosts"
            shutil.copyfile(origem, destino)
            messagebox.showinfo("Sucesso", "Arquivo hosts copiado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao copiar o arquivo hosts: {e}")
            logging.error(f"Erro ao copiar o arquivo hosts: {e}")

# Função para carregar a lista de sites bloqueados
def carregar_blacklist():
    """Carrega a lista de sites bloqueados do arquivo e exibe na interface."""
    try:
        with open(sites_file, "r") as file:
            sites = file.readlines()
            if not sites:
                messagebox.showinfo("Aviso", "A lista de sites bloqueados está vazia.")
            else:
                for site in sites:
                    site = site.strip()
                    if site:
                        lista.insert(tk.END, site)
    except FileNotFoundError:
        logging.error("Arquivo de blacklist não encontrado. Criando um novo arquivo.")
        with open(sites_file, "w") as file:
            file.write("")  # Cria um novo arquivo se não existir
        messagebox.showerror("Erro", "Arquivo de blacklist não encontrado. Um novo arquivo foi criado.")
        carregar_blacklist()

# Função para verificar se uma regra já existe
def regra_existente(dominio):
    """Verifica se a regra de bloqueio já existe no firewall para evitar duplicação."""
    try:
        regra_nome = f'Bloqueio de {dominio}'
        output = os.popen('netsh advfirewall firewall show rule name="{}"'.format(regra_nome)).read()
        return regra_nome in output
    except Exception as e:
        logging.error(f"Erro ao verificar regra: {e}")
        return False

# Função para bloquear domínio adicionando ao arquivo hosts
def bloquear_por_dominio(dominio):
    """Bloqueia um domínio adicionando uma entrada no arquivo hosts."""
    try:
        if regra_existente(dominio):
            logging.info(f"O domínio {dominio} já está bloqueado.")
            return True

        with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as hosts_file:
            hosts_file.write(f"0.0.0.0 {dominio}\n")
        
        logging.info(f"Domínio {dominio} bloqueado com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Falha ao bloquear {dominio} no arquivo hosts: {e}")
        return False

# Configuração dos frames da interface
frame_logo = tk.Frame(janela, width=410, height=60, bg=co1, relief="flat")
frame_logo.grid(row=0, column=0, columnspan=2, sticky="nsew")

frame_corpo = tk.Frame(janela, width=410, height=400, bg=co1, relief="flat")
frame_corpo.grid(row=1, column=0, columnspan=2, sticky="nsew")

# Configurando o frame do logo
imagem = Image.open(os.path.join(diretorio_atual, "assets/block.png"))
imagem = imagem.resize((40, 40))
image = ImageTk.PhotoImage(imagem)

l_image = tk.Label(frame_logo, height=60, image=image, bg=co1)
l_image.place(x=20, y=0)

l_logo = tk.Label(frame_logo, text="Bloqueador de Apostas", height=1, anchor="ne", font=('Ivy', 20), bg=co1, fg=co4)
l_logo.place(x=70, y=12)

# Linha separadora decorativa
l_linha = tk.Label(frame_logo, text="Bloqueador de Apostas", height=1, width="445", anchor="nw", font=('Ivy', 1), bg=co2)
l_linha.place(x=0, y=57)

# Configurando o frame corpo
l_blacklist = tk.Label(frame_corpo, text="Lista de bets bloqueadas", height=1, font=('Ivy', 12), bg=co1, fg=co4)
l_blacklist.place(x=18, y=20)

# Lista de sites bloqueados
lista = tk.Listbox(frame_corpo, width=40, height=14, bg=co0, fg=co4)
lista.place(x=20, y=50)

# Barra de Progresso para exibir o progresso de bloqueio
progresso = ttk.Progressbar(frame_corpo, orient="horizontal", length=360, mode="determinate")
progresso.place(x=20, y=330)

# Checkbox para concordar em participar da rede de apoio
checkbox_var = BooleanVar()
checkbox = tk.Checkbutton(
    frame_corpo,
    text="Ao clicar em 'Bloquear Sites', você concorda em comunicar a sua rede de apoio possíveis situações de jogo compulsivo.",
    variable=checkbox_var,
    bg=co1,
    fg=co4,
    font=('Ivy', 8),
    wraplength=380,
    anchor="w",
    justify="left"
)
checkbox.place(x=16, y=290)

# Botão para bloquear no firewall
b_bloquear = tk.Button(
    frame_corpo, text="Bloquear Firewall", width=15, height=2,
    bg=green_color, fg=white_color, command=lambda: bloquear_sites(checkbox_var, lista, progresso, janela), relief="flat"
)
b_bloquear.place(x=270, y=50)

# Botão para copiar o arquivo hosts
botao_copiar_hosts = tk.Button(
    frame_corpo, text="Bloquear DNS", width=15, height=2,
    bg=azul_color, fg=white_color, command=copiar_hosts, relief="flat"
)
botao_copiar_hosts.place(x=270, y=100)

# Botão para abrir configurações (implementação opcional)
botao_apoio = tk.Button(
    frame_corpo, text="Configurações", width=15, height=2,
    bg=orange_color, fg=white_color, relief="flat"
)
botao_apoio.place(x=270, y=150)

# Carregar a blacklist na inicialização
carregar_blacklist()

# Iniciar o loop da interface
janela.mainloop()

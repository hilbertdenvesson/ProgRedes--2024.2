import socket
import os

DIRBASE = "files/"
INTERFACE = '127.0.0.1'
PORT = 12345

def list(conn):
    try:
        files = os.listdir(DIRBASE)
        file_list = []
        for file in files:
            file_path = os.path.join(DIRBASE, file)
            if os.path.isfile(file_path):
                file_list.append(f"{file} {os.path.getsize(file_path)} Bytes")
        
        file_list_data = '\n'.join(file_list).encode('utf-8')
        conn.sendall(len(file_list_data).to_bytes(4, 'big') + file_list_data)
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
        conn.sendall((0).to_bytes(4, 'big'))  # Tamanho zero indica erro

def help(conn):
    help_text = '''Comandos disponíveis:
    list - Lista os arquivos no servidor com seus tamanhos
    help - Mostra esta mensagem de ajuda
    sget - Solicita o download de um arquivo (nome do arquivo será enviado separadamente)
    '''
    conn.sendall(help_text.encode('utf-8'))

def sget(conn):
    try:
        # Recebe o comprimento do nome do arquivo (2 bytes)
        file_name_length = conn.recv(2)
        if len(file_name_length) == 0:  # Verifica se não recebeu dados
            print("Erro: Nenhum dado recebido para o comprimento do nome do arquivo")
            return

        file_name_length = int.from_bytes(file_name_length, 'big')

        # Recebe o nome do arquivo
        file_name = conn.recv(file_name_length).decode('utf-8').strip()
        print(f"Pedido de download do arquivo: {file_name}")

        file_path = os.path.join(DIRBASE, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            conn.sendall(b'\x00\x00')  # Flag de sucesso
            conn.sendall(file_size.to_bytes(4, 'big'))  # Tamanho do arquivo

           
            fd = open(file_path, 'rb')
            while True:
                data = fd.read(4096)
                if data == b"": 
                    break
                conn.sendall(data) 

            fd.close()
            print(f"Arquivo '{file_name}' enviado com sucesso.")
        else:
            conn.sendall(b'\x00\x01')  
            print(f"Arquivo '{file_name}' não encontrado.")
    except Exception as e:
        print(f"Erro ao processar o comando 'sget': {e}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((INTERFACE, PORT))
sock.listen(1)

sock.settimeout(60)

print("Servidor TCP escutando em ...", (INTERFACE, PORT))

while True:
    try:
        conn, addr = sock.accept()
        print("Conexão recebida de:", addr)

        command = conn.recv(4)
        if len(command) == 0:  # Verifica se não recebeu nenhum dado
            print("Erro: Nenhum dado recebido para o comando")
            conn.close()
            continue

        command = command.decode('utf-8').strip()
        print(f"Comando recebido: {command}")
        # 'lower()' para ignorar caso digitado maiúscula ou minúscula
        if command.lower() == "list":
            list(conn)
        elif command.lower() == "help":
            help(conn)
        elif command.lower() == "sget":
            sget(conn)
        else:
            print(f"Comando desconhecido: {command}")
            conn.sendall(b'\x00\x01')  # Sinaliza erro para comando inválido
            continue

        conn.close()
    except Exception as erro:
        print(f"Erro no servidor: {erro}")
        break

sock.close()


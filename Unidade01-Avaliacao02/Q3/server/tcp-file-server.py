import socket
import os
import glob

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
    mget - Solicita o download de múltiplos arquivos de acordo com a máscara 
    '''
    conn.sendall(help_text.encode('utf-8'))

def sget(conn):
    try:
        file_name_length = conn.recv(2)
        if len(file_name_length) == 0:  
            print("Erro: Nenhum dado recebido para o comprimento do nome do arquivo")
            return

        file_name_length = int.from_bytes(file_name_length, 'big')
        file_name = conn.recv(file_name_length).decode('utf-8').strip()
        print(f"Pedido de download do arquivo: {file_name}")

        file_path = os.path.join(DIRBASE, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            conn.sendall(b'\x00\x00')  
            conn.sendall(file_size.to_bytes(4, 'big'))  

            fd = open(file_path, 'rb')
            file_data = fd.read(4096)
            while file_data != b'':
                conn.send(file_data)
                file_data = fd.read(4096)
            fd.close()

            print(f"Arquivo '{file_name}' enviado com sucesso.")
        else:
            conn.sendall(b'\x00\x01')  
            print(f"Arquivo '{file_name}' não encontrado.")
    except Exception as e:
        print(f"Erro ao processar o comando 'sget': {e}")

def mget(conn):
    try:
        mask_length = conn.recv(2)
        mask_length = int.from_bytes(mask_length, 'big')
        mask = conn.recv(mask_length).decode('utf-8').strip()

        print(f"Máscara recebida: {mask}")

        file_paths = glob.glob(os.path.join(DIRBASE, mask))

        if not file_paths:
            conn.sendall(b'\x00\x01')  
            print(f"Nenhum arquivo encontrado com a máscara '{mask}'.")
            return

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            conn.sendall(b'sget')  
            file_name_bytes = file_name.encode('utf-8')
            conn.sendall(len(file_name_bytes).to_bytes(2, 'big') + file_name_bytes)

            file_size = os.path.getsize(file_path)
            conn.sendall(file_size.to_bytes(4, 'big'))

            fd = open(file_path, 'rb')
            file_data = fd.read(4096)
            while file_data != b'':
                conn.send(file_data)
                file_data = fd.read(4096)
            fd.close()

            print(f"Arquivo '{file_name}' enviado com sucesso.")
    except Exception as e:
        print(f"Erro ao processar o comando 'mget': {e}")
        conn.sendall(b'\x00\x01')  


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
        if len(command) == 0:  
            print("Erro: Nenhum dado recebido para o comando")
            conn.close()
            continue

        command = command.decode('utf-8').strip()
        print(f"Comando recebido: {command}")
        if command.lower() == "list":
            list(conn)
        elif command.lower() == "help":
            help(conn)
        elif command.lower() == "sget":
            sget(conn)
        elif command.lower() == "mget":
            mget(conn)
        else:
            print(f"Comando desconhecido: {command}")
            conn.sendall(b'\x00\x01')  
            continue

        conn.close()
    except Exception as erro:
        print(f"Erro no servidor: {erro}")
        break

sock.close()


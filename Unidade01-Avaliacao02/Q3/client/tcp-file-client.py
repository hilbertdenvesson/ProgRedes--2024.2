import socket
import os

DIRBASE = "files/"
SERVER = '127.0.0.1'
PORT = 12345

def list(sock):
    sock.sendall(b'list')
    list_size_data = sock.recv(4)
    list_size = int.from_bytes(list_size_data, "big")

    if list_size == 0:
        print("Erro ao listar arquivos ou diretório vazio.")
    else:
        data = sock.recv(list_size).decode('utf-8')
        print("Arquivos no servidor:")
        print(data)

def help(sock):
    sock.sendall(b'help')
    help_text = sock.recv(4096).decode('utf-8')
    print(help_text)

def sget(sock):
    file_name = input("Digite o nome do arquivo para download: ").strip()
    if file_name == "":
        print("Nome do arquivo não pode estar vazio.")
        return

    sock.sendall(b'sget')
    file_name_bytes = file_name.encode('utf-8')
    sock.sendall(len(file_name_bytes).to_bytes(2, 'big') + file_name_bytes)

    response_flag = sock.recv(2)
    if response_flag == b'\x00\x01':
        print(f"Arquivo '{file_name}' não encontrado no servidor.")
        return

    file_size_data = sock.recv(4)
    file_size = int.from_bytes(file_size_data, "big")
    print(f"Tamanho do arquivo recebido: {file_size} bytes")

    local_file_path = os.path.join(DIRBASE, file_name)
    fd = open(local_file_path, 'wb')
    while file_size > 0:
        rec_bytes = sock.recv(4096)
        fd.write(rec_bytes)
        file_size -= len(rec_bytes)
    fd.close()

    print(f"Arquivo '{file_name}' gravado em '{local_file_path}'")

def mget(sock):
    # Solicita ao usuário a máscara de arquivos
    mask = input("Digite a máscara para selecionar arquivos (ex: *.jpg): ").strip()
    if mask == "":
        print("A máscara não pode estar vazia.")
        return

    # Envia o comando e a máscara ao servidor
    sock.sendall(b'mget')
    mask_bytes = mask.encode('utf-8')
    sock.sendall(len(mask_bytes).to_bytes(2, 'big') + mask_bytes)

    # Recebe resposta inicial do servidor
    response_flag = sock.recv(2)
    if response_flag == b'\x00\x01':
        print(f"Nenhum arquivo encontrado para a máscara '{mask}'.")
        return

    # Loop para receber múltiplos arquivos
    while True:
        # Recebe o tamanho do nome do arquivo
        file_name_length_data = sock.recv(2)
        if len(file_name_length_data) == 0:  # Finalização
            return

        file_name_length = int.from_bytes(file_name_length_data, 'big')
        file_name = sock.recv(file_name_length).decode('utf-8').strip()

        # Recebe o tamanho do arquivo
        file_size_data = sock.recv(4)
        file_size = int.from_bytes(file_size_data, 'big')

        # Inicia a gravação do arquivo recebido
        local_file_path = os.path.join(DIRBASE, file_name)
        try:
            fd = open(local_file_path, 'wb')
            while file_size > 0:
                rec_bytes = sock.recv(4096)
                fd.write(rec_bytes)
                file_size -= len(rec_bytes)
        except Exception as e:
            print(f"Erro ao gravar o arquivo '{file_name}': {e}")
        finally:
            fd.close()

        print(f"Arquivo '{file_name}' gravado em '{local_file_path}'")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))

sock.settimeout(20)

while True:
    try:
        command = input("Digite o comando (digite 'help' para ver os comandos disponíveis): ").strip()

        if command.lower() == "list":
            list(sock)
        elif command.lower() == "help":
            help(sock)
        elif command.lower() == "sget":
            sget(sock)
        elif command.lower() == "mget":
            mget(sock)
        else:
            print(f"Comando desconhecido: {command}")
            continue

    except Exception as erro:
        print(f"Erro no cliente: {erro}")
        break

sock.close()

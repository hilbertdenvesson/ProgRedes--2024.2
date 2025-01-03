import socket
import os

DIRBASE = "files/"
SERVER = '127.0.0.1'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER, PORT))

sock.settimeout(20)

while True:
    try:
        fileName = input("Arquivo a pedir ao servidor: ").strip()
        if fileName == "":
            print("Nome de arquivo vazio.")
            continue

        print("Enviando pedido ao servidor:", fileName)

        # Envia o comprimento do nome do arquivo (2 bytes) e o nome do arquivo
        fileNameBytes = fileName.encode('utf-8')
        sock.sendall(len(fileNameBytes).to_bytes(2, 'big') + fileNameBytes)

        # Recebe o sinalizador e tamanho do arquivo
        file_size_data = sock.recv(2)
        file_size_flag = file_size_data
        if file_size_flag == b'\x00\x01':
            print(f"Arquivo '{fileName}' não encontrado ou está vazio no servidor.")
            continue

        # Recebe o tamanho do arquivo (4 bytes)
        file_size_data = sock.recv(4)
        file_size = int.from_bytes(file_size_data, "big")

        print(f"Tamanho do arquivo recebido: {file_size} bytes")
        print("Gravando arquivo localmente.")
        
        # Recebe e grava o arquivo
        fd = open(os.path.join(DIRBASE, fileName), 'wb')
        tam = file_size
        while tam > 0:
            data = sock.recv(4096)
            fd.write(data)
            tam -= len(data)
        fd.close()

        print(f"Arquivo '{fileName}' gravado em '{DIRBASE}{fileName}'")

    except Exception as erro:
        print(f"Erro no cliente: {erro}")
        break

sock.close()

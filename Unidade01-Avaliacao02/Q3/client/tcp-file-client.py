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
        sock.sendall(fileName.encode('utf-8'))

        # Recebe o tamanho do arquivo
        file_size_data = sock.recv(4)
        file_size = int.from_bytes(file_size_data, "big")

        if file_size == 0:
            print(f"Arquivo '{fileName}' não encontrado ou está vazio no servidor.")
            continue

        print(f"Tamanho do arquivo recebido: {file_size} bytes")
        print("Gravando arquivo localmente.")
        
        fd = open(os.path.join(DIRBASE, fileName), 'wb')
        try:
            file_received = 0
            while file_received < file_size:
                data = sock.recv(4096)
                if data == "":
                    break
                fd.write(data)
                file_received += len(data)
        finally:
            fd.close()

        print(f"Arquivo '{fileName}' gravado em '{DIRBASE}{fileName}'")

    except Exception as erro:
        print(f"Erro no cliente: {erro}")
        break

sock.close()

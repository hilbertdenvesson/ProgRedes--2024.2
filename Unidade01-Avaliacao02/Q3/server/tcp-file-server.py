import socket
import os

DIRBASE = "files/"
INTERFACE = '127.0.0.1'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((INTERFACE, PORT))
sock.listen(1)

sock.settimeout(60)

print("Servidor TCP escutando em ...", (INTERFACE, PORT))

while True:
    try:
        conn, addr = sock.accept()
        print("Conexão recebida de:", addr)

        # Recebe o nome do arquivo 
        fileName = conn.recv(512).decode('utf-8').strip()
        print("Pedido para o arquivo:", fileName)

        file_path = os.path.join(DIRBASE, fileName)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        else: 
            file_size = 0
        conn.sendall(file_size.to_bytes(4, 'big'))

        if file_size == 0:
            print(f"Arquivo '{fileName}' não encontrado.")
            conn.close()
            continue

        print("Enviando arquivo:", fileName)
        
        fd = open(file_path, 'rb')
        try:
            while True:
                fileData = fd.read(4096)
                if fileData == "":
                    break
                conn.sendall(fileData)
        finally:
            fd.close()

        print(f"Envio do arquivo '{fileName}' concluído.")
        conn.close()

    except Exception as erro:
        print(f"Erro no servidor: {erro}")
        break

sock.close()

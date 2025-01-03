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

        # Recebe o comprimento do nome do arquivo (2 bytes)
        fileNameLength = conn.recv(2)
        fileNameLength = int.from_bytes(fileNameLength, 'big')

        # Recebe o nome do arquivo
        fileName = conn.recv(fileNameLength).decode('utf-8').strip()
        print("Pedido para o arquivo:", fileName)

        file_path = os.path.join(DIRBASE, fileName)
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        else: 
            file_size = 0
        
        # Envia sinalizador e tamanho do arquivo
        if file_size > 0:
            conn.sendall(b'\x00\x00')  # Flag de sucesso
            conn.sendall(file_size.to_bytes(4, 'big'))  # Tamanho do arquivo
        else:
            conn.sendall(b'\x00\x01')  # Flag de erro (arquivo não encontrado)
            print(f"Arquivo '{fileName}' não encontrado.")
            conn.close()
            continue

        print("Enviando arquivo:", fileName)
        
        # Envia o conteúdo do arquivo
        fd = open(file_path, 'rb')
        tam = file_size
        while tam > 0:
            fileData = fd.read(4096)
            conn.sendall(fileData)
            tam -= len(fileData)
        fd.close()

        print(f"Envio do arquivo '{fileName}' concluído.")
        conn.close()

    except Exception as erro:
        print(f"Erro no servidor: {erro}")
        break

sock.close()


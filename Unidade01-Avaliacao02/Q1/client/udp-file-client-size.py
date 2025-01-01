import socket

DIRBASE = "files/"
SERVER = '127.0.0.1'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Evita travar no terminal
sock.settimeout(10)


while True:
    try:
        fileName = input("Arquivo a pedir ao servidor: ").strip()
        # Volta ao início do loop caso ele o usuário digite o nome vazio
        if fileName == "":
            print("Nome de arquivo vazio.")
            continue

        print("Enviando pedido ao servidor:", (SERVER, PORT), "para", fileName)
        sock.sendto(fileName.encode('utf-8'), (SERVER, PORT))  

        # Recebe o tamanho do arquivo
        data, source = sock.recvfrom(4)
        file_size = int.from_bytes(data, "big")

        # Volta ao início do loop caso ele o usuário digite o nome vazio
        if file_size == 0:
            print(f"Arquivo '{fileName}' não encontrado ou está vazio no servidor.")
            continue

        print(f"Tamanho do arquivo recebido: {file_size} bytes")
        print("Gravando arquivo localmente.")
        fd = open(DIRBASE + fileName, 'wb')
        
        file_received = 0
        while file_received < file_size:
            data, source = sock.recvfrom(4096)
            fd.write(data)  
            file_received += len(data)
            
            # Envia ACK para o servidor confirmando o recebimento
            sock.sendto(b'ACK', source) 
        
        fd.close()
        print(f"Arquivo '{fileName}' gravado em '{DIRBASE}{fileName}'")

    except Exception as erro:
        print(f"Erro no cliente: {erro}")
        break

sock.close()

import socket

DIRBASE = "files/"
SERVER = '127.0.0.1'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(10)

while True:
    try:
        fileName = input("Arquivo a pedir ao servidor: ").strip()  # Ignora espaços extras
        if fileName == "":
            print("Nome de arquivo vazio.")
            
        
        # Envia o nome do arquivo ao servidor
        print("Enviando pedido a", (SERVER, PORT), "para", fileName)
        sock.sendto(fileName.encode('utf-8'), (SERVER, PORT))

        # Recebe o tamanho do arquivo
        data, source = sock.recvfrom(4)
        file_size = int.from_bytes(data, "big")
        
        if file_size == 0:
            print("Arquivo não encontrado ou vazio no servidor.")
       
            

        print(f"Tamanho do arquivo recebido: {file_size} bytes")

        
        print("Gravando arquivo localmente")
        fd = open(DIRBASE + fileName, 'wb')
       
        file_received = 0
        while file_received < file_size:
            data, source = sock.recvfrom(4096)
            fd.write(data)
            file_received += len(data)
        
        fd.close()

        print(f"Arquivo '{fileName}' gravado")
    except Exception as erro:
        print(f"Erro: {erro}")

sock.close()

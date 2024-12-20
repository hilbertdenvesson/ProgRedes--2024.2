import socket

def tamanho_arquivo(nome_arquivo):
    fd = open(nome_arquivo, "rb")
    
    #Se posiciona no final do arquivo e retorna a posição
    fd.seek(0, 2)  
    tamanho_arquivo = fd.tell()
    
    tamanho_arquivo_4bytes = tamanho_arquivo.to_bytes(4, 'big')
    
    # Retorna a leitura ao início do arquivo
    fd.seek(0)  
    fd.close()  
    return tamanho_arquivo_4bytes

DIRBASE = "files/"
INTERFACE = '127.0.0.1'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((INTERFACE, PORT))
sock.settimeout(60)

print("Escutando em ...", (INTERFACE, PORT))

while True:
   
    # Recebe o nome do arquivo solicitado
    data, source = sock.recvfrom(512)
    fileName = data.decode('utf-8').strip()
    print("Pedido para o arquivo", fileName)
        
    # Tenta abrir o arquivo
    try:
        file_size = tamanho_arquivo(DIRBASE + fileName)
        sock.sendto(file_size, source)
        fd = open(DIRBASE + fileName, 'rb')
        print("Enviando arquivo", fileName)
         
        fileData = fd.read(4096)
        while fileData != b"":  
            sock.sendto(fileData, source)
            fileData = fd.read(4096)
    
        fd.close()
    
    except Exception as erro:
        print(f"Erro:{erro}")
        exit(0)

sock.close()

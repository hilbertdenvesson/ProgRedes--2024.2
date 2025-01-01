import socket

def tamanho_arquivo(nome_arquivo):
    try:
        fd = open(nome_arquivo, "rb")
        # Posiciona no final para verificar o tamanho
        fd.seek(0, 2)  
        tamanho_arquivo = fd.tell()
        tamanho_arquivo_4bytes = tamanho_arquivo.to_bytes(4, 'big')
        # Retorna ao início para futuras leituras
        fd.seek(0)  
        fd.close()
        return tamanho_arquivo_4bytes
    except FileNotFoundError:
        # Retorna 0 se o arquivo não for encontrado
        return (0).to_bytes(4, 'big') 

DIRBASE = "files/"
INTERFACE = '127.0.0.1'
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((INTERFACE, PORT))

# Evita travar no terminal
sock.settimeout(60)


print("Escutando em ...", (INTERFACE, PORT))

while True:
    try:
        # Recebe o nome do arquivo solicitado
        data, source = sock.recvfrom(512)
        fileName = data.decode('utf-8').strip()
        print("Pedido para o arquivo:", fileName)
        
        # Tenta abrir o arquivo e enviar o tamanho ao cliente
        file_path = DIRBASE + fileName
        file_size = tamanho_arquivo(file_path)
        sock.sendto(file_size, source) 
        
        if int.from_bytes(file_size, 'big') == 0:
            print(f"Arquivo '{fileName}' não encontrado.")
            continue  
            
        print("Enviando arquivo:", fileName)
        fd = open(file_path, 'rb')
        
        fileData = fd.read(4096)
        # Envia os dados do arquivo
        while fileData != b"":  
            sock.sendto(fileData, source) 
            # Aguarda a confirmação do cliente
            ack, source = sock.recvfrom(3)
            # Se não receber 'ACK', reenvia
            if ack != b'ACK': 
                print("ACK não recebido, tentando novamente.")
                # Retorna para a posição onde o envio falhou
                fd.seek(-len(fileData), 1)
            fileData = fd.read(4096)
        
        fd.close()
        print(f"Envio do arquivo '{fileName}' concluído.")
    
    except Exception as erro:
        print(f"Erro no servidor: {erro}")
        break

sock.close()

import socket, os
from threading import Thread


class WebServer:

    def __init__(self, address='develaraujo.com.br', port=6789):
        self.port = port
        self.address = address

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.address, self.port))
            s.listen(10)

            while True:
                print('Waiting connections...')
                conn, addr = s.accept()
                req = HttpRequest(conn, addr)
                req.start()


class HttpRequest(Thread):

    def __init__(self, conn, addr):
        super(HttpRequest, self).__init__()
        self.conn = conn
        self.addr = addr
        self.CRLF = '\r\n'
        self.buffer_size = 4096
        self.arquivos = ['index.html','main.js','mickey-mouse.png','pernalonga.jpeg','piupiu-e-frajola.png','tom-e-jerry.png']
        self.arquivosNotFound = ['notFound.html','not-found.js']

    def run(self):
        request = self.conn.recv(self.buffer_size)
        referer = list(filter(lambda x: 'GET' in x, request.decode("UTF-8").splitlines())) # Capta a url
        verificacao = False

        # Verifica os arquivos se estão no vetor de rotas
        for arquivo in self.arquivos:
            if(f'GET /{arquivo} HTTP/1.1' in referer[0]):
                print(referer[0])
                print('\r\n')
                response = HttpResponse(self.conn, self.addr, arquivo)
                response.processRespose()
                verificacao = True
                break

        # Caso não existir a rota retorna uma resposta ao usuario
        if(verificacao == False):
            response = HttpResponse(self.conn, self.addr, self.arquivosNotFound[0])
            response.processRespose()

        self.conn.close()


class HttpResponse:

    def __init__(self, conn, addr, file):
        self.conn = conn
        self.addr = addr
        self.file = file

    def processRespose(self):
        arquivoHTML = open(self.file,'rb')
        self.conn.sendall('HTTP/1.0 200 OK\r\n'.encode('utf-8'))

        if(self.file.endswith('js')):
            self.conn.sendall('Content-Type: text/javascript\r\n\r'.encode('utf-8'))
        elif(self.file.endswith('html')):
            self.conn.sendall('Content-Type: text/html\r\n\r'.encode('utf-8'))
        elif(self.file.endswith('png')):
            tamanho = os.fstat(arquivoHTML.fileno()).st_size
            self.conn.send('Content-Type: image/png\r\n\r'.encode('utf-8'))
            self.conn.send(f'Content-Length: {tamanho}\r\n'.encode('utf-8'))
        elif(self.file.endswith('jpeg')):
            tamanho = os.fstat(arquivoHTML.fileno()).st_size
            self.conn.send('Content-Type: image/jpeg\r\n\r'.encode('utf-8'))
            self.conn.send(f'Content-Length: {tamanho}\r\n'.encode('utf-8'))

        self.conn.sendall((f'Location: http://{self.addr[0]}:6789/{self.file}\r\n').encode('utf-8'))
        self.conn.send(('\r\n').encode('utf-8'))

        for linha in arquivoHTML.readlines():
            self.conn.sendall(linha)

        arquivoHTML.close()
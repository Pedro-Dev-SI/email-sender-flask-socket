from flask import Flask, request, render_template, redirect
from socket import *
import ssl
import base64

app = Flask(__name__, template_folder='template')

bufferSize = 2048

def createAuthCommand(user: str, password: str):
  str = "\x00"+user+"\x00"+password
  base64_str = base64.b64encode(str.encode())
  return "AUTH PLAIN " + base64_str.decode()

def createSocketConnectEmailServer(emailServer, port):
    #Criando um objeto tipo socket utilizando endereços IPV4(AF_INET) e usando o protocolo TCP (SOCK_STREAM)
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(5)
    clientSocket = ssl.wrap_socket(s)
    #Conectando o socket ao servidor de email baseado nos dados de servidor e porta preenchidos no formulário
    clientSocket.connect((emailServer, port))
    return clientSocket

def receiveMessage(clientSocket):
  try:
    return clientSocket.recv(bufferSize).decode()
  except timeout:
    pass

def sendCommand(clientSocket, command, expect_return_msg=True):
    clientSocket.send(f"{command}\r\n".encode())
    if expect_return_msg:
        recv = receiveMessage(clientSocket)
        print(recv)
        return recv
    
def login(clientSocket, user, password):
    authCmd = createAuthCommand(user, password)
    sendCommand(clientSocket, authCmd)

# Rotas
@app.route('/')
def form():
    return render_template('form.html')

@app.route('/send', methods=['POST'])
def sendEmail():
    emailServer = request.form['server']
    port = request.form['port']
    sender = request.form['sender']
    receiver = request.form['receiver']
    subject = request.form['subject']
    password = request.form['password']
    body = request.form['body']
    
    print(emailServer)
    print(port)
    print(sender)
    print(receiver)
    print(subject)
    print(password)
    print(body)
    #Criando um objeto socket e conectando ao servidor de email informado no formulário.
    clientSocket = createSocketConnectEmailServer(emailServer, int(port))
    
    #ehlo
    sendCommand(clientSocket, "ehlo Pedro")
    
    #Realizando o login no servidor de email
    login(clientSocket, sender, password)
    
    #Enviando comandos SMTP para realizar o envio do email.
    sendCommand(clientSocket, f"MAIL FROM:<{sender}>")
    sendCommand(clientSocket, f"RCPT TO: <{receiver}>")
    sendCommand(clientSocket, f"DATA")
    sendCommand(clientSocket, f"SUBJECT: {subject}\r\n", expect_return_msg=False)
    sendCommand(clientSocket, body, expect_return_msg=False)
    sendCommand(clientSocket, ".")
    
    sendCommand(clientSocket, "QUIT")
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
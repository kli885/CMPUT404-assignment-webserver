#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.headers = self.data.decode().split("\r\n")
        self.method = self.headers[0].split(' ')[0]
        self.path = self.headers[0].split(' ')[1]

        for header in self.headers:
            if "Host" in header:
                self.host = header.split(": ")[1]
                break

        self.path = "./www" + self.path

        self.request.sendall(self.status_handler().encode())
    
    def status_handler(self):
        if self.method == "GET":
            if os.path.isdir(self.path) and not self.path.endswith('/'):
                return "HTTP/1.1 301 Moved Permanently\r\n\r\nLocation: http://{}{}/\r\n".format(self.host, self.path.split('/',2)[2])
            if self.path.endswith('/'):
                self.path += "index.html"
            try:
                if ".." in self.path:
                    raise FileNotFoundError
                with open(self.path, 'r') as file:
                    return "HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n{}\r\n".format(self.get_mime_type(), file.read())
            except:
                return "HTTP/1.1 404 Not Found\r\n\r\nConnection: Closed\r\n"
        else:
            return "HTTP/1.1 405 Method not allowed\r\n"
    
    def get_mime_type(self):
        if self.path.endswith('.html'):
            return "text/html"
        elif self.path.endswith('.css'):
            return "text/css"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

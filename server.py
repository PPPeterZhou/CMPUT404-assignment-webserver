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
        self.root = os.path.abspath(".")
        
        method = self.get_method(self.data)
        file_name = self.get_file_name(self.data)
        path = os.path.abspath("www") + file_name
        file_type = self.get_file_type(self.data, path)

        # check the method
        if method != "GET":
            response = self.code405(method, file_type)

        else:
            # handle get root
            if path.endswith("/"):
                path += "index.html"
                file_type = "html"
        
            try:
                file = open(path, 'r')
            
            except FileNotFoundError:
                response = self.code404(file_type)

            except IsADirectoryError:
                response = self.code301(file_type)

            else:
                response = self.code200(file_type, file)

            if file_type == "Invalid Type":
                response = self.code404(file_type)
            
        self.request.sendall(bytearray(response,'utf-8'))
        return

    def code301(self, file_type):
        response_start_line = "HTTP/1.1 301 Moved Permanently"
        response_headers = "Content-Type: text/{}\n".format(file_type)
        response_body = "Redirected!"
        return (response_start_line + response_headers + response_body)

    def code405(self, method, file_type):
        response_start_line = "HTTP/1.1 405 Method Not Allowed"
        response_headers = "Content-Type: text/{}\n".format(file_type)
        response_body = '"{}" Method Not Allowed'.format(method)
        return (response_start_line + response_headers + response_body)
    
    def code200(self, file_type, file):
        file_data = file.read()
        file.close()
        response_start_line = "HTTP/1.1 200 OK Not FOUND!\n"
        response_headers = "Content-Type: text/{}\n".format(file_type)
        response_body = file_data
        return (response_start_line + response_headers + response_body)
    
    def code404(self, file_type):
        response_start_line = "HTTP/1.1 404 Not FOUND!\n"  
        response_headers = "Content-Type: text/{}\n".format(file_type)
        response_body = "File Not Found!"
        return (response_start_line + response_headers + response_body)

    def get_request_url(self, data):
        return data.splitlines()[0].decode("utf-8")

    def get_file_name(self, data):
        return data.splitlines()[0].decode("utf-8").split()[1]

    def get_method(self, data):
        return data.splitlines()[0].decode("utf-8").split()[0]

    def get_file_type(self, data, path):
        type_data = data.splitlines()[0].decode("utf-8").split()[1]
        temp_path = path + "/"
        if os.path.isdir(temp_path):
            path += "/"
            return "Directory"
        if "/" == type_data:
            return "Root"
        if type_data.endswith("/"):
            return "Directory"
        if "." not in type_data.split("/")[-1]:
            return "Invalid Type"
        if "." in type_data:
            return type_data.split(".")[1]
        return "Invalid Type"

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

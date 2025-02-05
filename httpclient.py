#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Chase Warwick
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

# Do not use urllib"s HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    def __repr__(self):
        return f"Status Code: {self.code}\nResponse Body:\n{self.body}"


class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split("\r\n")[0].split(" ")[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data[data.find("\r\n\r\n"):]
    
    def is_remote_IP(self, url):
        url = url.strip("https://")
        url = url.strip("http://")
        url = url[:url.find("/")]
        for char in url:
            if char.isalpha():
                return False
        return True

    def get_host(self, url):
        netloc = urllib.parse.urlparse(url).netloc
        if self.is_remote_IP(url):
            return netloc[:netloc.find(":")]
        return netloc
        

    def get_port(self, url):
        netloc = urllib.parse.urlparse(url).netloc
        if self.is_remote_IP(url):
            return int(netloc[netloc.find(":")+1:])
        return 80
    
    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        host = self.get_host(url)
        port = self.get_port(url)
        path = urllib.parse.urlparse(url).path

        if path == "":
            path = "/"

        payload = (
            f"GET {path} HTTP/1.0\r\n" + 
            f"Host: {host}\r\n" + 
            f"Accept: */*\r\n" +
            f"Accept-Charset: UTF-8\r\n\r\n")
        self.connect(host, port)
        self.sendall(payload)
        
        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        
        host = self.get_host(url)
        port = self.get_port(url)
        path = urllib.parse.urlparse(url).path

        if path == "":
            path = "/"

        self.connect(host, port)

        body = ""
        if args:
            for i,key in enumerate(args):
                body_addition = f"{key}={args[key]}"
                if not (i == len(args)-1):
                    body_addition += "&"
                body += body_addition
        
        content_length = len(body.encode('utf-8'))
        
        payload = (
            f"POST {path} HTTP/1.0\r\nHost: {host}\r\n" +
            f"Accept: */*\r\n"
            f"Accept-Charset: UTF-8\r\n"
            f"Content-type: application/x-www-form-urlencoded\r\n" +
            f"Content-length: {content_length}\r\n\r\n{body}"
        )

        self.sendall(payload)
        
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
            
def main():
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

if __name__ == "__main__":
    main()

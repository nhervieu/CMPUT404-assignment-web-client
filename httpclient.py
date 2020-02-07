#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
	print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
	def __init__(self, code=200, body=""):
		self.code = code
		self.body = body

class HTTPClient(object):
	#def get_host_port(self,url):

	def connect(self, host, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("host: ", host)
		print("port: ", port)
		self.socket.connect((host, port))
		self.socket.send(b'')
		return None

	def get_code(self, data):
		return None

	def get_headers(self,data):
		return None

	def get_body(self, data):
		return None

	def parse_result(self,data):
		m = re.search("HTTP\/1\.[10] ([0-9]{3})[ A-Za-z]+(.*)",data,re.DOTALL)
		code = int(m.group(1))

		m = re.search("\r\n({.*})",data)
		if m:
			data = m.group(1)

		if code == 404:
			return code, "File not Found"
		else:
			return code, data

	def url_cleanup(self, url):
		if url[0:3] == 'www':
			return "http://" + url
		elif url[0:4] != "http":
			return "https://www." + url
		else:
			return url

	#return host, port, 
	def url_parse(self, url):
		port = 80
		if not url.netloc:
			return url.path, port
		else: 
			host_given = url.netloc.find(":")
			if host_given != -1:
				host = url.netloc[:host_given]
				port = int(url.netloc[host_given+1:])
				return host, port
			else:
				return url.netloc, port


	def sendall(self, data, port, host, args=None, request='GET '):
		header = ''

		#print("ARGS: " , args)
		query = ''

		if args != None:
			for key in args:
				value = args[key].replace("\r","%0D")
				value = value.replace("\n","%0A")
				value = value.replace(" ", "+")

				query = query + key + "=" + value+"&"
		print(query)

		path = data.path

		if request == "GET ":
			
			if not data.netloc:
				path = data.params#+data.query+data.fragment
			else:
				path = data.path#+data.params+data.query+data.fragment

			if path == "/" or path == "":
				header = 'GET / HTTP/1.0\r\nHost: '+host+'\r\n\r\n'
			else:
				header = 'GET '+path+' HTTP/1.0\r\nHost: '+host+'\r\n\r\n'


		elif request == "POST ":

			if not data.netloc:
				path = data.params#+data.query+data.fragment
			else:
				path = data.path+data.params#+data.query+data.fragment

			body = query[:-1]
			length = str(len(body.encode('utf-8')))

			if path == "/" or path == "":
				#header = 'POST / HTTP/1.0\r\nHost: '+host+'\r\n\r\n'
				header = 'POST ' + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ length + "\r\n\r\n" + body

			else:
				#header = 'POST '+path+' HTTP/1.0\r\nHost: '+host+'\r\n\r\n'
				header = 'POST ' + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ length + "\r\n\r\n" + body


			#header = 'POST ' + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ length + "\r\n\r\n" + body


			# if data.query != "":
			# 	header = request + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-Length: "+ str(len(data.query)) + "\r\n\r\n" + data.query+ "\r\n\r\n"
			# elif args != None:
			# 	header = request + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ str(len(query)-1) + "\r\n\r\n" + query[:-1]
			# else:
			# 	header = request + path + " HTTP/1.0\r\nHost: " + host  + "\r\n" + "Content-Length: "+ "0" +"\r\n\r\n"

		print("my post request: ")
		print(header)
		self.socket.sendall(header.encode('utf-8'))

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

		return buffer.decode('utf-8')

	def GET(self, url, args=None):
		port = 80
		host = ""

		url = self.url_cleanup(url)
		#print(url)

		url = urlparse(url)
		#print(url)

		host, port = self.url_parse(url)
		self.connect(host, port)

		self.sendall(url,port,host, args, "GET ")

		data = self.recvall(self.socket)

		#print result of request to stdout
		print(data)

		self.close()

		code, body = self.parse_result(data)

		
		return HTTPResponse(code, body)

	def POST(self, url, args=None):
		port = 80
		host = ""

		url = self.url_cleanup(url)

		url = urlparse(url)

		host, port = self.url_parse(url)
		self.connect(host, port)

		self.sendall(url,port,host,args, "POST ")

		data = self.recvall(self.socket)

		#print result of request to stdout
		print(data)

		self.close()

		code, body = self.parse_result(data)


		
		return HTTPResponse(code, body)

	def command(self, url, command='get', args=None):
		if (command.upper() == "POST"):
			return self.POST( url, args )
		else:
			return self.GET( url, args )

if __name__ == "__main__":
	client = HTTPClient()
	command = "GET"
	if (len(sys.argv) <= 1):
		help()
		sys.exit(1)
	elif (len(sys.argv) == 3):
		print(client.command( sys.argv[2], sys.argv[1] ))

	else:
		print(client.command( sys.argv[1] ))


# http://c2.com/cgi/wiki?CommonLispHyperSpec
# ParseResult(scheme='http', netloc='c2.com', path='/cgi/wiki', params='', query='CommonLispHyperSpec', fragment='')
# host:  c2.com
# port:  80
# my post request: 
# GET /cgi/wiki HTTP/1.0
# Host: c2.com

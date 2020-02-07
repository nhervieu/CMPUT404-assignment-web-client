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



#updated httpclient.py file done by Natalie Hervieux (ccid: nhervieu) in Feb 2020


import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
	#Remind user of correct input format
	print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
	#To return HTTPResponse object
	def __init__(self, code=200, body=""):
		self.code = code
		self.body = body

class HTTPClient(object):
	#def get_host_port(self,url):

	def connect(self, host, port):
		# connect to the host
		# if no port is given in input, it will default to 80
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((host, port))
		return None

	def get_code(self, data):
		return None

	def get_headers(self,data):
		return None

	def get_body(self, data):
		return None

	def parse_result(self,data):

		#parse the HTTP Response for the response code
		m = re.search("HTTP\/1\.[10] ([0-9]{3})[ A-Za-z]+(.*)",data,re.DOTALL)
		code = int(m.group(1))

		#parse the HTTP response for the body of a post (if in json format)
		#return the body for a post instead of whole response
		m = re.search("\r\n({.*})",data)
		if m:
			data = m.group(1)

		# if 404 error, we return file not found and ignore rest of response
		if code == 404:
			return code, "File not Found"
		# else return entire response
		else:
			return code, data
		

	#adds http and/or www to input url if missing
	def url_cleanup(self, url):
		if url[0:3] == 'www':
			return "http://" + url
		elif url[0:4] != "http":
			return "https://www." + url
		else:
			return url

	#parses url and returns host and port
	def url_parse(self, url):
		
		#defaul to port 80 if none given
		port = 80

		if not url.netloc:
			return url.path, port
		else: 
			#if the port is given, we replace default
			host_given = url.netloc.find(":")
			if host_given != -1:
				host = url.netloc[:host_given]
				port = int(url.netloc[host_given+1:])
				return host, port
			else:
				return url.netloc, port


	#create request header and send
	def sendall(self, data, port, host, args=None, request='GET '):
		header = ''
		query = ''
		path = data.path

		#put arguments in correct format for Content-type: application/x-www-form-urlencoded
		if args != None:
			for key in args:
				value = args[key].replace("\r","%0D")
				value = value.replace("\n","%0A")
				value = value.replace(" ", "+")
				query = query + key + "=" + value+"&"


		#find full path for first line of request header
		if not data.netloc:
			path = data.params
		else:
			path = data.path+data.params


		#handle get request
		if request == "GET ":
			if path == "/" or path == "":
				header = 'GET / HTTP/1.0\r\nHost: '+host+'\r\n\r\n'
			else:
				header = 'GET '+path+' HTTP/1.0\r\nHost: '+host+'\r\n\r\n'


		#handle post request
		elif request == "POST ":
			body = query[:-1] #remove extra &
			length = str(len(body.encode('utf-8')))

			if path == "/" or path == "":
				header = "POST / HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ length + "\r\n\r\n" + body
			#elif data.query != "" and args == None:
				#header = 'POST ' + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ str(len(data.query.encode('utf-8'))) + "\r\n\r\n" + data.query
			else:
				header = 'POST ' + path + " HTTP/1.0\r\nHost: " + host + "\r\n" +"Content-type: application/x-www-form-urlencoded" + "\r\n" +"Content-Length: "+ length + "\r\n\r\n" + body

		self.socket.sendall(header.encode('utf-8'))

	def close(self):
		#close the connection
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

	#handle protocol for get request
	def GET(self, url, args=None):
		port = 80
		host = ""

		#parse input to get url, open connection with host
		url = self.url_cleanup(url)
		url = urlparse(url)
		host, port = self.url_parse(url)
		self.connect(host, port)

		#Create get request and send
		self.sendall(url,port,host, args, "GET ")

		#Collect data returned from host
		data = self.recvall(self.socket)

		#print the full result of request to stdout
		print(data)

		#close the connection
		self.close()

		# Parse the result to get the code and body and return them
		code, body = self.parse_result(data)
		return HTTPResponse(code, body)

	#handle protocol for post request
	def POST(self, url, args=None):
		port = 80
		host = ""

		#parse input to get url, open connection with host
		url = self.url_cleanup(url)
		url = urlparse(url)
		host, port = self.url_parse(url)
		self.connect(host, port)

		#Create get request and send
		self.sendall(url,port,host,args, "POST ")

		#Collect data returned from host
		data = self.recvall(self.socket)

		#print result of request to stdout
		print(data)

		#close the connection
		self.close()

		# Parse the result to get the code and body and return them
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
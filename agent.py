import threading, Queue
from datetime import datetime


class Agent(threading.Threading):
	def __init__(self, name, opt, message_server, auctioneer):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.message_queue = Queue.Queue()
		self.message_server = message_server
		self.terminate = False
		self.auctioneer = auctioneer
		self.name = name
		
	
	def run(self):
		while not self.terminate:
			self.read_message()
			self.process()
	
	def recieve(self, sender, content):
		self.message_queue.put((sender, content))
	
	def send(self, reciever, content):
		self.message_server.send((self.name, reciever, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

	def read_message(self):
		while not self.message_queue.empty():
			pass

	def process(self):
		pass
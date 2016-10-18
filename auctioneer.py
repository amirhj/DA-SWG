import threading, Queue
from datetime import datetime


class Auctioneer(threading.Threading):
	def __init__(self, opt, message_server, agents):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.message_queue = Queue.Queue()
		self.message_server = message_server
		self.terminate = False
		self.agents = agents
		
	
	def run(self):
		while not self.terminate:
			pass
	
	def recieve(self, sender, content):
		self.message_queue.put((sender, content))
	
	def send(self, reciever, content):
		self.message_server.send((self.name, reciever, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
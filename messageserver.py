import threading, Queue


class MessageServer(threading.Threading):
	def __init__(self):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.message_queue = Queue.Queue()
		self.opt = opt
		self.clients = None
		self.scheduler = scheduler
		self.log = []
		self.terminate = False
	
	def load(self, clients):
		self.clients = clients
		
	def run(self):
		while not self.terminate:
			while self.message_queue.empty():
				pass
			m = self.message_queue.get()
			self.log.append(m)
			self.clients[receiver].receive(m[0], m[2]) # 0:sender, 2:content
	
	def send(self, sender, receiver, content, sendtime):
		self.message_queue.put((sender, receiver, content, sendtime))
import threading, Queue
from datetime import datetime


class Auctioneer(threading.Threading):
	def __init__(self, grid, message_server, opt):
		threading.Thread.__init__(self)
		self.setDaemon(True)

		self.message_server = message_server
		self.opt = opt
		self.grid = grid

		self.message_queue = Queue.Queue()
		self.message_types = {'submission': {}}
		self.terminate = False
		self.state = ('phase1', 'send-request')

	
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
			sender, m = self.message_queue.get()
			self.message_types[m['type']][sender] = m['content']


	def process(self):
		if self.state[0] == 'phase1':
			if self.state[1] == 'send-request':
				for s in self.grid.sellers:
					self.send(s, {'type':'submission'})
				for b in self.grid.buyers:
					self.send(b, {'type':'submission'})
				self.state[1] = 'wait-response'
			elif self.state[1] == 'wait-response':
				all_responses = True
				for m in self.message_types['submission']:
					if (m not in self.grid.sellers) or (m not in self.grid.buyers):
						all_responses = False
						break
				if all_responses:
					self.run_phase1()

	def run_phase1(self):
		pass
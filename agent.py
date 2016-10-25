import threading, Queue
from datetime import datetime


class Agent(threading.Thread):
	def __init__(self, name, grid, message_server, opt):
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.message_queue = Queue.Queue()
		self.message_server = message_server
		self.terminate = False
		self.opt = opt
		self.grid = grid
		self.name = name

		self.proposal = None
		if self.grid.agents[self.name]['is_seller']:
			self.proposal = {'price':self.grid.agents[self.name]['price'], 'amount':self.grid.agents[self.name]['max_delivery']}
		else:
			self.proposal = {'price':self.grid.agents[self.name]['bid'], 'amount':self.grid.agents[self.name]['max_demand']}
		
	
	def run(self):
		while not self.terminate:
			self.read_message()
	def receive(self, sender, content):
		self.message_queue.put((sender, content))
	
	def send(self, receiver, content):
		self.message_server.send(self.name, receiver, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

	def read_message(self):
		while not self.message_queue.empty():
			sender, m = self.message_queue.get()
			if sender == 'auctioneer':
				if m['type'] == 'submission':
					self.send('auctioneer', {'type':'submission', 'content':self.proposal})
				elif m['type'] == 'result':
					self.update_proposal(m['content']['price'], m['content']['others-actions'])
				elif m['type'] == 'price':
					pass #self.calculate_utility(m['content'])
				elif m['type'] == 'out':
					pass #self.calculate_utility(m['content'])
				else:
					raise Exception('Invalid message type ' + m['type'])
			else:
				raise Exception('Invalid sender '+ sender)

	def update_proposal(self, price, actions):
		pass

	def calculate_utility(self, price):
		pass

class Scheduler:
	def __init__(self, grid, agents, auctioneer, message_server, opt):
		self.grid = grid
		self.agents = agents
		self.auctioneer = auctioneer
		self.opt = opt
		self.message_server = message_server

	def initialize(self):
		clients = {a:self.agents[a] for a in self.agents}
		clients['auctioneer'] = auctioneer
		self.message_server.load(clients)
		self.message_server.start()

		for a in self.agents:
			self.agents[a].start()

		self.auctioneer.start()

	def run(self):
		terminate = False
		while not terminate:
			terminate = True
			for a in self.agents:
				if not self.agents[a].converged:
					terminate = False
					break

		for a in self.agents:
			self.agents[a].terminate = True
			self.agents[a].join()

		self.auctioneer.terminate = True
		self.auctioneer.join()
		self.message_server.terminate = True
		self.message_server.join()
	
	def terminate(self):
		pass
class Grid:
	def __init__(self, inputFile, opt):
		self.grid = inputFile
		self.agents = {}
		self.sellers = []
		self.buyers = []
		self.transfer_cost = {}
		self.inf = float('inf')
		self.opt = opt

		for a in self.grid['agents']:
			self.agents[a['id']] = a
			self.agents[a['id']]['is_seller'] = False
			self.agents[a['id']]['is_buyer'] = False
			self.agents[a['id']]['sellers'] = set()
			self.agents[a['id']]['buyers'] = set()

		for s in self.grid['sellers']:
			self.sellers.append(s)
			self.agents[s]['is_seller'] = True
			self.agents[s]['price'] = self.grid['sellers'][s]['price']
			self.agents[s]['max_delivery'] = self.grid['sellers'][s]['max_delivery']

		for b in self.grid['buyers']:
			self.buyers.append(b)
			self.agents[b]['is_buyer'] = True
			self.agents[b]['bid'] = self.grid['buyers'][b]['price']
			self.agents[b]['max_demand'] = self.grid['buyers'][b]['max_demand']
			self.agents[b]['amplitude'] = tuple(self.grid['buyers'][b]['amplitude'])

		for c in self.grid['transfer_cost']:
			self.transfer_cost[(c['from'], c['to'])] = c['cost']
			self.agents[c['from']]['buyers'].add(c['to'])
			self.agents[c['to']]['sellers'].add(c['from'])

	def get_transfer_cost(self, seller, buyer):
		cost = self.inf
		if (seller, buyer) in self.transfer_cost:
			cost = self.transfer_cost[(seller, buyer)]
		return cost

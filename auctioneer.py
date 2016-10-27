import threading, Queue
from datetime import datetime
from util import PipeQueue


class Auctioneer(threading.Thread):
	def __init__(self, grid, message_server, opt):
		threading.Thread.__init__(self)
		self.setDaemon(True)

		self.message_server = message_server
		self.opt = opt
		self.grid = grid

		self.message_queue = Queue.Queue()
		self.message_types = {'submission': {}}
		self.terminate = False
		self.state = ['phase1', 'send-request']
		self.sellers_prices = {s:PipeQueue(self.opt['convergence_size']) for s in self.grid.sellers}

		self.name = 'auctioneer'
		self.converged = False

	
	def run(self):
		while not self.terminate:
			self.read_message()
			self.process()
	
	def receive(self, sender, content):
		self.message_queue.put((sender, content))
	
	def send(self, receiver, content):
		self.message_server.send(self.name, receiver, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
				for m in self.grid.sellers:
					if m not in self.message_types['submission']:
						all_responses = False
						break
				if all_responses:
					for m in self.grid.buyers:
						if m not in self.message_types['submission']:
							all_responses = False
							break
				if all_responses:
					self.run_phase1()
		elif self.state[0] == 'phase2':
			self.run_phase2()

	def run_phase1(self):
		# sorting sellers increasing
		sellers = []
		for s in self.grid.sellers:
			m = self.message_types['submission'][s]
			c = {'agents': [s], 'price':m['price'], 'amount': m['amount']}
			inserted = False
			i = 0
			while i < len(sellers) and not inserted:
				if sellers[i]['price'] == c['price']:
					sellers[i]['agents'].append(c['agents'][0])
					sellers[i]['amount'] += c['amount']
					inserted = True
				elif sellers[i]['price'] > c['price']:
					sellers.insert(i, c)
					inserted = True
				i += 1
			if not inserted:
				sellers.append(c)

			self.sellers_prices[s].push(m['price'])

		# sorting buyers decreasing
		buyers = []
		for b in self.grid.buyers:
			m = self.message_types['submission'][b]
			c = {'agents': [b], 'price':m['price'], 'amount': m['amount']}
			inserted = False
			i = 0
			while i < len(buyers) and not inserted:
				if buyers[i]['price'] == c['price']:
					buyers[i]['agents'].append(c['agents'][0])
					buyers[i]['amount'] += c['amount']
					inserted = True
				elif buyers[i]['price'] < c['price']:
					buyers.insert(i, c)
					inserted = True
				i += 1
			if not inserted:
				buyers.append(c)

		# making sellers rectangles
		startx = 0
		starty = 0
		for s in sellers:
			endx = s['amount'] + startx
			s['amount'] = (startx, endx)
			startx = endx

			endy = s['price'] + starty
			s['price'] = (starty, endy)
			startx = endy

		# making buyers rectangles
		startx = 0
		for b in buyers:
			endx = b['amount'] + startx
			b['amount'] = (startx, endx)
			startx = endx

		buyers.reverse()
		endy = 0
		for b in buyers:
			starty = b['price'] + endy
			b['price'] = (starty, endy)
			endy = starty
		buyers.reverse()

		# finding intersection point
		maxs = None
		maxb = None
		for i in range(len(sellers)):
			found = False
			s = sellers[i]
			for j in range(len(buyers)):
				b = buyers[j]
				if (s['price'][0] <= b['price'][0] and s['price'][1] >= b['price'][0]) or (b['price'][0] <= s['price'][0] and b['price'][1] >= s['price'][0]):
					if (s['amount'][0] <= b['amount'][0] and s['amount'][1] >= b['amount'][0]) or (b['amount'[0]] <= s['amount'][0] and b['amount'][1] >= s['amount'][0]):
						found = True
						maxb = j
						break
			if found:
				maxs = i
				break

		# calculating price
		s = self.message_types['submission'][sellers[maxs]['agents'][0]]
		b = self.message_types['submission'][sellers[maxb]['agents'][0]]
		price = (s['price'] + b['price']) / 2

		if maxs > 0:
			maxs -= 1
		if maxb > 0:
			maxb -= 1

		# identifing in auction sellers
		in_sellers = []
		for i in range(maxs+1):
			for s in sellers[i]['agents']:
				in_sellers.append(s)

		# identifing in auction buyers
		in_buyers = []
		for i in range(maxb+1):
			for b in buyers[i]['agents']:
				in_buyers.append(b)

		# identifing out of auction sellers
		out_sellers = []
		i = maxs+1
		while i < len(sellers):
			for s in sellers[i]['agents']:
				out_sellers.append(s)
			i += 1

		# identifing out of auction buyers
		out_buyers = []
		i = maxb+1
		while i < len(buyers):
			for b in buyers[i]['agents']:
				out_buyers.append(b)
			i += 1

		# sending calculated price and actions of other sellers to participating sellers
		for s in in_sellers:
			actions = {a:self.message_types['submission'][s]['amount'] for a in self.grid.sellers}
			del actions[s]
			self.send(s, {'type':'result', 'content': {'price':price, 'others-actions':actions, 'in_sellers':in_sellers, 'in_buyers':in_buyers}})

		# sending calculated price to participating buyers
		for b in in_buyers:
			self.send(b, {'type':'price', 'content': {'price':price, 'in_sellers':in_sellers, 'in_buyers':in_buyers}})

		# sending other sellers that they are out of auction
		for s in out_sellers:
			actions = {a:self.message_types['submission'][s]['amount'] for a in self.grid.sellers}
			del actions[s]
			self.send(s, {'type':'out', 'content': {'price':price, 'others-actions':actions, 'in_sellers':in_sellers, 'in_buyers':in_buyers}})

		# sending other buyers that they are out of auction
		for b in out_buyers:
			self.send(b, {'type':'out', 'content': {'price':price, 'in_sellers':in_sellers, 'in_buyers':in_buyers}})

		# checking convergence
		converged = True
		for s in self.sellers_prices:
			if self.sellers_prices[s].is_full():
				if self.sellers_prices[s].get_standard_deviation() > self.opt['standard_deviation']:
					converged = False
					break
			else:
				converged = False
				break

		# decision how to progress
		if converged:
			self.state = ['phase2']
			self.converged = True
		else:
			self.state = ['phase1', 'send-request']
			self.message_types['submission'] = {}
	
	def run_phase2(self):
		pass



import sys, json
from argparser import ArgParser
from grid import grid
from Scheduler import scheduler
from agent import Agent
from auctioneer import Auctioneer
from messageserver import MessageServer

opt_pattern = {'-e': {'name': 'episodes', 'type': 'int', 'default': 200},
               '--alpha': {'name': 'alpha', 'type': 'float', 'default': 0.9},
               '--gamma': {'name': 'gamma', 'type': 'float', 'default': 0.8},
               '--epsilon': {'name': 'epsilon', 'type': 'float', 'default': 0.09},
               '--temperature': {'name': 'temperature', 'type': 'float', 'default': 0.9},
               '--landa': {'name': 'landa', 'type': 'int', 'default': 1},
               '-T': {'name': 'timeout', 'type': 'int', 'default': 200},
               '-t': {'name': 'tests', 'type': 'int', 'default': 20},
               '-a': {'name': 'auto_lines', 'type': 'bool', 'default': False},
               '-d': {'name': 'debug_level', 'type': 'int', 'default': 1},
               '-r': {'name': 'random_init', 'type': 'bool', 'default': False}
               }
arg = ArgParser(sys.argv[2:], opt_pattern)
opt = arg.read()

grid = Grid(json.open(sys.argv[1], 'r'), opt)

messageserver = MessageServer()
auctioneer = Auctioneer(grid, messageserver, opt)

agents = {}
for a in grid.agents:
	agent = Agent(a, grid, messageserver, opt)
	agents[a] = agent

scheduler = Scheduler(grid, agents, auctioneer, messageserver, opt)

scheduler.initialize()
scheduler.run()
scheduler.terminate()
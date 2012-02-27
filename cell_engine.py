from __future__ import print_function
#  
#  Copyright (c) 2012 Edward Langley
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#  
#  Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#  
#  Redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the following disclaimer in the
#  documentation and/or other materials provided with the distribution.
#  
#  Neither the name of the project's author nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  
#  

import time
import random
import pygame
import sys
import collections
import game

import collections

############### Cell ################
class Cell(game.Cell):
	pass

Cell.add_rule(3)(0)
Cell.add_rule(2)(3)

@Cell.add_rule(1)
def hook_1(cell):
	neighbors = [c and c.value for c in cell.neighbors]
	neighbor_value = cell.neighbor_value()
	rnd = random.random()
	if 2 in neighbors or 3 in neighbors:
		if rnd < .62 * neighbor_value/2: return 2

	else:
		if rnd < .01 * neighbor_value:
			return 0

@Cell.add_rule(0)
def hook_0(cell):
	neighbor_value = cell.neighbor_value()
	if neighbor_value != 0:
		nearby_fire = set([2,3]) & set(c and c.value for c in cell.neighbors)
		if nearby_fire == set() and random.random() < .02 * neighbor_value:
			return 1
	return cell.value

########## End Cell #################

class Presence(game.Presence):
	def act(self):
		value = int(round( (self.locale.neighbor_value() + self.locale.value) ))
		self.locale.set_value(0)
		for x in self.locale.neighbors:
			if not x: continue
			if x.value == 1:
				x.set_value(2)

import time

if __name__ == '__main__':
	pygame.init()
	pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
	pygame.display.set_caption('Simulator')

	board = game.Board(120, 120)
	window = pygame.display.set_mode(board.rect.size, pygame.DOUBLEBUF)
	window.set_alpha(None)
	for sprite in board.board_group:
		sprite.image.convert()

	a = game.Controller(board)

	p = a.add_observer(Presence, a.board.init.south)
	np = a.board.init.southeast
	for x in range(20):
		np = np.east
	np = a.add_observer(Presence, np)

	window.fill( (64,64,64) )

	running = True

	board.board_group.draw(window)
	pygame.display.flip()

	clck = pygame.time.Clock()

	paused = True
	while running:
		clck.tick(80)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running=False
				break
			elif event.type == pygame.KEYDOWN and event.unicode == 'e':
				paused = not paused
			elif event.type == pygame.KEYDOWN and event.unicode == 'w':
				new = p.locale.north
				if new:
					p.locale = new
			elif event.type == pygame.KEYDOWN and event.unicode == 'a':
				new = p.locale.west
				if new:
					p.locale = new
			elif event.type == pygame.KEYDOWN and event.unicode == 's':
				new = p.locale.south
				if new:
					p.locale = new
			elif event.type == pygame.KEYDOWN and event.unicode == 'd':
				new = p.locale.east
				if new:
					p.locale = new

		if not paused:
			a.step()
			updates = a.board.board_group.draw(window)
			pygame.display.update(updates)

		print( clck.get_fps(), '\r', end='' )
		sys.stdout.flush()


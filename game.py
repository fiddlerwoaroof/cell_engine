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

import sys
import collections
import pygame

class Cell(object):
	north = None
	south = None
	east = None
	west = None
	rules = {}


	def rule(self, *a):
		'''The rule used to determine the new value for the current cell, add_rule reassigns this based on the current value'''
		return self.value

	@classmethod
	def add_rule(self, value):
		'''Add a rule to correspond to the current value of the cell'''
		def _inner(rule):
			self.rules[value] = rule
			return rule
		return _inner

	def __init__(self):
		self.value = None
		self.update_neighbors()

	def set_value(self, v):
		'''Change the cells value and select the appropriate rule'''
		if v != self.value:
			self.value = v
			if v is not None:
				self.rule = self.rules[v]

	def neighbor_value(self):
		'''Get the total of the values of neighbouring cells'''
		result = 0
		for c in self.neighbors:
			if c is None: continue
			elif c.value is None: continue
			result += c.value
		return result

	def update_neighbors(self):
		'''Change the neighbors attribute to reflect the current situation'''
		self.neighbors = (self.north, self.south, self.east, self.west, self.northwest, self.northeast, self.southwest, self.southeast)

	def autoconnect(self):
		'''Set up the reverse links appropriate to the current situation'''
		updated = []

		if self.south and self.south.north is not self:
			self.south.north = self
			updated.append(self.south)
		if self.north and self.north.south is not self:
			self.north.south = self
			updated.append(self.north)
		if self.east and self.east.west is not self:
			self.east.west = self
			updated.append(self.east)
		if self.west and self.west.east is not self:
			self.west.east = self
			updated.append(self.west)

		for up in updated:
			up.autoconnect()

		self.update_neighbors()

	@property
	def northeast(self):
		r = self.north
		if r is not None:
			return r.east

	@property
	def northwest(self):
		r = self.north
		if r is not None:
			return r.west

	@property
	def southeast(self):
		r = self.south
		if r is not None:
			return r.east

	@property
	def southwest(self):
		r = self.south
		if r is not None:
			return r.west


	def __repr__(self):
		return '%s().set_value(%s)' % (self.__name__, self.value)

	def __str__(self):
		return str(self.value)

class CellSprite(pygame.sprite.DirtySprite):
	'''Display code for :py:class:`Cell`'''

	def __init__(self, cell, row, col, *a):
		self.image = pygame.surface.Surface( (6,6) )
		self.cell = cell
		self.row = row
		self.col = col
		cell.sprite = self
		self.spacing = 0

		row, col = self.row, self.col
		spacing = self.spacing
		size = width, height = self.image.get_size()
		self.rect = pygame.rect.Rect( (width*(col)+spacing*(col), (height*(row)+spacing*(row))), size )

		pygame.sprite.DirtySprite.__init__(self, *a)
		self.start_update(self.cell.value)


	colors = {
		None: (128,128,128),
		0: (0,0,0),
		1: (0,255,0),
		2: (128,64,0),
		3: (255,0,0)
	}

	def start_update(self, value):
		'''Begin to update the cell: store the new value and mark the sprite "dirty"'''
		self.new_value = value
		self.dirty = 1
		self.ud = True

	def update(self):
		'''Update the cell: set the cell's value and paint the new image'''
		if self.ud:
			self.cell.set_value(self.new_value)
			self.image.fill( self.colors[self.cell.value] )


class Board(object):
	'''Set up and store the cells'''

	def __init__(self, width, height):
		self.board_group = pygame.sprite.LayeredDirty(_use_update=True)
		self.rect = pygame.Rect(0,0,0,0)
		self.dct = {}

		for col in xrange(width):
			for row in xrange(0,height):
				cell = self.dct[row, col] = Cell()
				sprite = CellSprite(cell, row, col, self.board_group)

		for col in xrange(width):
			for row in xrange(height):
				cell = self.dct[row,col]
				cell.east = self.dct.get((row,col+1))
				cell.south = self.dct.get((row+1,col))
				cell.autoconnect()

		self.init = self.dct[0,0]
		self.rect.unionall_ip(list(self.board_group))


	def __str__(self):
		current = self.init
		result = []
		while current.east != None:
			top = current
			result.append([])
			while top.south != None:
				result[-1].append(str(top))
				top = top.south
			current = current.east
		result = zip(*result)
		return '\n'.join(
			' '.join(r) for r in result
		)

import random



class Controller(object):
	'''Initialize cell values and run the simulation'''
	def __init__(self, board):
		self.board = board
		self.observers = []

		column = self.board.init
		for sprite in self.board.board_group:
			sprite.start_update( random.choice([1]*7+[0]*5 +[2]) )
		self.board.board_group.update()


	def step(self):
		'''Run one iteration of the simulation'''
		for observer in self.observers:
			observer.act()

		c_sprites = pygame.sprite.Group()
		for sprite in self.board.board_group:
			cell = sprite.cell
			nvalue = cell.rule
			if callable(nvalue):
				nvalue = nvalue(cell)
			if nvalue is None:
				nvalue = cell.value
			if nvalue != cell.value:
				sprite.start_update(nvalue)
				c_sprites.add(sprite)
		c_sprites.update()
		return self

	def add_observer(self, cls, *args, **kwargs):
		'''add an observer to a cell'''
		observer = cls(*args, **kwargs)
		self.observers.append(observer)
		return observer

	def init(self, cb):
		self.init = cb
		return self

	def add_event(self, cb):
		self.events.append(cb)
		return self

	def loop(self):
		variables = {}
		variables.update(self.init())
		clck = pygame.time.Clock()
		variables['running'] = True

class Presence(object):
	'''Observer interface'''
	def __init__(self, locale):
		self.locale = locale

	def act(self):
		'''Override to implement behavior'''
		pass


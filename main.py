import colorama
from colorama import Fore
from time import sleep
from pynput import keyboard
import os
from time import perf_counter

colorama.init(autoreset=True)

CONTROL = {
	'a' : (0, -1),
	'w' : (-1, 0),
	's' : (1, 0),
	'd' : (0, 1),
}


class Sudoku:

	def __init__(self, width = 3, heigh = 1) -> None:
		self.WIDTH = width
		self.HEIGHT = heigh
		self.matrix = [[0 for y in range(9)] for _ in range(9)]
		self.curindex = [8, 0]

	def on_press(self, key) -> None:

		''' On keyboard press '''

		try:
			if key.char in 'asdw':
				self.moveIndex(CONTROL[key.char][0], CONTROL[key.char][1])
			elif key.char in '123456789':
				self.writeNum(key.char)
			elif key.char == 'j':
				self.solve()

				self.drawSolved()
			elif key.char =='c':
				self.matrix = [[0 for y in range(9)] for _ in range(9)]
				self.drawSolved()
				

		except Exception as e:
			raise e
			pass

	def solve(self):

		''' Main Backtracking algorithm to solve sudoku '''

		def solveMat(x, y):

			if x == 9 and y == 0:
				return True

			if self.matrix[x][y]:	
				if solveMat(*((x, y+1) if y+1 < 9 else (x+1, 0))):
					return True
				return

			for l in range(1, 10):
				self.matrix[x][y] = l
				if self.isValid(x, y):
					if solveMat(*((x, y+1) if y+1 < 9 else (x+1, 0))):
						return True
				self.matrix[x][y] = 0
				
		solveMat(0, 0)

	def drawSolved(self):

		''' Drawing solved sudoku '''
		self.moveIndex(self.curindex[0]*-1, self.curindex[1]*-1)

		for j in range(9):
			for i in range(9):
				self.curindex[0], self.curindex[1] = j, i
				self.writeNum(str(self.matrix[j][i]))
				self.moveIndex(0, 1)
			self.moveIndex(1, 0)

	def startGame(self, firstTime = True) -> None:

		''' Printing sudoku starting interface '''

		if firstTime:
			while not self.WIDTH%2:
				self.WIDTH+=1
			while not self.HEIGHT%2:
				self.HEIGHT+=1

		for i in range(10):
			for j in range(9*self.WIDTH+10):
				if (not i % 3) or (not j % (self.WIDTH*3+3)): 
					color = Fore.BLUE
				else:
					color = Fore.GREEN

				if j%(self.WIDTH+1):
					print(color + '-', end='')
				else:
					print(color + '+', end='')

			print()
			if i != 9:
				for h in range(self.HEIGHT):
					for l in range(10):
						print((Fore.BLUE if not l % 3 else Fore.GREEN) + '|' + ' '*self.WIDTH, end='')
					print()
		print(f'\033[{1+(self.HEIGHT+1)//2}A\033[{(self.WIDTH+1)//2}C', end='')
		self.moveIndex(1, 0)

		print(f'\033[{self.WIDTH//2 + self.WIDTH*9 + 9}C', end='')

		texts = ("Solve - J", "Clear - C")

		for text in texts:
			l = len(text)
			print(text, end='')
			print(f'\033[{l}D', end='')
			print(f'\033[2B', end='')
		print(f'\033[{2*len(texts)}A', end='')
		print(f'\033[{self.WIDTH//2 + self.WIDTH*9 + 9}D', end='')

		with keyboard.Listener(on_press=self.on_press) as listener:
			listener.join()
		
	def isValid(self, x=None, y=None) -> bool:
		
		''' Returning True if the current Sudoku is valid else False '''

		if not x and not y:
			x, y = self.curindex

		if not self.matrix[x][y]:
			return True
		
		# Row validator
		if self.matrix[x].count(self.matrix[x][y]) > 1:
			print(' ', end='')
			print('\033[1D', end='')
			return False

		# Column validator
		if [self.matrix[j][y] for j in range(9)].count(self.matrix[x][y]) > 1:
			print(' ', end='')
			print('\033[1D', end='')
			return False

		# Cube validator
		xc, yc = x//3, y//3
		cubeMatrix = [self.matrix[i][j] for i in range(xc*3, xc*3+3) for j in range(yc*3, yc*3+3)]

		if cubeMatrix.count(self.matrix[x][y]) > 1:
			print(' ', end='')
			print('\033[1D', end='')
			return False

		return True

	def moveIndex(self, movedown, moveright) -> None:

		""" 
		Moving cursor position by {movedown} points 
		down and {moveright} points right
		{movedown} and {moveright} can be negative numbers
		"""

		downup = 'B' if movedown > 0 else 'A'
		leftright = 'C' if moveright > 0 else 'D'

		self.curindex[0] += movedown
		self.curindex[1] += moveright


		if self.curindex[0] > 8 or self.curindex[0] < 0:
			movedown = min(9-movedown, 9+movedown)
			downup = ('B', 'A')[self.curindex[0] > 8]


		if self.curindex[1] > 8 or self.curindex[1] < 0:
			moveright = min(9-moveright, 9+moveright)
			leftright = ('C', 'D')[self.curindex[1] > 8]


		for j in range(len(self.curindex)):
			if self.curindex[j] > 8:
				self.curindex[j] -= 9
			elif self.curindex[j] < 0:
				self.curindex[j] += 9

		movedown, moveright = abs(movedown), abs(moveright)
		movedown = movedown + movedown*self.HEIGHT + 1
		moveright = moveright + moveright*self.WIDTH + 1

		print(f'\033[{movedown-1}{downup}', end='')
		print(f'\033[{moveright-1}{leftright}', end='')

	def writeNum(self, num):

		''' Writing number into cell '''

		self.matrix[self.curindex[0]][self.curindex[1]] = int(num)
		if not self.matrix[self.curindex[0]][self.curindex[1]]:
			num = ' '

		invalidNum = False
		if not self.isValid():
			color = Fore.RED
			invalidNum = True
		else:
			color = Fore.YELLOW

		print(color+num, end='')
		print('\033[1D', end='')

		if invalidNum:
			print('\033[1C', end='')
			sleep(1)
			print('\033[1D', end='')
			print(' ', end='')
			print('\033[1D', end='')
			self.matrix[self.curindex[0]][self.curindex[1]] = 0


game = Sudoku(5, 3)
game.startGame()


input()
		

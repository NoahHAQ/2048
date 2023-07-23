import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable

from a3_support import *

class Model:
	"""This is the model class that the controller uses to understand and 
    mutate the game state.
	"""
	def __init__(self) -> None:
		"""Constructs a new 2048 model instance."""
		self.new_game()
		self._valid_move = [UP, LEFT, DOWN, RIGHT]
		self._score = 0
		self._undos = 3
		self._previous_info = []

	def new_game(self) -> None:
		"""Sets or resets the game state to an initial game state.
		
		Any information is set to its initial state, the tiles are all set to 
		empty, and then two new starter tiles are randomly generated.
		"""
		self.tiles_matrix = [
			[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
		self.add_tile()
		self.add_tile()
		
	def get_tiles(self) -> list[list[Optional[int]]]:
		"""Return the current tiles matrix."""
		return self.tiles_matrix

	def add_tile(self) -> None:
		"""Randomly generate a new tile at an empty location and add it to the 
		current tiles matrix.
		"""
		tile, value = generate_tile(self.tiles_matrix)
		self.tiles_matrix[tile[0]][tile[1]] = value

	def move_left(self) -> None:
		"""Moves all tiles to their left extreme, merging where necessary, and 
		add any points gained from the move to the total score.
		"""
		self.tiles_matrix = stack_left(self.tiles_matrix)
		self.tiles_matrix, score_added = combine_left(self.tiles_matrix)
		self.tiles_matrix = stack_left(self.tiles_matrix)
		self._score += score_added

	def move_right(self) -> None:
		"""Moves all tiles to their right extreme, merging where necessary, and 
		add any points gained from the move to the total score.
		"""
		self.tiles_matrix = reverse(self.tiles_matrix)
		self.move_left()
		self.tiles_matrix = reverse(self.tiles_matrix)	

	def move_up(self) -> None:
		"""Moves all tiles to their top extreme, merging where necessary, and 
		add any points gained from the move to the total score.
		"""
		self.tiles_matrix = transpose(self.tiles_matrix)
		self.move_left()
		self.tiles_matrix = transpose(self.tiles_matrix)	

	def move_down(self) -> None:
		"""Moves all tiles to their bottom extreme, merging where necessary, 
		and add any points gained from the move to the total score.
		"""
		self.tiles_matrix = transpose(self.tiles_matrix)
		self.move_right()
		self.tiles_matrix = transpose(self.tiles_matrix)

	def move_detected(self, move: str) -> None:
		"""Makes the move according to the key detected by event.

		Parameters:
			move: A string represents a key press.
		"""
		if move == UP:
			self.move_up()
		elif move == LEFT:
			self.move_left()
		elif move == DOWN:
			self.move_down()
		elif move == RIGHT:
			self.move_right()
	
	def move_check(self, move: str) -> bool:
		"""Returns True if the move resulted in a change to the game state, 
		else False. 

		Parameters:
			move: A string represents a key press.
		"""
		if len(self._previous_info) > 0:
			last_step = (self.get_tiles(), self.get_score())
			self.move_detected(move)
			if self.tiles_matrix != last_step[0]:
				self.tiles_matrix = last_step[0]
				self._score = last_step[1]
				return True
			return False

	def attempt_move(self, move: str) -> bool:
		"""Makes the appropriate move according to the move string provided. 
		
		Precondition:
			The move provided must be one of wasd.

		Parameters:
			move: A string represents a key press.

		Returns:
			True if the move resulted in a change to the game state, else 
			False. 
		"""
		removed_info = ()
		# Update the list of information of previous steps for undos
		if len(self._previous_info) > self.get_undos_remaining():
			removed_info = self._previous_info.pop(0)
		self._previous_info.append((self.get_tiles(), self.get_score()))
		
		check = self.move_check(move)
		if check:
			self.move_detected(move)
			return True
		else:
			# Recover the content in self.previous_info
			if removed_info:
				self._previous_info.insert(0, removed_info)
			self._previous_info.pop()
			return False

	def has_won(self) -> bool:
		"""Returns True if the game has been won, else False.
		
		The game has been won if a 2048 tile exists on the grid.
		"""
		for row in self.tiles_matrix:
			if 2048 in row:
				return True
		return False

	def has_lost(self) -> bool:
		"""Returns True if the game has been lost, else False.
		
		The game has been lost if there are no remaining empty places in the 
		grid, but no move would result in a change to the game state.
		"""
		for row in self.tiles_matrix:
			if None in row or \
				any([self.move_check(x) for x in self._valid_move]):
				return False
		return True

	def get_score(self) -> int:
		"""Returns the current score for the game."""
		return self._score
		
	def get_undos_remaining(self) -> int:
		"""Gets the number of undos the player has remaining."""
		return self._undos

	def get_previous_info(self) -> int:
		"""Returns the information of previous steps for undos."""
		return self._previous_info

	def use_undo(self) -> None:
		"""Attempts to undo the previous move, returning the current tiles to 
		the previous tiles state before the last move that made changes to the 
		tiles matrix.
		"""
		if self._undos > 0 and len(self._previous_info) > 0:
			self._undos -= 1
			a = self._previous_info.pop()
			self.tiles_matrix = a[0]
			self._score = a[1]

	def loading(
		self, tiles_matrix: list[list[Optional[int]]],
		score: int,
		undos: int,
		previous_info: list[list[list[Optional[int]]]]
	) -> None:
		"""Update the data of game according to the game described in the 
		selected file.

		Parameters:
			tiles_matrix: The tiles currently on the grid.
			score: The current score for the game.
			undos: The number of undos the player has remaining.
			previous_info: A list of information of previous steps for undos.
		"""
		self.tiles_matrix = tiles_matrix
		self._score = score
		self._undos = undos
		self._previous_info = previous_info


class GameGrid(tk.Canvas):
	"""The GameGrid is a view class which inherits from tk.Canvas and 
	represents the 4x4 grid.
	"""
	BOARD_WIDTH = 400
	BUFFER = 10

	def __init__(self, master: tk.Tk, **kwargs) -> None:
		"""Sets up a new GameGrid in the master window.
		
		Parameters:
			master: The master window.
			**kwargs: The keyword arguments supported by tk.Canvas.
		"""
		self.box_side = (self.BOARD_WIDTH - 5 * self.BUFFER) / 4
		super().__init__(
			master,
			width=400,
			height=400,
			**kwargs
		)

	def _get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
		"""Return the bounding box for the (row, column) position, in the form: 
		(x_min, y_min, x_max, y_max).
		
		Parameters:
			position: A list of the (row, column) position.
		"""
		row, col = position
		x_min = (self.box_side + self.BUFFER) * col + self.BUFFER
		y_min = (self.box_side + self.BUFFER) * row + self.BUFFER
		x_max = (self.box_side + self.BUFFER) * (col + 1)
		y_max = (self.box_side + self.BUFFER) * (row + 1)
		return (x_min, y_min, x_max, y_max)

	def _get_midpoint(self, position: tuple[int, int]) -> tuple[int, int]:
		"""Return the graphics coordinates for the center of the cell at the 
		given (row, col) position.
		
		Parameters:
			position: A list of the (row, column) position.
		"""
		x_min, y_min, x_max, y_max = self._get_bbox(position)
		x_mid = (x_min + x_max) // 2
		y_mid = (y_min + y_max) // 2
		return (x_mid, y_mid)

	def clear(self) -> None:
		"""Clears all items."""
		super().delete(tk.ALL)

	def redraw(self, tiles: list[list[Optional[int]]]) -> None:
		"""Clears and redraws the entire grid based on the given tiles.
		
		Parameters:
			tiles: A list of lists of tiles.
		"""
		self.clear()
		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):
				x_min, y_min, x_max, y_max = self._get_bbox((row, col))
				x_mid, y_mid = self._get_midpoint((row, col))
				value = tiles[row][col]
				# Draw the box
				self.create_rectangle(
					x_min, y_min, x_max, y_max,
					width=1,
					fill=COLOURS[value]
				)
				# Add the value at the center of the box
				if value != None:
					self.create_text(
						x_mid, y_mid,
						text=str(value),
						font=TILE_FONT,
						fill=FG_COLOURS[value]
					)


class StatusBar(tk.Frame):
	"""The StatusBar is a view class which that inherits from tk.Frame and 
	represents information about score and remaining undos, as well as a button 
	to start a new game and a button to undo the previous move.
	"""
	def __init__(self, master: tk.Tk, **kwargs):
		"""Sets up self to be an instance of tk.Frame and sets up inner frames, 
		labels and buttons in this status bar.
				
		Parameters:
			master: The master window.
			**kwargs: The keyword arguments supported by tk.Frame.
		"""
		super().__init__(
			master,
			**kwargs
		)

		# Score block
		self.score_block = tk.Frame(self, bg=BACKGROUND_COLOUR)
		self.score_block.pack(side=tk.LEFT, expand=tk.TRUE)

		self.score_text = tk.Label(
			self.score_block,
			text="SCORE",
			font=('Arial bold', 20),
			fg=COLOURS[None],
			bg=BACKGROUND_COLOUR
			)
		self.score_text.pack()

		self.score_num = tk.Label(
			self.score_block,
			text="0",
			font=('Arial bold', 15),
			fg=LIGHT,
			bg=BACKGROUND_COLOUR
		)
		self.score_num.pack()

		# Undos block
		self.undos_block = tk.Frame(self, bg=BACKGROUND_COLOUR)
		self.undos_block.pack(side=tk.LEFT, expand=tk.TRUE)

		self.undos_text = tk.Label(
			self.undos_block,
			text="UNDOS",
			font=('Arial bold', 20),
			fg=COLOURS[None],
			bg=BACKGROUND_COLOUR
			)
		self.undos_text.pack()

		self.undos_num = tk.Label(
			self.undos_block,
			text="3",
			font=('Arial bold', 15),
			fg=LIGHT,
			bg=BACKGROUND_COLOUR
		)
		self.undos_num.pack()

		# Button block
		self.buttons = tk.Frame(self)
		self.buttons.pack(side=tk.LEFT, expand=tk.TRUE)

		self.new_game = tk.Button(self.buttons, text="New Game")
		self.new_game.pack()

		self.undo_move = tk.Button(self.buttons, text="Undo Move")
		self.undo_move.pack()

	def redraw_infos(self, score: int, undos: int) -> None:
		"""Updates the score and undos labels to reflect the information given.
		
		Parameters:
			score: The current score for the game.
			undos: The current number of undos the player has remaining.
		"""
		self.score_num.config(text=str(score))
		self.undos_num.config(text=str(undos))

	def set_callbacks(
		self, new_game_command: callable, undo_command: callable
	) -> None:
		"""Sets the commands for the new game and undo buttons to the given 
		commands.

		Parameters:
			new_game_command: The function to be called when the "New Game" 
			button is pressed.
			undos_command: The function to be called when the "Undo Move" 
			button is pressed.
		"""
		self.new_game.config(command=new_game_command)
		self.undo_move.config(command=undo_command)


class Game:
	"""Game is a controller class. The controller class is responsible for 
	maintaining the model and view classes, binding some event handlers, and 
	facilitating com-munication between model and view classes.
	"""
	def __init__(self, master: tk.Tk) -> None:
		self.master = master
		self.master.wm_title("CSSE1001/7030 2022 Semester 2 A3")
		self.model = Model()

		# Draw the header
		self.header = tk.Frame(master)
		self.header.pack(fill=tk.BOTH)
		self.title = tk.Label(
			self.header,
			text="2048",
			font=TITLE_FONT,
			fg=LIGHT,
			bg="orange"
			)
		self.title.pack(fill=tk.BOTH)
		
		# Draw the canvas
		self.view = GameGrid(master, bg=BACKGROUND_COLOUR)
		self.view.pack()

		# Draw the statusbar
		self.status_bar = StatusBar(master)
		self.status_bar.pack(fill=tk.BOTH)

		self.draw()

		# Set the events
		master.bind("<KeyPress-a>", self.attempt_move)
		master.bind("<KeyPress-w>", self.attempt_move)
		master.bind("<KeyPress-s>", self.attempt_move)
		master.bind("<KeyPress-d>", self.attempt_move)
		self.status_bar.set_callbacks(
			self.start_new_game, self.undo_previous_move)

	def draw(self) -> None:
		"""Redraws any view classes based on the current model state."""
		self.view.redraw(self.model.get_tiles())
		self.status_bar.redraw_infos(
			self.model.get_score(), self.model.get_undos_remaining())

	def attempt_move(self, event: tk.Event) -> None:
		"""Attempt a move. Once a move has been made, this method redraws the 
		view and displays an information messagebox if the game has been won or 
		creates a new tile after 150ms if the game has not been won.

		Parameters:
			event: The event represents a key press.
		"""
		if self.model.attempt_move(event.char):
			self.draw()
			if self.model.has_won():
				messagebox.showinfo(
					title="Congratulations!",
					message=WIN_MESSAGE
					)
			else:
				self.view.after(150, self.new_tile)			

	def new_tile(self) -> None:
		"""Adds a new tile to the model and redraws. If the game has been lost 
		with the addition of the new tile, then this method displays an 
		information messagebox.
		"""
		self.model.add_tile()
		self.draw()
		if self.model.has_lost():
			messagebox.showinfo(title="Oops!", message=LOSS_MESSAGE)

	def undo_previous_move(self) -> None:
		"""A handler for when the 'Undo' button is pressed in the status bar. 
		
		This method attempts to undo the last action, and then redraws the view 
		classes with the updated model information.
		"""
		self.model.use_undo()
		self.draw()

	def start_new_game(self) -> None:
		"""A handler for when the "New Game' button is pressed in the status 
		bar.
		
		This method causes the model to set its state to that of a new game, 
		and redraws the view classes to reflect these changes.
		"""
		self.model = Model()
		self.draw()


def save_game(game: Game) -> Callable:
	"""Prompts the player for the location to save their file and save all 
	necessary information to replicate the current state of the game.
	
	Parameters:
		game: The Game class.
	"""
	def handler():
		file_type = [('Text Document', '*.save')]
		filepath = filedialog.asksaveasfile(
			mode='w',
			filetypes = file_type,
			defaultextension = file_type
			)
		if filepath:
			replicate = []
			replicate.append(game.model.get_tiles())
			replicate.append(game.model.get_score())
			replicate.append(game.model.get_undos_remaining())
			replicate.append(game.model.get_previous_info())
			with filepath as file:
				file.write(str(replicate))
	return handler

def load_game(game: Game) -> Callable:
	"""Prompts the player for the location of the file to load a game from and 
	load the game described in that file.
	
	Parameters:
		game: The Game class.
	"""
	def handler():
		file_type = [('Text Document', '*.save')]
		filepath = filedialog.askopenfile(mode='r', filetypes = file_type)
		
		if filepath:
			extension = filepath.name.split('.')[-1]
			# Check the player has selected the correct file type.
			if extension != "save":
				messagebox.showerror(
					title="Error",
					message="The file type is incorrect!"
					)
			else:
				with filepath as file:
					replicate = eval(file.read())
					# Check the player has selected a valid game file.
					if type(replicate) is list and len(replicate) == 4:
						game.model.loading(replicate[0], replicate[1],
											replicate[2], replicate[3])
						game.draw()
					else:
						messagebox.showerror(
							title="Error",
							message="This save file is not valid for game!"
							)
	return handler

def new_game(game: Game) -> Callable:
	"""Creates a new game.
	
	Parameters:
		game: The Game class.
	"""
	def handler():
		game.start_new_game()
	return handler

def quit(game: Game) -> Callable:
	"""Prompts the player via messagebox to ask whether they are sure they 
	would like to quit. If no, do nothing. If yes, quit the game.

	Parameters:
		game: The Game class.
	"""
	def handler():
		if messagebox.askyesno(
			title="Confirmation",
			message="Wanna quit the game?"
			):
			game.master.destroy()
	return handler
		
def play_game(root):
	"""Instantiates the application.

	Parameters:
		root: the master window.
	"""
	game = Game(root)

	# Add a file menu
	menu = tk.Menu(root)
	root.config(menu=menu)

	# File >
	file_menu = tk.Menu(menu)
	menu.add_cascade(
		label="File",
		menu=file_menu
	)

	# File > Save game
	file_menu.add_command(
		label="Save game",
		command=save_game(game)
	)

	# File > Load game
	file_menu.add_command(
		label="Load game",
		command=load_game(game)
	)

	# File > New game
	file_menu.add_command(
		label="New game",
		command=new_game(game)
	)

	# File > Quit
	file_menu.add_command(
		label="Quit",
		command=quit(game)
	)


if __name__ == '__main__':
	root = tk.Tk()
	play_game(root)
	root.mainloop()
	
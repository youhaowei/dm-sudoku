from tkinter import *
from tkinter import filedialog

"""
global variable
"""
selected_position = -2, -2 # initialize selected position, -2 instead of -1 because -1,-1 will draw an extra rectangle on canvas
master = Tk()

class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args + "-- current version 0.0.2 (alpha)")
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="(-- current version 0.0.2 (alpha)")
        self.label.update_idletasks()

statusBar = StatusBar(master)
statusBar.pack(side=BOTTOM, fill=X)
canvas = Canvas(master, width=580, height=580)
canvas.create_rectangle(15,15,565,565, width=2.0) # draw the outer-boarder
canvas.pack(side=LEFT) # add canvas into frame
table = [] # initialize table
pencil = False
SCREEN_W = master.winfo_screenwidth()#This value is the width of the screen
SCREEN_H = master.winfo_screenheight()#This is the height of the screen
master.resizable(0,0)

class Cell:

	def __init__(self):
		self.value = 0
		self.isLocked = False
		self.guess = [False] * 9
		self.isValid = True

	def __repr__(self):
		if self.value < 0:
			return '?'
		elif(self.value not in range(1,10)):
			return ""
		else:
		 	return str(self.value)

"""
Functions
"""
def eliminateWrongGuesses(row, col):
	##print("call eliminateWrongGuesses()")
	cell = table[row][col]
	if cell.value > 0:
		section_x = row // 3 * 3
		section_y = col // 3 * 3
		for r in range(section_x, section_x+3):
			for c in range(section_y, section_y+3):
				if table[r][c].value == 0:
					table[r][c].guess[cell.value-1] = False
		for i in range(9):
			if table[row][i].value == 0:
				table[row][i].guess[cell.value-1] = False
			if table[i][col].value == 0:
				table[i][col].guess[cell.value-1] = False

def getHint():
	for row in range(9):
		for col in range(9):
			cell = table[row][col]
			if cell.value == 0:
				cell.guess = [True]*9
				section_x = row // 3 * 3
				section_y = col // 3 * 3
				for r in range(section_x, section_x+3):
					for c in range(section_y, section_y+3):
						if(table[r][c].value > 0):
							cell.guess[table[r][c].value-1] = False
				for i in range(9):
					if(table[row][i].value > 0):
						cell.guess[table[row][i].value-1] = False
					if(table[i][col].value > 0):
						cell.guess[table[i][col].value-1] = False
	draw(canvas, table)


def quit():
	exit()

def loadLocalProblemFile(master=master):
	loadProblem(table, filedialog.askopenfilename(filetypes=(('sudoku problem file', '.sdp'),), initialdir='./problems/', initialfile='start.sdp', parent=master, title="choose a problem to solve"))
	draw(canvas, table)

def loadProblem(table, filename):
	file_in = open(filename)
	r = -1
	for line in file_in:
		r += 1
		l = line.split()
		c = -1
		for i in l:
			c += 1
			##print(len(l))
			if i >= '1' and i <= '9':
				##print(r,c)
				table[r][c].value = int(i)
				table[r][c].isLocked = True
			else:
				table[r][c].value = 0
				table[r][c].isLocked = False

	file_in.close()

def drawValue(row, col, table):
	if(row != selected_position[0] or col != selected_position[1]):
		drawRectangle(row, col, "white")
	weight = 'italic'
	font = "times"
	if table[row][col].isLocked:
		weight = 'bold'
	if table[row][col].value == 0:
		guess = table[row][col].guess
		index = 0
		for i in guess:
			if i:
				drawGuess(row, col, index)
			index += 1
	elif isValid(row, col, table):
		#print("draw text")
		canvas.create_text(row*60+50, col*60+50, font=(font, 24, weight), text=str(table[row][col]))
	else:
		#print("draw text")
		canvas.create_text(row*60+50, col*60+50, font=(font, 24, weight), text=str(table[row][col]), fill="red")

def drawGuess(row, col, guess):
	#print("draw guess")
	x = row*60+20
	y = col*60+20
	if guess % 3 == 0:
		x += 10
	elif guess % 3 == 1:
		x += 30
	else:
		x += 50
	if guess // 3 == 0:
		y += 10
	elif guess // 3 == 1:
		y += 30
	else:
		y += 50
	canvas.create_text(x, y, text=str(guess+1))


def drawRectangle(row, col, color):
	#print("draw rect")
	canvas.create_rectangle(row*60+20, col*60+20, row*60+60+20, col*60+60+20, fill=color, width=1.0)

def drawBoard():
	"""
	Make the line wider every 3 cells
	"""
	#print("draw lines")
	for i in range(0, 10, 3):
		j = 20+i*60
		canvas.create_line(j, 20, j, 560, width=2.0)
		canvas.create_line(20, j, 560, j, width=2.0)

def onMouseClick(event):
	global selected_position, pencil
	row = selected_position[0]
	col = selected_position[1]
	drawRectangle(row, col, "white")
	drawValue(row, col, table)
	selected_position = getPosition(event.x, event.y)
	draw(canvas, table)
	row = selected_position[0]
	col = selected_position[1]
	if event.num == 1:
		# left-click
		drawRectangle(row, col, "gray")
		pencil = False
	else:
		# right-click
		drawRectangle(row, col, "#FFE8D3")
		pencil = True
	drawValue(row, col, table)
	drawBoard()

def getValue(event):
	global selected_position
	##print(event.keysym, pencil)
	if selected_position[0] >= 0 and selected_position[1] >= 0 and not table[selected_position[0]][selected_position[1]].isLocked:
		if pencil:
			if event.char > '0' and event.char <= '9':		
				table[selected_position[0]][selected_position[1]].guess[int(event.char)-1] = not table[selected_position[0]][selected_position[1]].guess[int(event.char)-1]
			elif event.char == '0':
				table[selected_position[0]][selected_position[1]].guess = [False]*9
		else:
			if event.char > '0' and event.char <= '9':		
				table[selected_position[0]][selected_position[1]].value = int(event.char)
				eliminateWrongGuesses(selected_position[0], selected_position[1])
			elif len(event.char) > 0:
			 	table[selected_position[0]][selected_position[1]].value = -1
	redraw_cell(canvas, table, selected_position[0], selected_position[1])
	#draw(canvas, table)

def onDeleteClicked(event):
	#global selected_position
	##print(event.keysym, event.keycode)
	if selected_position[0] >= 0 and selected_position[1] >= 0:
		if not table[selected_position[0]][selected_position[1]].isLocked:
			table[selected_position[0]][selected_position[1]].value = 0
	redraw_cell(canvas, table, selected_position[0], selected_position[1])
	#draw(canvas, table)

def onRightClicked(event):
	global selected_position
	if selected_position[0] >= 0 and selected_position[1] >= 0:
		row = selected_position[0]
		col = selected_position[1]
		drawRectangle(row, col, "white")
		drawValue(row, col, table)
		if selected_position[0] < 8:
			selected_position = selected_position[0] + 1, selected_position[1]
		row = selected_position[0]
		col = selected_position[1]
		if(pencil):
			drawRectangle(row, col, "#FFE8D3")
		else:
			drawRectangle(row, col, "gray")
		drawValue(row, col, table)
		drawBoard()

def onLeftClicked(event):
	global selected_position
	if selected_position[0] >= 0 and selected_position[1] >= 0:
		row = selected_position[0]
		col = selected_position[1]
		drawRectangle(row, col, "white")
		drawValue(row, col, table)
		if selected_position[0] > 0:
			selected_position = selected_position[0] - 1, selected_position[1]
		row = selected_position[0]
		col = selected_position[1]
		if(pencil):
			drawRectangle(row, col, "#FFE8D3")
		else:
			drawRectangle(row, col, "gray")
		drawValue(row, col, table)
		drawBoard()

def onDownClicked(event):
	global selected_position
	if selected_position[0] >= 0 and selected_position[1] >= 0:
		row = selected_position[0]
		col = selected_position[1]
		drawRectangle(row, col, "white")
		drawValue(row, col, table)
		if selected_position[1] < 8:
			selected_position = selected_position[0], selected_position[1] + 1
		row = selected_position[0]
		col = selected_position[1]
		if(pencil):
			drawRectangle(row, col, "#FFE8D3")
		else:
			drawRectangle(row, col, "gray")
		drawValue(row, col, table)
		drawBoard()

def onUpClicked(event):
	global selected_position
	if selected_position[0] >= 0 and selected_position[1] >= 0:
		row = selected_position[0]
		col = selected_position[1]
		drawRectangle(row, col, "white")
		drawValue(row, col, table)
		if selected_position[1] > 0:
			selected_position = selected_position[0], selected_position[1] - 1
		row = selected_position[0]
		col = selected_position[1]
		if(pencil):
			drawRectangle(row, col, "#FFE8D3")
		else:
			drawRectangle(row, col, "gray")
		drawValue(row, col, table)
		drawBoard()

def isValid(row, col, table):
	if table[row][col].value < 0:
		return True
	section_x = row // 3 * 3
	section_y = col // 3 * 3
	for r in range(section_x, section_x+3):
		for c in range(section_y, section_y+3):
			if table[r][c].value == table[row][col].value and not (r == row and c == col):
				return False
	for i in range(9):
		if table[row][i].value == table[row][col].value and col != i:
			return False
		if table[i][col].value == table[row][col].value and row != i:
			return False
	return True


def getPosition(x,y):
	row = (x-20) // 60
	col = (y-20) // 60
	if row < 0:
		row = 0;
	if col < 0:
		col = 0;
	if row > 8:
		row = 8
	if col > 8:
		col = 8
	return row, col

def redraw_cell(canvas, table, row, col):
	section_x = row // 3 * 3
	section_y = col // 3 * 3
	for r in range(section_x, section_x+3):
		for c in range(section_y, section_y+3):
			drawValue(r, c, table)
	for i in range(9):
		if not i in range(section_y, section_y+3):
			drawValue(row, i, table)
		if not i in range(section_x, section_x+3):
			drawValue(i, col, table)
	if pencil:
		drawRectangle(row, col, "#FFE8D3")
	else:
		drawRectangle(row, col, "gray")
	drawBoard()
	drawValue(row, col, table)

def draw(canvas, table):
	for row in range(9):
		for col in range(9):
			if row == selected_position[0] and col == selected_position[1]:
				drawRectangle(row, col, "gray")
			else:
				drawRectangle(row, col, "white")
			if not table[row][col] == None:
				drawValue(row, col, table)
	drawBoard()

def callback():
    ##print("called the callback!")
    statusBar.set("funtion under developed...")


def main():
	for i in range(9):
		col = []
		for j in range(9):
			col.append(Cell())
		table.append(col)
	canvas.bind("<Button-1>", onMouseClick)
	master.bind("<Key>", getValue)
	master.bind("<Left>", onLeftClicked)
	master.bind("<Right>", onRightClicked)
	master.bind("<Up>", onUpClicked)
	master.bind("<Down>", onDownClicked)
	master.bind("<BackSpace>", onDeleteClicked)
	canvas.bind("<Button-2>", onMouseClick)
	canvas.bind("<Button-3>", onMouseClick)
	w = 700
	h = 600
	master.geometry('%dx%d+%d+%d' % (w, h, SCREEN_W/2-290, SCREEN_H/2-290))
	canvas.create_text(580/2, 580/2, font=("Times", 48), text="Welcome to sudoku!")
	master.title("sudoku")
	master.withdraw()
	master.lift()
	master.deiconify()
	master.focus_force()
	#master.wm_iconbitmap('sudoku.icns')

	# create a menu
	menu = Menu(master)
	master.config(menu=menu)
	
	filemenu = Menu(menu)
	menu.add_cascade(label="File", menu=filemenu)
	filemenu.add_command(label="New Game", command=loadLocalProblemFile)
	filemenu.add_command(label="Load Local Problem", command=loadLocalProblemFile)
	filemenu.add_separator()
	filemenu.add_command(label="Continue a Saved Game", command=callback)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=quit)

	helpmenu = Menu(menu)
	menu.add_cascade(label="Help", menu=helpmenu)
	helpmenu.add_command(label="About...", command=callback)

	# create a toolbar
	toolbar = Frame(master)

	b = Button(toolbar, text="New", width=100, command=loadLocalProblemFile)
	b.pack(side=TOP,fill=X)

	b = Button(toolbar, text="get hint", width=100, command=getHint)
	b.pack(side=TOP,fill=X)

	toolbar.pack(side=RIGHT)

	
	master.mainloop()

if __name__ == '__main__':
	main()
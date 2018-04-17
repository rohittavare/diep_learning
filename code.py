"""
Rohit Tavare
April 2017

Screen size of 1080x1920
Chrome fullscreen
no bookmarks
visible windows bar on bottom
"""
#Global vars
#color values for different elements on screen
colors = {'block': (255, 232, 105), 'triangle': (252, 118, 119), 'pentagon': (118, 141, 252), 'wall': (185, 185, 185), 'enemy': (241, 78, 84), 'menu': (113, 204, 200), 'blank': (205, 205, 205)}
#score requred to achieve a level. This is our measure of fitness
levelScores = [0, 4, 13, 28, 50, 78, 113, 157, 211, 275, 350, 437, 538, 655, 787, 938, 1109, 1301, 1516, 1757, 2026, 2325, 2658, 3026, 3433, 3883, 4379, 4925, 5525, 6184, 6907, 7698, 8537, 9426, 10368, 11367, 12426, 13549, 14739, 16000, 17337, 18754, 20256, 21849, 23536]
#initialize to first generation
generation = 1
levelingUp = False
#a list to keep track of each of the networks our program is testing
networks = []
#a list to keep track of neuron counts for each network
numNeurons = []
#initialize a list to keep track of the fitness of our networks
fitness = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#a list to keep track of the last output of the networks
last = [0, 0, 0, 0, 0, 0]
#arrays to save the previous 2 frames
prevFrame = []
prevFrame2 = []
#an incrementor to tell us which network is being tested
currentNet = 0
#a variable to count the streak of identical outputs (too many means the network is failing)
stk = 0
#is the player alive?
alive = 0
#is the network currently playing
playing = False
mouseOnTarget = False
#an incremented variable to keep track of the innovation number of mutations
innovation = 0
#starting level for the round, changes for each game
lev_start = 1
#ending level, used to calculate fitness score accoring to points
lev_end = 1
#level just completed, using to calculate fitness if current level was not beaten
prev_lev = 1

x_pos = 250
y_pos = 66

import ImageGrab
import os
import time
import win32api, win32con
import random
import msvcrt
import numpy
import ImageOps
try:
    import Image
except ImportError:
    from PIL import Image
import pytesser as pt

def screenGrab():
    box=(0,y_pos,x_pos+1400 ,y_pos+973)
    im = ImageGrab.grab(box)
    #im.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) + '.png', 'PNG')
    return im

#get the level of the player
def scoreGrab():
    box=(890, 998, 1015, 1016)
    im = ImageGrab.grab(box)
    name = 'score.png'
    im.save(name, 'PNG')
    im = Image.open(name)
    text = pt.image_to_string(im)
    text = pt.image_file_to_string(name)
    text = pt.image_file_to_string(name, graceful_errors=True)
    ret = 0
    try:
        ret = int(filter(str.isdigit, text))
    except ValueError:
        ret = 2
    return ret

#initialize variables at the start of a game
def setStartLevels():
    global lev_start
    global lev_end
    global prev_lev
    num = scoreGrab()
    lev_start = num
    lev_end = num
    prev_lev = num

#increment levels
def increasePrev():
    global prev_lev
    prev_lev = lev_end

#setter for ending level
def setEndLevels():
    global lev_end
    num = scoreGrab()
    if num == 3 and lev_start >= 3:
        num = 8
    lev_end = num

#a program to determine if the player levels up: check when the level meter has filled and emptied
def isLevelUp():
    im = screenGrab()
    col = im.getpixel((919 + x_pos, 940))
    if col[0] > col[2] and levelingUp == False:
        toggleLevelUp(False)
        return False
    elif col[0] <= col[2] and levelingUp == True:
        toggleLevelUp(True)
        increasePrev()
        time.sleep(.1)
        setEndLevels()
        return True
    else:
        return False

#invert the state of the level up variable
def toggleLevelUp(lu):
    global levelingUp
    if lu == True:
        levelingUp = False
    else:
        levelingUp = True

#get data on how the screen currently looks as an array
def getData():
    mouseNotTarget()
    im = screenGrab()
    inp = []
    up = im.getpixel((100, 250))
    if up[0]  > up[2]:
        x, y = get_cords()
        setMousePos((-150, 250))
        leftCLick()
        time.sleep(0.1)
        setMousePos((x, y))
    for x in range(14):
        new = []
        for y in range(9):
            new.append(-2)
        inp.append(new)
    for i in range(14):
        for j in range(9):
            for x in range(0, 100, 5):
                for y in range(0, 100, 5):
                    if inp[i][j] == -2:
                        col = im.getpixel((100 * i + x + x_pos, 100 * j + y))
                        if (( i < 6 or i > 8) or (j < 4 or j > 6)) and col[0] == 153 and col[1] == 153 and col[2] == 153:
                            if mouseOnScreen():
                                setMousePos((100 * i + 50, 100 * j + 50))
                                mouseIsOnTarget()
                        if isSameColor(col, colors['enemy']):
                            inp[i][j] = -1
                            if mouseOnScreen() and not mouseOnTarget:
                                setMousePos((100 * i + 50, 100 * j + 50))
                                mouseIsOnTarget()
                            break
                        elif isSameColor(col, colors['block']):
                            inp[i][j] = 1
                            break
                        elif isSameColor(col, colors['triangle']):
                            inp[i][j] = 1
                            break
                        elif isSameColor(col, colors['pentagon']):
                            inp[i][j] = 1
                            break
            #col = im.getpixel((25 + 100*i, 25 + 100 * j))
            col2 = im.getpixel((75 + 100 * i + x_pos, 25 + 100 * j))
            col3 = im.getpixel((25 + 100 * i + x_pos, 75 + 100 * j))
            col4 = im.getpixel((75 + 100 * i + x_pos, 75 + 100 * j))
            col5 = im.getpixel((50 + 100 * i + x_pos, 50 + 100 * j))
            #if isSameColor(col1, colors['block']) or isSameColor(col2, colors['block']) or isSameColor(col3, colors['block']) or isSameColor(col4, colors['block']) or isSameColor(col5, colors['block']):
            #    inp[i][j] = 1
            #elif isSameColor(col1, colors['triangle']) or isSameColor(col2, colors['triangle']) or isSameColor(col3, colors['triangle']) or isSameColor(col4, colors['triangle']) or isSameColor(col5, colors['triangle']):
            #    inp[i][j] = 1
            #elif isSameColor(col1, colors['pentagon']) or isSameColor(col2, colors['pentagon']) or isSameColor(col3, colors['pentagon']) or isSameColor(col4, colors['pentagon']) or isSameColor(col5, colors['pentagon']):
            #    inp[i][j] = 1
            #elif isSameColor(col1, colors['enemy']) or isSameColor(col2, colors['enemy']) or isSameColor(col3, colors['enemy']) or isSameColor(col4, colors['enemy']) or isSameColor(col5, colors['enemy']):
            #    inp[i][j] = -1
            if inp[i][j] == -2:
                if isSameColor(col2, colors['blank']) or isSameColor(col3, colors['blank']) or isSameColor(col4, colors['blank']) or isSameColor(col5, colors['blank']):
                    inp[i][j] = 0.25
                else:
                    inp[i][j] = -2
    #printInput(inp)
    if mouseOnScreen() and not mouseOnTarget:
        for i in range(14):
            for j in range(9):
                if not mouseOnTarget and inp[i][j] == 1:
                    setMousePos((100 * i + 50, 100 * j + 50))
                    mouseIsOnTarget()
    return inp

#print the array passed in; meant to be used to print the data captured from the screen
def printInput(inp):
    for y in range(9):
        s = ""
        for x in range(14):
            if inp[x][y] == 1:
                s = s + "O"
            elif inp[x][y] == -1:
                s = s + "#"
            else:
                s = s + " "
        print s
    print "  "

#compare 2 colors
def isSameColor(c1, c2):
    if c1[0] == c2[0] and c1[1] == c2[1] and c1[2] == c2[2]:
        return True
    else:
        return False

#get the value of the key pressed
def getKey():
    key = ord(msvcrt.getch())
    print(key)

def main():
    initPrevFrame()
    initPrevFrame2()
    startGame()
    initializeNetworks()
    #while the program runs, start a new game by clicking the start button, or keep playing the current game
    while True:
        #start a new game by checking if the current screen is the menu screen then clicking enter. before a new game, the program moves to the next neural network.
        time.sleep(0.2)
        c = screenGrab().getpixel((587 + x_pos, 61))
        if isSameColor(c, colors['menu']):
            if playing:
                if alive >= 75:
                    curr = (currentNet + 1) % len(fitness)
                    incrementCurrNet(curr)
                incrementStk(0)
                incrementLife(0)
                togglePlay(True)
                releaseSpace()
            if mouseOnScreen():
                startGame()
            toggleLevelUp(True)
        else:
            #set the playing state to true and run the script to play
            if playing == False:
                togglePlay(False)
                holdSpace()
                setStartLevels()
            if stk < 50:
                runNetworks()
            upgrades()

#code to start a game
def startGame():
    setMousePos((100, 100))
    leftCLick()
    pressEnter()

#reset the prev frame variables
def initPrevFrame():
    global prevFrame
    for i in range(126):
        prevFrame.append(0)

def initPrevFrame2():
    global prevFrame2
    for i in range(126):
        prevFrame2.append(0)

#press buttons to upgrade the player
def upgrades():
    win32api.keybd_event(win32con.VK_NUMPAD7, 0, 1, 0)
    time.sleep(.01)
    win32api.keybd_event(win32con.VK_NUMPAD7, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_NUMPAD5, 0, 1, 0)
    time.sleep(.01)
    win32api.keybd_event(win32con.VK_NUMPAD5, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_NUMPAD6, 0, 1, 0)
    time.sleep(.01)
    win32api.keybd_event(win32con.VK_NUMPAD6, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_NUMPAD4, 0, 1, 0)
    time.sleep(.01)
    win32api.keybd_event(win32con.VK_NUMPAD4, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

#functions to simulate various key actions
def pressEnter():
    win32api.keybd_event(win32con.VK_RETURN, 0, 1, 0)
    time.sleep(.1)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_EXTENDEDKEY  | win32con.KEYEVENTF_KEYUP, 0)

def holdDown():
    win32api.keybd_event(win32con.VK_DOWN, 0, 1, 0)

def releaseDown():
    win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

def holdUp():
    win32api.keybd_event(win32con.VK_UP, 0, 1, 0)

def releaseUp():
    win32api.keybd_event(win32con.VK_UP, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

def holdRight():
    win32api.keybd_event(win32con.VK_RIGHT, 0, 1, 0)

def releaseRight():
    win32api.keybd_event(win32con.VK_RIGHT, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

def holdLeft():
    win32api.keybd_event(win32con.VK_LEFT, 0, 1, 0)

def releaseLeft():
    win32api.keybd_event(win32con.VK_LEFT, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

def holdSpace():
    win32api.keybd_event(win32con.VK_SPACE, 0, 1, 0)

def releaseSpace():
    win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

def leftCLick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

#move the mouse to a coordinate
def setMousePos(cord):
    win32api.SetCursorPos((x_pos + cord[0], y_pos + cord[1]))

#change the state of the mouse on target variable
def mouseIsOnTarget():
    global mouseOnTarget
    mouseOnTarget = True

def mouseNotTarget():
    global mouseOnTarget
    mouseOnTarget = False

def mouseOnScreen():
    x, y = get_cords()
    if x < 0 or x > 1400 or y < 0 or y > 905:
        return False
    return True

def get_cords():
    x,y = win32api.GetCursorPos()
    x = x - x_pos
    y = y - y_pos
    #print x,y
    return (x - 5, y - 5)

#calculate the output of the network
def runNetworks():
    output = calculate(getData(), networks[currentNet], numNeurons[currentNet], [378, 379, 380, 381, 382, 383])
    if output[0] > 0 and last[0] <= 0:
        holdUp()
    elif output[0] <= 0 and last[0] > 0:
        releaseUp()
    if output[1] > 0 and last[1] <= 0:
        holdDown()
    elif output[1] <= 0 and last[1] > 0:
        releaseDown()
    if output[2] > 0 and last[2] <= 0:
        holdLeft()
    elif output[2] <= 0 and last[2] > 0:
        releaseLeft()
    if output[3] > 0 and last[3] <= 0:
        holdRight()
    elif output[3] <= 0 and last[3] > 0:
        releaseRight()
    #if output[4] > .5 and last[3] <= .5:
    #    holdSpace()
    #elif output[4] <= .5 and last[3] > .5:
    #    releaseSpace()
    #if mouseOnScreen():
    #    angleMouse(output[5])
    if sameOut(output):
        streak = stk + 1
        incrementStk(streak)
    else:
        incrementStk(0)
    changeLast(output)
    if isLevelUp():
        #print "level end: " + str(lev_end - 1)
        #print "level start: " + str(lev_start - 1)
        try:
            fit = levelScores[lev_end - 1] - levelScores[lev_start - 1]
            incrementFit(fit)
        except IndexError:
            print "Index Error: starting level: " + str(lev_start) + " ending level: " + str(lev_end)
            fit = levelScores[prev_lev] - levelScores[lev_start - 1]
            setLev()
            incrementFit(fit)
    #if stk > 50:
    #    curr = (currentNet + 1) % len(fitness)
    #    incrementCurrNet(curr)
    #    incrementStk(0)
    #    incrementLife(0)
    #    holdSpace()
    liv = alive + 1
    incrementLife(liv)

def setLev():
    global lev_end
    lev_end = prev_lev + 1

def incrementStk(num):
    global stk
    stk = num

def incrementLife(num):
    global alive
    alive = num

def togglePlay(val):
    global playing
    if val == True:
        playing = False
    if val == False:
        playing = True

#old genetic algorithm implemented without speciation
def nextGeneration():
    max = 0
    maxIdx = 0
    for idx, score in enumerate(fitness):
        if score > max:
            max = score
            maxIdx = idx
    paths = networks[maxIdx]
    numNeu = numNeurons[maxIdx]
    print str(fitness[maxIdx])
    clearNetworks()
    if(max < 0):
        initializeNetworks()
        for i in range(5):
            fitness.append(0)
    else:
        networks.append(paths)
        numNeurons.append(numNeu)
        for i in range(5):
            fitness.append(0)
        inputs = []
        for i in range(126):
            inputs.append(i)
        outputs = [126, 127, 128, 129, 130, 131]
        for i in range(4):
            numN = numNeu
            pathways = copyPaths(paths)
            r = random.randint(2, 5)
            for j in range(r):
                pathways, numN = mutate(pathways, inputs, outputs, numN)
            networks.append(pathways)
            numNeurons.append(numN)
        gen = generation + 1
        incrementGen(gen)
        #print "Generation" + str(generation)

#new genetic algorithm implementing speciation
def nextGen():
    m = 0
    mI = 0
    for idx, score in enumerate(fitness):
        if score > m:
            m = score
            mI = idx
    print str(m)
    #Separate networks in species
    spec = []
    numSpec = 1
    spec.append(0)
    for i in range(1, len(networks)):
        match = False
        for j in range(0, i):
            if sameSpiecies(networks[j], networks[i]):
                spec.append(spec[j])
                match = True
                break
        if match == False:
            spec.append(numSpec)
            numSpec = numSpec + 1
    newNetworks = []
    newNumNeur = []
    #iterate through all species
    for i in range(0, numSpec):
        #find the best network in a species
        max = 0
        maxIdx = 0
        for idx, score in enumerate(fitness):
            if spec[idx] == i and score > max:
                max = score
                maxIdx = idx
        paths = networks[maxIdx]
        numNeu = numNeurons[maxIdx]
        #find the second best in a species
        sec = 0
        secId = 0
        for idx, score in enumerate(fitness):
            if spec[idx] == i and idx != maxIdx and score > sec:
                sec = score
                secId = idx
        paths2 = networks[secId]
        numNeu2 = numNeurons[secId]
        #breed the networks a random number of times
        rand = random.randint(1, 5)
        for x in range(rand):
            newPath, newNumn = breed(paths, numNeu, paths2, numNeu2)
            newNetworks.append(newPath)
            newNumNeur.append(newNumn)
    clearNetworks()
    clearPrevFrame()
    clearPrevFrame2()
    inputs = []
    for i in range(378):
        inputs.append(i)
    outputs = [378, 379, 380, 381, 382, 383]
    #iterate through all the new networks
    for h in range(len(newNetworks)):
        #randomly mutate the new networks and add them to the global arrays
        pathways = copyPaths(newNetworks[h])
        numN = newNumNeur[h]
        r = random.randint(2, 5)
        for j in range(r):
            pathways, numN = mutate(pathways, inputs, outputs, numN)
        networks.append(pathways)
        numNeurons.append(numN)
        fitness.append(0)
    #increment generation
    gen = generation + 1
    incrementGen(gen)

def clearPrevFrame():
    global prevFrame
    for i in range(126):
        prevFrame[i] = 0

def clearPrevFrame2():
    global prevFrame2
    for i in range(126):
        prevFrame2[i] = 0

#set the position of mouse based on the angle. input between 0 and 1
def angleMouse(r):
    rad = r * numpy.pi * 2
    cos = numpy.cos(rad)
    sin = numpy.sin(rad)
    x = 100*cos + 700
    y = 100*sin + 450
    setMousePos((int(x), int(y)))

def copyArr(arr):
    p = []
    for i in arr:
        p.append(i)
    return p

def copyPaths(path):
    p = []
    for i in path:
        p.append([i[0], i[1], i[2], i[3], i[4]])
    return p

def releaseAllKeys():
    releaseRight()
    releaseLeft()
    releaseUp()
    releaseDown()
    releaseSpace()

#reset neural networks
def clearNetworks():
    global networks
    global numNeurons
    global fitness
    networks = []
    numNeurons = []
    fitness = []

def incrementFit(fit):
    global fitness
    fitness[currentNet] = fit

def incrementGen(gen):
    global generation
    generation = gen

def incrementCurrNet(num):
    global currentNet
    currentNet = num
    releaseAllKeys()
    if num == 0:
        nextGen()

def changeLast(put):
    global last
    last = put

#determine if the network produced an identical output in a row
def sameOut(out):
    for i in range(len(out)):
        if out[i] != last[i]:
            return False
    return True

#start off with randomized networks
def initializeNetworks():
    inputs = []
    for i in range(126 * 3):
        inputs.append(i)
    outputs = [378, 379, 380, 381, 382, 383]
    for i in range(10):
        numN = 384
        pathways = []
        r = random.randint(2, 7)
        for j in range(r):
            pathways, numN = mutate(pathways, inputs, outputs, numN)
        networks.append(pathways)
        numNeurons.append(numN)

#find the output of a network given data about it
def calculate(inputs, pathways, numNeurons, outputs):
    neuralVals = []
    status = []
    for i in range(numNeurons):
        neuralVals.append(0)
        status.append(0)
    for i in range(14):
        for j in range(9):
            neuralVals[i * 9 + j] = inputs[i][j]
            status[i * 9 + j] = 2
    for i in range(126):
        neuralVals[i + 126] = prevFrame[i]
        status[i + 126] = 2
    for i in range(126):
        neuralVals[i + 252] = prevFrame2[i]
        status[i + 252] = 2
    updatePrevFrame2(prevFrame)
    updatePrevFrame(inputs)
    for i in range(14):
        for j in range(9):
            neuralVals[i * 9 + j] = inputs[i][j]
            status[i * 9 + j] = 2
    for idx, connection in enumerate(pathways):
        if moreCalcs(pathways, connection[0], idx):
            status[connection[0]] = 1
        if status[connection[0]] != 1:
            val = neuralVals[connection[0]] * connection[2]
            neuralVals[connection[1]] = neuralVals[connection[1]] + val
            status[connection[0]] = 2
    while True:
        if 1 in status:
            for idx, connection in enumerate(pathways):
                if status[connection[0]] == 1 and moreCalcs2(pathways, connection[0], idx, status) == False:
                    val = neuralVals[connection[0]] * connection[2]
                    neuralVals[connection[1]] = neuralVals[connection[1]] + val
                    if moreCalcs3(pathways, connection[0], idx, status) == False:
                        status[connection[0]] = 2
        else:
            break
    out = []
    for nnum in outputs:
        out.append(neuralVals[nnum])
    return out

def updatePrevFrame(inp):
    global prevFrame
    for i in range(14):
        for j in range(9):
            prevFrame[i * 9 + j] = inp[i][j]

def updatePrevFrame2(inp):
    global prevFrame2
    prevFrame2 = copyArr(inp)

def sigmoid(x):
    return 1 / (1 + numpy.exp(-x))

#determine if the final output of a network has been reached
def moreCalcs(pathways, neuron, start):
    for index in range(len(pathways)):
        if(index > start):
            if pathways[index][1] == neuron:
                return True
    return False

def moreCalcs2(pathways, neuron, start, status):
    for index in range(len(pathways)):
        if (index > start):
            if pathways[index][1] == neuron and status[pathways[index][0]] == 1:
                return True
    return False

def moreCalcs3(pathways, neuron, start, status):
    for index in range(len(pathways)):
        if (index > start):
            if pathways[index][0] == neuron:
                return True
    return False

def incrementInnovation(num):
    global innovation
    innovation = num + 1

#generate a new network by randomly passing on traits with certain innovation numbers
def breed(path1, numn1, path2, numn2):
    path = []
    numn = 0
    for connection in path1:
        if containsInnov(path2, connection[4]):
            path.append(connection)
        else:
            if random.random > 0.5:
                path.append(connection)
    for connection in path2:
        if not containsInnov(path1, connection[4]):
            if random.random > 0.5:
                path.append(connection)
    if numn1 > numn2:
        numn = numn1
    else:
        numn = numn2
    return path, numn

#compare the number of shared innovation numbers to see if the topology of two networks has sufficiently diverged to be separate species
def sameSpiecies(path1, path2):
    mismatch = 0
    for connection in path1:
        if not containsInnov(path2, connection[4]):
            mismatch = mismatch + 1
    for connection in path2:
        if not containsInnov(path1, connection[4]):
            mismatch = mismatch + 1
    if mismatch < 6:
        return True
    return False

#see if a network contains an innovation number
def containsInnov(path, num):
    for connection in path:
        if connection[4] == num:
            return True
    return False

#randomly mutate a network to have a new path, weight or bias. Each mutation is given an innovation number to keep track of it in future networks
def mutate(pathways, inputs, outputs, numNeurons):
    rand = random.randint(0, 4)
    neur = numNeurons
    path = pathways
    if(len(pathways) == 0):
        rand = 1
    if rand == 0:
        path = addNeuron(pathways, numNeurons)
        neur = neur + 1
    elif rand == 1:
        path = addConnection(pathways, inputs, outputs, numNeurons)
    elif rand == 2:
        path = pointMutate(pathways)
    elif rand == 3:
        neur = neur + 1
    elif rand == 4:
        path = toggleEnable(pathways)
    return path, neur

#change a weight
def pointMutate(pathways):
    r = random.randint(0, len(pathways) - 1)
    w = random.random()*2 - 1
    a = pathways[r][0]
    b = pathways[r][1]
    d = pathways[r][3]
    e = pathways[r][4]
    pathways[r] = [a, b, w, d, e]
    return pathways

#disable or enable a path
def toggleEnable(pathways):
    r = random.randint(0, len(pathways) - 1)
    a = pathways[r][0]
    b = pathways[r][1]
    c = pathways[r][2]
    e = pathways[r][4]
    if pathways[r][3] == 1:
        pathways[r] = [a, b, c, 0, e]
    else:
        pathways[r] = [a, b, c, 1, e]
    return pathways

#add a node
def addNeuron(pathways, numNeurons):
    split = random.randint(0, len(pathways) - 1)
    a = pathways[split][0]
    b = pathways[split][1]
    pathways[split] = [a, numNeurons, random.random()*2 - 1, 1, innovation]
    incrementInnovation(innovation)
    pathways.insert(split + 1, [numNeurons, b, random.random()*2 - 1, 1, innovation])
    incrementInnovation(innovation)
    return pathways

#add a path
def addConnection(pathways, inputs, outputs, numNeurons):
    startConnection = []
    for i in range(numNeurons):
        if i not in outputs:
            startConnection.append(i)
    endConnection = []
    for i in range(numNeurons):
        if i not in inputs:
            endConnection.append(i)
    num = 0
    while True:
        start = startConnection[random.randint(0, len(startConnection) - 1)]
        end = endConnection[random.randint(0, len(endConnection) - 1)]
        if connectionExists(start, end, pathways) == False:
            pathways.append([start, end, random.random()*2 - 1, 1, innovation])
            incrementInnovation(innovation)
            break
        num = num + 1
        if num > 10:
            break
    return pathways

def connectionExists(s, e, pathways):
    for path in pathways:
        if path[0] == s and path[1] == e:
            return True
        if path[1] == s and path[0] == e:
            return True
    return False

if __name__ == '__main__':
    main()

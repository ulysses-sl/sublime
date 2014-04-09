# sublim.py
""" Test suite for subliminal influence of image
    Copyright (c) 2014, Sak Lee
    All rights reserved.
    Released under FreeBSD license.

    1. Pre-survey
    2. Series of questions
    2-1. Cross for 1500ms
    2-2. Picture for 16ms
    2-3. Mask for 350ms
    2-4. Word until correct keypress
    3. Post-survey
    4. Save data
    (5. Repeat until 'r' or 'q')

    -A note to whoever maintains the code in the future:
    I know this code is ugly as crap and not Pythonic,
    but I don't have time to explore OOP system of Pyglet.
    """

import pyglet
from pyglet.window import key
from pyglet.gl import *
import csv
import sys
import time
import random
import itertools
import copy
import time
import math

sleep = lambda x: time.sleep(x / 1000)

#
# Globals
#
imgToBlit = None
wordToDisplay = None

#
# Window setting
#
color_bg = 132/255, 132/255, 132/255, 1
winWidth = 1366
winHeight = 768
window = pyglet.window.Window(winWidth, winHeight, fullscreen=True, vsync=True)
pyglet.clock.set_fps_limit(None)
fps = 60

timeCross = 1500
timePict = 16    # roughly at the multiples of 16, since 1 frame is 16.7ms
timeMask = 350


#
# Define all images
#
imgFace = dict()
for line in open('faces.txt'):
    lineList = line.split()
    if lineList[0] not in {'#', '##'}:
        imgFace[int(lineList[0])] = pyglet.resource.image(lineList[1])

imgMask = []
for line in open('masks.txt'):
    lineList = line.split()
    if lineList[0] not in {'#', '##'}:
        imgMask.append(pyglet.resource.image(lineList[1]))

imgCross = pyglet.resource.image('faces/00Cross.jpeg')
imgEmpty = pyglet.resource.image('faces/00Empty.jpeg')


#
# Center the images
#
def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width/2
    image.anchor_y = image.height/2

for face in imgFace.values():
    center_image(face)
for mask in imgMask:
    center_image(mask)
center_image(imgCross)
center_image(imgEmpty)


#
# Prepare word dictionary
#
wordDict = {}
wordDivide, wordTemp = 0, 0
for line in open('words.txt'):
    lineList = line.split()
    if lineList[0] not in {'#', '##'}:
        wordDict[int(lineList[0])] = lineList[1]
        wordTemp = int(lineList[0])
    elif lineList[0] == '##':
        wordDivide = wordTemp


#
# Permutation of face:word
#
allQuestions = list(itertools.product(imgFace.keys(), wordDict.keys()))


#
# Basic Labels
#
textControl = pyglet.text.Label(
    'Q: quit / R: restart',
    font_name='Times New Roman',
    font_size=16, color=(0, 0, 0, 255),
    x=window.width-120, y=window.height-50, bold=True,
    anchor_x='center', anchor_y='center')

textRoom = pyglet.text.Label(
    'Z: Room',
    font_name='Times New Roman',
    font_size=20, color=(0, 0, 0, 255),
    x=100, y=50, bold=True,
    anchor_x='center', anchor_y='center')

textPerson = pyglet.text.Label(
    '/: Person',
    font_name='Times New Roman',
    font_size=20, color=(0, 0, 0, 255),
    x=window.width-100, y=50, bold=True,
    anchor_x='center', anchor_y='center')

textProceed = pyglet.text.Label(
    'Tab: next / C: continue.',
    font_name='Times New Roman',
    font_size=30, color=(0, 0, 0, 255),
    x=window.width/2, y=50, bold=True,
    anchor_x='center', anchor_y='center')

strID = "ID #: "
strGender = "Gender: "

#
# Input cases
#
inputNumber = {key.NUM_0: 0, key.NUM_1: 1, key.NUM_2: 2,
               key.NUM_3: 3, key.NUM_4: 4, key.NUM_5: 5,
               key.NUM_6: 6, key.NUM_7: 7, key.NUM_8: 8, key.NUM_9: 9}

inputControl = {key.BACKSPACE, key.UP, key.DOWN, key.C}


def legalInput(symbol):
    return symbol in inputNumber or symbol in inputControl


#
# Control Structure
#
class TestSuite:
    def __init__(self):
        # programPhase
        # 0: pre-survey
        # 1: practice
        # 2: questions
        # 3: post-survey
        # 4: savedata
        self.programPhase = 'pre-survey'
        # questionPhase
        # 0: load
        # 1: cross
        # 2: face
        # 3: mask
        # 4: word
        self.questionPhase = 'load'

        # Copy from original question list and shuffle it
        self.questionList = copy.deepcopy(allQuestions)
        random.shuffle(self.questionList)
        # tuple of (face#, word#)
        self.currentQuestion = None
        # use by resultList.append((*currentQuestion, answer, reactionTime))
        self.resultList = []

        # image to display
        self.img = imgCross
        # face to display
        self.face = None
        # word to display
        self.word = None
        # mask to display
        self.mask = None

        # timer for counting time
        self.timer = 0
        # was there any key input?
        self.receivedInput = False
        # transition between phases
        self.proceed = False
        # how long does it take to draw and erase a frame?
        self.debugFaceTime = 0
        # on which element of survey you are working on?
        self.cursorFocus = 0
        # was data saved?
        self.savedData = False

        # finished pre-survey?
        self.preSurveyDone = False
        # id # of the test subject
        self.id = ''
        # gender: 1=Male, 2=Female, 3=Other, 0=X
        self.gender = 0
        # ethnicity
        # 1=White
        # 2=Black
        # 3=Hisp/Lat
        # 4=Asian
        # 5=NatAm
        # 6=Mult
        # 0=X
        self.ethnicity = 0
        # age
        self.age = 0

        # finished post-survey?
        self.postSurveyDone = False
        # Political orientation, 1 to 7
        self.polDem = 0  # democrats
        self.polRep = 0  # republicans
        self.polInd = 0  # independents
        self.polLib = 0  # liberals
        self.polCon = 0  # conservatives

    def reset(self):
        # create random order of questions
        self.questionList = copy.deepcopy(allQuestions)
        random.shuffle(self.questionList)
        # reset everything
        self.programPhase = 'questions'
        self.questionPhase = 'load'

        self.currentQuestion = None
        self.resultList = []

        self.img = imgCross
        self.face = None
        self.word = None
        self.mask = None

        self.timer = 0
        self.receivedInput = False
        self.proceed = False
        self.debugFaceTime = 0
        self.cursorFocus = 0
        self.savedData = False

        self.preSurveyDone = False
        self.id = ''
        self.gender = 0
        self.ethnicity = 0
        self.age = 0

        self.postSurveyDone = False
        self.polDem = 0
        self.polRep = 0
        self.polInd = 0
        self.polLib = 0
        self.polCon = 0

    def loadQuestion(self):
        self.currentQuestion = self.questionList.pop()
        self.face = imgFace[self.currentQuestion[0]]
        self.word = pyglet.text.Label(
            wordDict[self.currentQuestion[1]],
            font_name='Times New Roman',
            font_size=42, color=(0, 0, 0, 255),
            x=window.width/2, y=window.height/2,
            anchor_x='center', anchor_y='center')
        self.mask = random.choice(imgMask)

    def answerInput(self, answer):
        self.appendAnswer(answer)
        self.receivedInput = True

    def appendAnswer(self, answer):
        if self.receivedInput:
            return
        if (answer == 'Upper' and self.currentQuestion[1] > wordDivide) or \
           (answer == 'Lower' and self.currentQuestion[1] <= wordDivide):
            correct = 1
        else:
            correct = 0

        numFace, numWord = self.currentQuestion
        resultTuple = numFace, numWord, correct, self.timer
        self.resultList.append(resultTuple)

        debugStr = str(correct) + ', ' + str(int(self.timer)) + " ms"
        self.debugText = pyglet.text.Label(
            debugStr,
            font_name='Times New Roman',
            font_size=42, color=(0, 0, 0, 255),
            x=window.width/2, y=window.height/2,
            anchor_x='center', anchor_y='center')

    def advanceProgramPhase(self):
        self.programPhase = (self.programPhase + 1) % 4

    def advanceQuestionPhase(self):
        self.timer = 0
        self.questionPhase = (self.questionPhase + 1) % 6

    def relayInput(self, symbol):
        if self.programPhase == 0:
            if symbol == key.C:
                self.preSurveyDone = True
        elif self.programPhase == 2:
            if symbol == key.C:
                self.postSurveyDone = True

    def update(self, dt):
        if self.programPhase == 0:
            if self.preSurveyDone:
                self.advanceProgramPhase()

        elif self.programPhase == 1:
            if self.questionPhase == 0:  # Load question
                self.advanceQuestionPhase()
                self.loadQuestion()
                self.img = imgCross

            elif self.questionPhase == 1:  # Show cross
                self.timer += 1000/fps
                if self.timer >= timeCross:
                    print("question :" + str(self.currentQuestion))
                    self.advanceQuestionPhase()
                    self.img = self.face
                    self.debugFaceTime = time.time()

            elif self.questionPhase == 2:  # Show face
                self.timer += 1000/fps
                if self.timer >= timePict:
                    self.advanceQuestionPhase()
                    self.img = self.mask
                    ms = math.floor(1000 * (time.time() - self.debugFaceTime))
                    print("displayed for " + str(ms) + " ms")
                    self.debugFaceTime = 0

            elif self.questionPhase == 3:  # Show mask
                self.timer += 1000/fps
                if self.timer >= timeMask:
                    self.advanceQuestionPhase()
                    self.img = imgCross

            elif self.questionPhase == 4:
                self.timer += 1000/fps
                if self.receivedInput:
                    self.receivedInput = False
                    self.advanceQuestionPhase()
                    if not self.questionList:
                        self.programPhase = 2

            elif self.questionPhase == 5:
                self.timer += 1000/fps
                if self.timer >= 1500:
                    self.advanceQuestionPhase()

        elif self.programPhase == 2:
            if self.postSurveyDone:
                self.advanceProgramPhase()

        elif self.programPhase == 3:
            if not self.savedData:
                self.save()
            self.timer += 1000/fps
            if self.timer >= 5000:
                self.reset()


program = TestSuite()

pyglet.clock.schedule_interval(program.update, 1/fps)

faceMaskFlag = False


@window.event
def on_draw():
    global faceMaskFlag
    pyglet.gl.glClearColor(*color_bg)
    window.clear()
    # Label for quit and restart
    textControl.draw()

    if program.programPhase == 0:
        textProceed.draw()

    elif program.programPhase == 1:
        textRoom.draw()
        textPerson.draw()
        if program.questionPhase in {1, 2, 3}:
            program.img.blit(winWidth / 2, winHeight / 2)
            if program.img == program.face:
                print("face drawn!")
                faceMaskFlag = True
            elif faceMaskFlag and program.img == program.mask:
                print("masked!\n")
                faceMaskFlag = False
        elif program.questionPhase == 4:
            program.word.draw()
        elif program.questionPhase == 5:
            program.debugText.draw()

    elif program.programPhase == 2:
        textProceed.draw()

    elif program.programPhase == 3:
        pass


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE:
        return True
    elif symbol == key.Q:
        window.on_close()
    elif symbol == key.R:
        program.reset()
    elif program.programPhase == 0:
        if legalInput(symbol):
            program.relayInput(symbol)
    elif program.programPhase == 1 and program.questionPhase == 4:
        if symbol == key.SLASH:
            program.answerInput('Lower')
        if symbol == key.Z:
            program.answerInput('Upper')


def main():
    pyglet.app.run()

if __name__ == "__main__":
    main()

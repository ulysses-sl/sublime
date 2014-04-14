# sublim.py
""" Test suite for subliminal influence of image
    Copyright (c) 2014, Sak Lee
    All rights reserved.
    Released under FreeBSD license.

    1. Pre-survey
    2. Practice Trial
    3. Series of questions
    3-1. Cross for 1500ms
    3-2. Picture for 16ms
    3-3. Mask for 350ms
    3-4. Word until correct keypress
    4. Post-survey
    5. Save data
    (6. Repeat until 'r' or 'q')
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
import math
import time
import datetime

sleep = lambda x: time.sleep(x / 1000)

#
# Globals
#

#
# Window setting
#
color_bg = 132/255, 132/255, 132/255, 1
winWidth = 1366
winHeight = 768
window = pyglet.window.Window(winWidth, winHeight, fullscreen=True, vsync=True)
pyglet.clock.set_fps_limit(None)
fps = 60
timePerFrame = 1000 / fps
howManyFrames = 1 # Change this to change display time

timeCross = 1500
timePict = math.floor(timePerFrame * howManyFrames) - 1
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
def centerImage(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width/2
    image.anchor_y = image.height/2

for face in imgFace.values():
    centerImage(face)
for mask in imgMask:
    centerImage(mask)
centerImage(imgCross)
centerImage(imgEmpty)


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
# Practice Trial
#
testFaceNum = max(imgFace.keys()) + 1
testWordNum = max(wordDict.keys()) + 1

practiceQuestions = []

for line in open('practice.txt'):
    lineList = line.split()
    if lineList[0] not in {'#', '##'}:
        imgFace[testFaceNum] = pyglet.resource.image(lineList[1])
        wordDict[testWordNum] = lineList[2]
        centerImage(imgFace[testFaceNum])
        practiceQuestions.append((testFaceNum, testWordNum))
        testFaceNum += 1
        testWordNum += 1


#
# Basic Labels
#
textControl = pyglet.text.Label(
    'Q: quit / R: restart',
    font_name='Helvetica',
    font_size=16, color=(0, 0, 0, 255),
    x=window.width-220, y=window.height-50, bold=True,
    anchor_x='left', anchor_y='center')

textRoom = pyglet.text.Label(
    'Z: Room',
    font_name='Helvetica',
    font_size=20, color=(0, 0, 0, 255),
    x=100, y=50, bold=True,
    anchor_x='center', anchor_y='center')

textPerson = pyglet.text.Label(
    '/: Person',
    font_name='Helvetica',
    font_size=20, color=(0, 0, 0, 255),
    x=window.width-100, y=50, bold=True,
    anchor_x='center', anchor_y='center')

textContinue = pyglet.text.Label(
    'C: continue',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=window.width/2, y=50, bold=True,
    anchor_x='center', anchor_y='center')

textNav = pyglet.text.Label(
    'Arrows: navigate',
    font_name='Helvetica',
    font_size=16, color=(0, 0, 0, 255),
    x=window.width-220, y=window.height-80, bold=True,
    anchor_x='left', anchor_y='center')

textInst = pyglet.text.Label(
    'Instructions:',
    font_name='Helvetica',
    font_size=40, color=(0, 0, 0, 255),
    x=20, y=window.height-100, bold=True,
    anchor_x='left', anchor_y='center')

textInstBody1 = pyglet.text.Label(
    'Please first focus on the crosshatch in the center of the screen. You',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=20, y=window.height-200, bold=True,
    anchor_x='left', anchor_y='center')

textInstBody2 = pyglet.text.Label(
    'may see a flash, and a descriptor will appear that can describe either',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=20, y=window.height-275, bold=True,
    anchor_x='left', anchor_y='center')

textInstBody3 = pyglet.text.Label(
    'a ROOM or a PERSON. Your task is to press either the "ROOM" or the',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=20, y=window.height-350, bold=True,
    anchor_x='left', anchor_y='center')

textInstBody4 = pyglet.text.Label(
    '"PERSON" key as quickly as possible while being accurate.',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=20, y=window.height-425, bold=True,
    anchor_x='left', anchor_y='center')

textInstBody5 = pyglet.text.Label(
    'You will get two practice trials. When you are ready to begin,',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=20, y=window.height-500, bold=True,
    anchor_x='left', anchor_y='center')

textInstBody6 = pyglet.text.Label(
    'press CONTINUE.',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=20, y=window.height-575, bold=True,
    anchor_x='left', anchor_y='center')

textPracticeEnd1 = pyglet.text.Label(
    'End of the practice trial.',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=window.width/2, y=window.height-200, bold=True,
    anchor_x='center', anchor_y='center')

textPracticeEnd2 = pyglet.text.Label(
    'The actual test begins.',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=window.width/2, y=window.height-300, bold=True,
    anchor_x='center', anchor_y='center')

textTestEnd = pyglet.text.Label(
    'Finished. Thank you.',
    font_name='Helvetica',
    font_size=30, color=(0, 0, 0, 255),
    x=window.width/2, y=window.height/2, bold=True,
    anchor_x='center', anchor_y='center')


#
# Input cases
#
inputNumber = {key.NUM_0: 0, key.NUM_1: 1, key.NUM_2: 2,
               key.NUM_3: 3, key.NUM_4: 4, key.NUM_5: 5,
               key.NUM_6: 6, key.NUM_7: 7, key.NUM_8: 8, key.NUM_9: 9,
               key._0: 0, key._1: 1, key._2: 2,
               key._3: 3, key._4: 4, key._5: 5,
               key._6: 6, key._7: 7, key._8: 8, key._9: 9}

inputControl = {key.BACKSPACE, key.UP, key.DOWN, key.LEFT, key.RIGHT, key.C}


def legalInput(symbol):
    return symbol in inputNumber or symbol in inputControl


#
# Control Structure
#
class TestSuite:
    """Contains the actual test material."""
    def __init__(self):
        # programPhase
        # 0: pre-survey
        # 1: instruction
        # 2: practice
        # 3: pause
        # 4: questions
        # 5: post-survey
        # 6: savedata
        self.programPhase = 'pre-survey'
        # questionPhase
        # 0: load
        # 1: cross
        # 2: face
        # 3: mask
        # 4: word
        self.questionPhase = 'load'

        # Copy from original question list and shuffle it
        self.questionList = copy.deepcopy(practiceQuestions)
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
        self.cursorFocus = 'id'
        # was data saved?
        self.savedData = False
        # does user want to continue?
        self.continueFlag = False

        self.varSurveyList = ['id', 'age', 'gender', 'ethnicity',
                              'polDem', 'polRep', 'polInd', 'polLib', 'polCon']

        self.varSurvey = {'id': 0, 'age': 0, 'gender': 0, 'ethnicity': 0,
                          'polDem': 4, 'polRep': 4, 'polInd': 4,
                          'polLib': 4, 'polCon': 4}

        # id # of the test subject
        #
        # age
        #
        # gender: 1=Male, 2=Female, 3=Other, 0=X
        #
        # ethnicity
        # 1=White
        # 2=Black
        # 3=Hisp/Lat
        # 4=Asian
        # 5=NatAm
        # 6=Mult
        # 0=X
        #
        # Political orientation, 1 to 7
        # polDem = 4  # democrats
        # polRep = 4  # republicans
        # polInd = 4  # independents
        # polLib = 4  # liberals
        # polCon = 4  # conservatives

        # range for all survey items
        self.varSurveyRange = {
            'id': range(10000000), 'age': range(100),
            'gender': range(4), 'ethnicity': range(7),
            'polDem': range(1, 8), 'polRep': range(1, 8),
            'polInd': range(1, 8), 'polLib': range(1, 8),
            'polCon': range(1, 8)}

    def reset(self):
        # create random order of questions
        self.questionList = copy.deepcopy(practiceQuestions)
        random.shuffle(self.questionList)
        # reset everything
        self.programPhase = 'pre-survey'
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
        self.cursorFocus = 'id'
        self.savedData = False
        self.continueFlag = False

        self.varSurvey = {'id': 0, 'age': 0, 'gender': 0, 'ethnicity': 0,
                          'polDem': 4, 'polRep': 4, 'polInd': 4,
                          'polLib': 4, 'polCon': 4}

# ################### Pre-survey questions ####################

    def textId(self):
        selected = self.cursorFocus == 'id'
        labelText = None
        if selected:
            labelText = '-> ID:'
        else:
            labelText = 'ID:'

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=40, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height/2+300, bold=True,
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                str(self.varSurvey['id']),
                font_name='Helvetica',
                font_size=40, color=(0, 0, 0, 255),
                x=window.width/2, y=window.height/2+300, bold=False,
                anchor_x='right', anchor_y='center')]

        return textList

    def textAge(self):
        selected = self.cursorFocus == 'age'
        labelText = None
        if selected:
            labelText = '-> Age:'
        else:
            labelText = 'Age:'

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=40, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height/2+210, bold=True,
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                str(self.varSurvey['age']),
                font_name='Helvetica',
                font_size=40, color=(0, 0, 0, 255),
                x=window.width/2-300, y=window.height/2+210, bold=False,
                anchor_x='right', anchor_y='center')]

        return textList

    def textListGender(self):
        selected = self.cursorFocus == 'gender'
        labelText = None
        if selected:
            labelText = '-> Gender:'
        else:
            labelText = 'Gender:'
        colorList = []
        boldList = []
        for i in range(4):
            if i == self.varSurvey['gender']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=40, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height/2+120, bold=True,
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '1) Male',
                font_name='Helvetica',
                font_size=30, color=colorList[1],
                x=window.width/2-600, y=window.height/2+50, bold=boldList[1],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '2) Female',
                font_name='Helvetica',
                font_size=30, color=colorList[2],
                x=window.width/2-200, y=window.height/2+50, bold=boldList[2],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '3) Other',
                font_name='Helvetica',
                font_size=30, color=colorList[3],
                x=window.width/2+200, y=window.height/2+50, bold=boldList[3],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '0) I prefer not to say',
                font_name='Helvetica',
                font_size=30, color=colorList[0],
                x=window.width/2-600, y=window.height/2, bold=boldList[0],
                anchor_x='left', anchor_y='center')]

        return textList

    def textListEthnicity(self):
        selected = self.cursorFocus == 'ethnicity'
        labelText = None
        if selected:
            labelText = '-> Ethnicity:'
        else:
            labelText = 'Ethnicity:'
        colorList = []
        boldList = []
        for i in range(7):
            if i == self.varSurvey['ethnicity']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=40, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height/2-80, bold=True,
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '1) White',
                font_name='Helvetica',
                font_size=30, color=colorList[1],
                x=window.width/2-600, y=window.height/2-150, bold=boldList[1],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '2) Black',
                font_name='Helvetica',
                font_size=30, color=colorList[2],
                x=window.width/2-200, y=window.height/2-150, bold=boldList[2],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '3) Hispanic/Latino(a)',
                font_name='Helvetica',
                font_size=30, color=colorList[3],
                x=window.width/2+200, y=window.height/2-150, bold=boldList[3],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '4) Asian',
                font_name='Helvetica',
                font_size=30, color=colorList[4],
                x=window.width/2-600, y=window.height/2-200, bold=boldList[4],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '5) Native American',
                font_name='Helvetica',
                font_size=30, color=colorList[5],
                x=window.width/2-200, y=window.height/2-200, bold=boldList[5],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '6) Biracial/Multiracial',
                font_name='Helvetica',
                font_size=30, color=colorList[6],
                x=window.width/2+200, y=window.height/2-200, bold=boldList[6],
                anchor_x='left', anchor_y='center'),
            pyglet.text.Label(
                '0) I prefer not to say',
                font_name='Helvetica',
                font_size=30, color=colorList[0],
                x=window.width/2-600, y=window.height/2-250, bold=boldList[0],
                anchor_x='left', anchor_y='center')]

        return textList

# ################### Post-survey questions ####################

    def textPostSurvey(self):
        labelText = 'To what degree do you identify with the following groups?'
        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=30, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height-120, bold=True,
                anchor_x='left', anchor_y='center')]
        return textList

    def textDemocrats(self):
        selected = self.cursorFocus == 'polDem'
        labelText = None
        if selected:
            labelText = '-> Democrats:'
        else:
            labelText = 'Democrats:'
        colorList = [0]
        boldList = [0]
        for i in self.varSurveyRange['polDem']:
            if i == self.varSurvey['polDem']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=30, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height-200, bold=True,
                anchor_x='left', anchor_y='center')]
        for i in self.varSurveyRange['polRep']:
            textList.append(
                pyglet.text.Label(
                    str(i),
                    font_name='Helvetica',
                    font_size=30, color=colorList[i],
                    x=window.width/2-400+100*i, y=window.height-250,
                    bold=boldList[i], anchor_x='right', anchor_y='center'))

        return textList

    def textRepublicans(self):
        selected = self.cursorFocus == 'polRep'
        labelText = None
        if selected:
            labelText = '-> Republicans:'
        else:
            labelText = 'Republicans:'
        colorList = [0]
        boldList = [0]
        for i in self.varSurveyRange['polRep']:
            if i == self.varSurvey['polRep']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=30, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height-300, bold=True,
                anchor_x='left', anchor_y='center')]
        for i in self.varSurveyRange['polRep']:
            textList.append(
                pyglet.text.Label(
                    str(i),
                    font_name='Helvetica',
                    font_size=30, color=colorList[i],
                    x=window.width/2-400+100*i, y=window.height-350,
                    bold=boldList[i], anchor_x='right', anchor_y='center'))

        return textList

    def textIndependents(self):
        selected = self.cursorFocus == 'polInd'
        labelText = None
        if selected:
            labelText = '-> Independents:'
        else:
            labelText = 'Independents:'
        colorList = [0]
        boldList = [0]
        for i in self.varSurveyRange['polInd']:
            if i == self.varSurvey['polInd']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=30, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height-400, bold=True,
                anchor_x='left', anchor_y='center')]
        for i in self.varSurveyRange['polRep']:
            textList.append(
                pyglet.text.Label(
                    str(i),
                    font_name='Helvetica',
                    font_size=30, color=colorList[i],
                    x=window.width/2-400+100*i, y=window.height-450,
                    bold=boldList[i], anchor_x='right', anchor_y='center'))

        return textList

    def textLiberals(self):
        selected = self.cursorFocus == 'polLib'
        labelText = None
        if selected:
            labelText = '-> Liberals:'
        else:
            labelText = 'Liberals:'
        colorList = [0]
        boldList = [0]
        for i in self.varSurveyRange['polLib']:
            if i == self.varSurvey['polLib']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=30, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height-500, bold=True,
                anchor_x='left', anchor_y='center')]
        for i in self.varSurveyRange['polRep']:
            textList.append(
                pyglet.text.Label(
                    str(i),
                    font_name='Helvetica',
                    font_size=30, color=colorList[i],
                    x=window.width/2-400+100*i, y=window.height-550,
                    bold=boldList[i], anchor_x='right', anchor_y='center'))

        return textList

    def textConservatives(self):
        selected = self.cursorFocus == 'polCon'
        labelText = None
        if selected:
            labelText = '-> Conservatives:'
        else:
            labelText = 'Conservatives:'
        colorList = [0]
        boldList = [0]
        for i in self.varSurveyRange['polCon']:
            if i == self.varSurvey['polCon']:
                colorList.append((180, 0, 0, 255))
                boldList.append(True)
            else:
                colorList.append((0, 0, 0, 255))
                boldList.append(False)

        textList = [
            pyglet.text.Label(
                labelText,
                font_name='Helvetica',
                font_size=30, color=(0, 0, 0, 255),
                x=window.width/2-600, y=window.height-600, bold=True,
                anchor_x='left', anchor_y='center')]
        for i in self.varSurveyRange['polRep']:
            textList.append(
                pyglet.text.Label(
                    str(i),
                    font_name='Helvetica',
                    font_size=30, color=colorList[i],
                    x=window.width/2-400+100*i, y=window.height-650,
                    bold=boldList[i], anchor_x='right', anchor_y='center'))

        return textList

# ################### Flow Control ####################

    def loadQuestion(self):
        self.currentQuestion = self.questionList.pop()
        self.face = imgFace[self.currentQuestion[0]]
        self.word = pyglet.text.Label(
            wordDict[self.currentQuestion[1]],
            font_name='Helvetica',
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
            font_name='Helvetica',
            font_size=42, color=(0, 0, 0, 255),
            x=window.width/2, y=window.height/2,
            anchor_x='center', anchor_y='center')

    def advanceProgramPhase(self):
        self.continueFlag = False

        if self.programPhase == 'pre-survey':
            self.programPhase = 'instruction'
            self.cursorFocus = 'polDem'

        elif self.programPhase == 'instruction':
            self.programPhase = 'practice'

        elif self.programPhase == 'practice':
            self.programPhase = 'pause'

        elif self.programPhase == 'pause':
            self.programPhase = 'questions'

        elif self.programPhase == 'questions':
            self.programPhase = 'post-survey'

        elif self.programPhase == 'post-survey':
            self.programPhase = 'savedata'

        elif self.programPhase == 'savedata':
            self.reset()

    def advanceQuestionPhase(self):
        self.timer = 0

        if self.questionPhase == 'load':
            self.questionPhase = 'cross'

        elif self.questionPhase == 'cross':
            self.questionPhase = 'face'

        elif self.questionPhase == 'face':
            self.questionPhase = 'mask'

        elif self.questionPhase == 'mask':
            self.questionPhase = 'word'

        elif self.questionPhase == 'word':
            self.questionPhase = 'load'

    def advanceSurveyPhase(self, symbol):
        # Down key
        if symbol == key.DOWN:
            # Pre-survey
            if self.cursorFocus == 'id':
                self.cursorFocus = 'age'
            elif self.cursorFocus == 'age':
                self.cursorFocus = 'gender'
            elif self.cursorFocus == 'gender':
                self.cursorFocus = 'ethnicity'
            elif self.cursorFocus == 'ethnicity':
                self.cursorFocus = 'id'
            # Post-survey
            elif self.cursorFocus == 'polDem':
                self.cursorFocus = 'polRep'
            elif self.cursorFocus == 'polRep':
                self.cursorFocus = 'polInd'
            elif self.cursorFocus == 'polInd':
                self.cursorFocus = 'polLib'
            elif self.cursorFocus == 'polLib':
                self.cursorFocus = 'polCon'
            elif self.cursorFocus == 'polCon':
                self.cursorFocus = 'polDem'
        # Up key
        else:
            # Pre-survey
            if self.cursorFocus == 'id':
                self.cursorFocus = 'ethnicity'
            elif self.cursorFocus == 'age':
                self.cursorFocus = 'id'
            elif self.cursorFocus == 'gender':
                self.cursorFocus = 'age'
            elif self.cursorFocus == 'ethnicity':
                self.cursorFocus = 'gender'
            # Post-survey
            elif self.cursorFocus == 'polDem':
                self.cursorFocus = 'polCon'
            elif self.cursorFocus == 'polRep':
                self.cursorFocus = 'polDem'
            elif self.cursorFocus == 'polInd':
                self.cursorFocus = 'polRep'
            elif self.cursorFocus == 'polLib':
                self.cursorFocus = 'polInd'
            elif self.cursorFocus == 'polCon':
                self.cursorFocus = 'polLib'

    def relayInput(self, symbol):
        if symbol == key.C:
            program.continueFlag = True
        elif self.programPhase in {'pre-survey', 'post-survey'}:
            if symbol in {key.UP, key.DOWN}:
                self.advanceSurveyPhase(symbol)
            elif self.cursorFocus in {'id', 'age'}:
                if symbol == key.BACKSPACE:
                    self.deleteDigit()
                elif symbol in inputNumber.keys():
                    self.addDigit(inputNumber[symbol])
            elif symbol in inputNumber.keys() and \
                    inputNumber[symbol] in \
                    self.varSurveyRange[self.cursorFocus]:
                self.chooseAnswer(inputNumber[symbol])
            elif self.programPhase == 'post-survey' and \
                    symbol in {key.LEFT, key.RIGHT}:
                self.moveLeftRight(symbol)

    def deleteDigit(self):
        self.varSurvey[self.cursorFocus] //= 10

    def addDigit(self, num):
        currVal = self.varSurvey[self.cursorFocus]
        if currVal * 10 in self.varSurveyRange[self.cursorFocus]:
            self.varSurvey[self.cursorFocus] = 10 * currVal + num

    def chooseAnswer(self, num):
        self.varSurvey[self.cursorFocus] = num

    def moveLeftRight(self, symbol):
        if symbol == key.LEFT:
            if self.varSurvey[self.cursorFocus] - 1 in \
                    self.varSurveyRange[self.cursorFocus]:
                self.varSurvey[self.cursorFocus] -= 1
        if symbol == key.RIGHT:
            if self.varSurvey[self.cursorFocus] + 1 in \
                    self.varSurveyRange[self.cursorFocus]:
                self.varSurvey[self.cursorFocus] += 1

    def save(self):
        self.savedData = True
        savedata = []
        for item in self.varSurveyList:
            savedata.append(self.varSurvey[item])
            savedata.append(',')
        self.resultList.sort()
        print(self.resultList)
        del savedata[-1]
        for question in self.resultList:
            savedata.append(',')
            savedata.append(question[2])
            savedata.append(',')
            savedata.append(round(question[3],2))
        entirecsv = []
        with open('savedata/savedata.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                entirecsv.append(row)
        entirecsv.append(savedata)
        with open('savedata/savedata.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for eachLine in entirecsv:
                writer.writerow(eachLine)

    def update(self, dt):
        if self.programPhase in {'pre-survey',
                                 'post-survey',
                                 'instruction',
                                 'pause'}:
            if self.continueFlag:
                if self.programPhase == 'pause':
                    self.questionList = copy.deepcopy(allQuestions)
                    random.shuffle(self.questionList)
                self.advanceProgramPhase()

        elif self.programPhase in {'questions', 'practice'}:
            if self.questionPhase == 'load':  # Load question
                self.advanceQuestionPhase()
                self.loadQuestion()
                self.img = imgCross

            elif self.questionPhase == 'cross':  # Show cross
                self.timer += 1000/fps
                if self.timer >= timeCross:
                    print("question :" + str(self.currentQuestion))
                    self.advanceQuestionPhase()
                    self.img = self.face
                    self.debugFaceTime = time.time()

            elif self.questionPhase == 'face':  # Show face
                self.timer += 1000/fps
                if self.timer >= timePict:
                    self.advanceQuestionPhase()
                    self.img = self.mask
                    ms = math.floor(1000 * (time.time() - self.debugFaceTime))
                    print("displayed for " + str(ms) + " ms")
                    self.debugFaceTime = 0

            elif self.questionPhase == 'mask':  # Show mask
                self.timer += 1000/fps
                if self.timer >= timeMask:
                    self.advanceQuestionPhase()
                    self.img = imgCross

            elif self.questionPhase == 'word':  # Show word
                self.timer += 1000/fps
                if self.receivedInput:
                    self.receivedInput = False
                    self.advanceQuestionPhase()
                    if not self.questionList:
                        self.advanceProgramPhase()

        elif self.programPhase == 'savedata':
            if not self.savedData:
                self.save()
            self.timer += 1000/fps
            if self.timer >= 5000:
                self.reset()


program = TestSuite()

pyglet.clock.schedule_interval(program.update, 1/fps)

# to see when does the mask set off
faceMaskFlag = False


@window.event
def on_draw():
    global faceMaskFlag
    pyglet.gl.glClearColor(*color_bg)
    window.clear()
    # Label for quit and restart
    textControl.draw()

    if program.programPhase in {'practice', 'questions'}:
        textRoom.draw()
        textPerson.draw()
        if program.questionPhase in {'cross', 'face', 'mask'}:
            program.img.blit(winWidth / 2, winHeight / 2)
            if program.img == program.face:
                print("face drawn!")
                faceMaskFlag = True
            elif faceMaskFlag and program.img == program.mask:
                print("masked!\n")
                faceMaskFlag = False
        elif program.questionPhase == 'word':
            program.word.draw()

    elif program.programPhase == 'pre-survey':
        textContinue.draw()
        textNav.draw()
        allText = program.textId() + program.textAge() + \
            program.textListGender() + program.textListEthnicity()
        for text in allText:
            text.draw()

    elif program.programPhase == 'post-survey':
        textContinue.draw()
        textNav.draw()
        allText = program.textPostSurvey() + program.textDemocrats() + \
            program.textRepublicans() + program.textIndependents() + \
            program.textLiberals() + program.textConservatives()
        for text in allText:
            text.draw()

    elif program.programPhase == 'instruction':
        textContinue.draw()
        textInst.draw()
        textInstBody1.draw()
        textInstBody2.draw()
        textInstBody3.draw()
        textInstBody4.draw()
        textInstBody5.draw()
        textInstBody6.draw()

    elif program.programPhase == 'pause':
        textContinue.draw()
        textPracticeEnd1.draw()
        textPracticeEnd2.draw()

    elif program.programPhase == 'savedata':
        textTestEnd.draw()


@window.event
def on_key_press(symbol, modifiers):
    print(program.programPhase)
    if symbol == key.ESCAPE:
        return True
    elif symbol == key.Q:
        window.on_close()
    elif symbol == key.R:
        program.reset()
    elif program.programPhase in {'pre-survey',
                                  'instruction',
                                  'pause',
                                  'post-survey'}:
        program.relayInput(symbol)
    elif program.programPhase in {'practice', 'questions'} and \
            program.questionPhase == 'word':
        if symbol == key.SLASH:
            program.answerInput('Lower')
        if symbol == key.Z:
            program.answerInput('Upper')


def main():
    pyglet.app.run()

if __name__ == "__main__":
    main()

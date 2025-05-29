# importing libraries etc
import os,random,sys,math,json,requests,serial
from psychopy import event, visual, gui, core




#-----------------------------------
#  Setting up Psychopy
#-----------------------------------

# variable with the window's settings
win=visual.Window(fullscr=True,units='pix')
# win = visual.Window(
#     fullscr=True, screen=0, 
#     winType='pyglet', allowStencil=False,
#     monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
#     blendMode='avg', useFBO=True, 
#     units='height')
#win.mouseVisible = False

# create the dialogue box to get the subject number
#subject_info = {'Subject number':''} 
#
#if not gui.DlgFromDict(subject_info,title='Enter subject info:').OK: 
#    print('User hit cancel at subject information')
#    exit()
#try:
#    subj_number = int(subject_info['Subject number'])
#except:
#    raise

#----------------------------------------
# Timing things
# ---------------------------------------

isi = core.StaticPeriod(screenHz=2.5)
stream = core.StaticPeriod(screenHz=2.5)
fix = core.StaticPeriod(screenHz=60)

# ---------------------------------------
# Defining the Images and Text classes
#----------------------------------------

class Images:

    #constructor
    def __init__(self, path, width, height, position = (0.0, 0.0)):
        self.path = path 
        self.position = position
        self.width = width
        self.height = height
        self.image = visual.ImageStim(win=win, image=path, pos=position, size=(width, height))

    def display_image(self):
        self.image.draw()


class Text:
    def __init__(self, text, size, position=(0, 0)):
        self.text = text
        self.size = size
        self.text_stim = visual.TextStim(win=win, text = text, pos = position)

    def show_text(self):
        self.text_stim.draw()

class Triggers:
    def __init__(self, colour):
        self.colour = colour
        self.triggers = visual.Rect(win,size=.1,units='norm',pos=(-1,1),
                                    name='triggersquare',fillColorSpace='rgb255',lineWidth=0, fillColor=[colour, 0, 0])

    def show_trigger(self):
        self.triggers.draw()


    
# -------------------------
# Functions 
# -------------------------



#def check_abort(k):    #cree une touche pour escape (q)
#    if k and k[0][0]=='q':
#        writeout(eventlist)
#        raise Exception('User pressed q')

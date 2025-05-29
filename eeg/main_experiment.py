from psychopy import event, gui, core
import pandas as pd
import random
from psychopy.hardware import keyboard
import re

from definitions import Images, Triggers, Text, win


# subject's information:
debug_testsubject = 0

if debug_testsubject == 0:
    subjectnr = 'test'
else:
    subjectnr = debug_testsubject



#----------------------------------------------------
# %% setting the parameters for each type of elements
#----------------------------------------------------

## Text
# welcome

welcometxt = 'Thank you for participating in this experiment. \n\nYou will see a fast stream of visual illusions with objects. \nYour task is to count how many empty visual illusions you see in each block.'
welcome = Text(welcometxt, 5)


firstblocktxt = 'Count how many empty visual illusions you see in each block. \n\nPress "space" to continue (it might take a few seconds to load)'
firstblock = Text(firstblocktxt, 5)

responsetxt = 'How many empty visual illusions did you see? (1-8)'
question = Text(responsetxt, 5)



## Images
# fixation point
fixation_path = "Fixation.png"
fixation_height = 12
fixation_width = 12
fixation = Images(fixation_path, fixation_width, fixation_height)


# stimuli
conditions_df = pd.read_excel("conditions.xlsx") # opening the excel file where the stimuli paths are


stimuli_list = [] 
for stimulus in conditions_df['stimpath']:
    # this iterates through each 'row' of the excel file and adds each path to a list
    stimulus_path = stimulus
    stimuli_list.append(stimulus_path)


random_num_stim = random.randint(0, len(stimuli_list)-1) # choosing a random index from the list of paths
random_stim = stimuli_list[random_num_stim] # getting the value (path) corresponding to the random index

stimulus_path = random_stim 
stimulus_height = 256
stimulus_width = 256
stimulus = Images(stimulus_path, stimulus_width, stimulus_height)


# targets
targets_df = pd.read_excel("targets.xlsx") # opening the excel file where the targets paths are


targets_list = [] 
for target in targets_df['targetpath']:
    # this iterates through each 'row' of the excel file and adds each path to a list
    target_path = target
    targets_list.append(target_path)

random_num_tar = random.randint(0, len(targets_list)-1) # choosing a random index from the list of paths
random_tar = targets_list[random_num_tar]

target_path = random_tar
target_height = 50
target_width = 20
targets = Images(target_path, target_width, target_height)

## Triggers

trigger_stimon = Triggers(64/255)
trigger_stimoff = Triggers(32/255)
trigger_sequencestart = Triggers(16/255)

## Keyboard
kb = keyboard.Keyboard()
kb.clock.reset()


#-------------------------------------------------
# %% randomising the stimuli
#-------------------------------------------------
nsequences = 12

istarget = [] 
presentation_number = []
blocksequencenumber = []
allstimuli=[]
sequencenumber = []
f = 0

for s in range(nsequences):
    random.shuffle(stimuli_list)

    pattern = r'(.+)\\(\d{4})(.+)\.png'
    stim_group1 = []
    stim_group2 = []
    stim_group3 = []
    stim_group4 = []
    codes = {'1': [], '2': [], '3': [], '4': []}
    for img in stimuli_list:
        match = re.match(pattern, img)
        object_code = match.group(2)
        if object_code not in codes['1']:
            codes.setdefault('1', []).append(object_code)
            stim_group1.append(img)
        elif object_code not in codes['2']:
            codes.setdefault('2', []).append(object_code)
            stim_group2.append(img)
        elif object_code not in codes['3']:
            codes.setdefault('3', []).append(object_code)
            stim_group3.append(img)
        elif object_code not in codes['4']:
            codes.setdefault('4', []).append(object_code)
            stim_group4.append(img)


    # shuffle and divide the targets in the groups
    random.shuffle(targets_list)
    ntargets = random.randint(2, 4)
    tar_group1 = targets_list[:ntargets]
    random.shuffle(targets_list)
    ntargets = random.randint(2, 4)
    tar_group2 = targets_list[:ntargets]
    tar_seq1 = tar_group1 + tar_group2

    random.shuffle(targets_list)
    ntargets = random.randint(2, 4)
    tar_group3 = targets_list[:ntargets]
    random.shuffle(targets_list)
    ntargets = random.randint(2, 4)
    tar_group4 = targets_list[:ntargets]
    tar_seq2 = tar_group3 + tar_group4
    
    # create groups with random targets and stimuli to create the sequence
    group1 = random.sample(tar_group1 + stim_group1, len(tar_group1) + len(stim_group1))
    group2 = random.sample(tar_group2 + stim_group2, len(tar_group2) + len(stim_group2))
    group3 = random.sample(tar_group3 + stim_group3, len(tar_group3) + len(stim_group3))
    group4 = random.sample(tar_group4 + stim_group4, len(tar_group4) + len(stim_group4))
    sequence1 = group1 + group2 
    sequence2 = group3 + group4
    sequence = sequence1 + sequence2

    allstimuli = allstimuli+sequence

    for j in range(len(sequence)):
        blocksequencenumber.append(s)
        presentation_number.append(j)
        istarget.append(1 if sequence[j] in targets_list else 0) # append target-> boolean value

    div = [0,1]
    for x in range(len(div)):
        if x == 0:
            for _ in range(len(sequence1)):
                sequencenumber.append(f)
        else:
            f+=1
            for _ in range(len(sequence2)):
                sequencenumber.append(f)
            f+=1
   
    
print("sequence:", len(sequence))        
#-------------------------------------------------
# %% output files
#-------------------------------------------------

## event file
output = f'sub-{subjectnr}_eventlist.csv' # path of the output file-> TODO: solve having to insert the subject number manually in the output file name

def writeout(eventlist):

    with open(output,'w') as out:
        eventlist.to_csv(out,index_label='eventnumber') # create a list with the events that will happen in the experiment

eventlist = pd.DataFrame(blocksequencenumber,columns=['blocksequencenumber'])

eventlist['sequencenumber'] = sequencenumber
eventlist['presentation_number'] = presentation_number
eventlist['stimpath'] = allstimuli
eventlist['istarget'] = istarget

## response file
respfile = f'sub-{subjectnr}_responses.csv' #TODO: solve having to insert the subject number manually in the output file name

def writeout_resp(outresp):

    with open(respfile,'w') as file:
        outresp.to_csv(file,index_label='sequencenumber')

outresp = pd.DataFrame()

#-------------------------------------------------
# %% main loop
#-------------------------------------------------

# timing
refreshrate = 60
fixationduration = 1 - .5/refreshrate
stimduration = .2 - .5/refreshrate # change to .2
isiduration = .4 - .5/refreshrate # change to .4

# saving the conditions
writeout(eventlist)

# showing the exp
event.Mouse(visible = False)
welcome.show_text()
first_text=win.flip()
while core.getTime() < (first_text + 1):pass
response = None
while not response:
    keys = event.getKeys(keyList=['space', 'scape'])
    if keys:
        pressed = keys[0]
        response = core.getTime()
        writeout(eventlist)
        if pressed == 'escape':
                win.close()
                core.quit()

firstblock.show_text()
instructions=win.flip()
while core.getTime() < (instructions + 1):pass
response = None
while not response:
    keys = event.getKeys(keyList=['space', 'scape'])
    if keys:
        pressed = keys[0]
        response = core.getTime()
        writeout(eventlist)
        if pressed == 'escape':
                win.close()
                core.quit()


event_idx = -1
for n in range(24):

    trigger_sequencestart.show_trigger()
        
    fixation.display_image()
    fix_time = win.flip()
    fixation.display_image()
    win.flip()
    while core.getTime() < (fix_time + 1):pass

    seq_idx = [x==n for x in eventlist['sequencenumber']]
    stimuli_textures = [Images(x,stimulus_height,stimulus_width) for x in eventlist['stimpath'][seq_idx]]
    tar_seq = sum(eventlist['istarget'][seq_idx])

    for stim in stimuli_textures:
        event_idx+=1
        # first group's fast stream (images + isi)
        trigger_stimon.show_trigger()
        stim.display_image()
        fixation.display_image()
        time_stim = win.flip()
        #stim_index = stimuli_textures1.index(stim1) 
        eventlist.at[event_idx, 'time_stimon'] = time_stim 
        eventlist.at[event_idx, 'time_stimoff'] = time_stim + stimduration 
        eventlist.at[event_idx, 'stimduration'] = stimduration
        while core.getTime() < (time_stim + stimduration):pass

        fixation.display_image()
        win.flip()
        trigger_stimoff.show_trigger()
        keys = event.getKeys(keyList=['escape'])
        if keys:
            writeout(eventlist)
            win.close()
            core.quit()
        while core.getTime() < (time_stim + isiduration):pass
    
    question.show_text()
    time_question_on = win.flip()

    response = None
    while not response:
        keys = event.getKeys(keyList=['1', '2', '3', '4', '5', '6', '7', '8', 'escape'])
        if keys:
            pressed = keys[0]
            response = core.getTime()-time_question_on
            writeout(eventlist)
            if pressed == 'escape':
                win.close()
                core.quit()

    outresp.at[n, 'response'] = pressed
    outresp.at[n, 'number_targets'] = tar_seq
    if pressed == str(tar_seq):
        outresp.at[n, 'correct'] = 1
    else:
        outresp.at[n, 'correct'] = 0
    writeout_resp(outresp)

    # feedback
    feedback_text = f'There were {tar_seq} empty illusions and your answer was {pressed}.'
    # TODO: add sequence number as feedback
    feedback = Text(feedback_text, 5)
    feedback.show_text()
    next_block = win.flip()
    while core.getTime() < (next_block + 1):pass
    
    # continue and seq feedback
    continuetxt = f'Sequence {n+2} out of {nsequences*2}. Press "space" to continue'
    cont = Text(continuetxt, 5)
    # 'press "space" to continue' text
    cont.show_text()
    contxt = win.flip()
    while core.getTime() < (contxt + 1):pass

    response = None
    while not response:
        keys = event.getKeys(keyList=['space', 'scape'])
        if keys:
            pressed = keys[0]
            response = core.getTime()
            writeout(eventlist)
            if pressed == 'escape':
                    win.close()
                    core.quit()


# Close the PsychoPy window
writeout(eventlist)
win.flip()
win.close()
core.quit()
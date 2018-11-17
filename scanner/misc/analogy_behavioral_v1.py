import os, sys, csv
from datetime import datetime
from psychopy import core, visual, gui, misc, event  # , data, sound
# try to import numpy, if that fails, use random
try:
    import numpy as np 
except ImportError:
    import random

""" 
experiment file for analogy behavioral. 
This is meant to be modular and reusable code, so leave main() intact. 
Modify the extra functions as necessary for each experiment
Qarr is either the positional variability or probe 
"""

### Global Variables | Experiment parameters ###
if sys.platform == 'darwin':
    ROOT = os.path.join('/Users', 'njchiang')
else:
    ROOT = 'D:\\'
# PATH where all of the experiment files are
PATH = os.path.join(ROOT, 'Cloudstation', 'Grad', 'Research', 'Analogy', 'Behavioral')

# Paradigm attributes
HARD = True # whether two stimuli or one stimulus is presented
# HARD = False
RESP_TYPE = 1 # 1: for switching yes no, 2 for hit/miss
RESPONSE_LIST = ["a", "l"]  # valid responses. This config would be for behavioral
TIMELOCK = False # if we want presentations timelocked to MR pulse
# RESPONSE_LIST = ["3", "4"]  # valid responses. 
# This means that the cord is facing the subject's feet/opposite of thumb!
QTEXT = ["no", "yes"] # make sure this corresponds with RESPONSE_LIST

# timing parameters
JITTER_C = .5 # jitter time constant
ITI = 1  # time between trials (fixation after probe)
AB_DUR = 2  # duration of AB
CD_DUR = 2  # duration of CD
RESP_DUR = 4  # duration of probe
ISI1 = .5 # fixation after AB
ISI2 = .5  # fixation after CD
END_DUR= 1 # time at end of block
PRETRIAL = 3 # wait at beginning of block

# "4" is their index finger, 3 is their middle finger
RESOLUTION = [800,600] # monitor resolution
WAIT_TRs = 4 # discard 4 TRs
MR_PULSE = "5" # input from MR
ESCKEY=['escape']
MONITOR = "testMonitor" 
os.chdir(PATH)

# change this to the output format of the experiment, OUTKEYS and OUTFORMAT should correspond in data type
OUTKEYS = 'ABStart,ABDur,CDStart,CDDur,QStart,QDur,TrialTag,Match,QResponse,QCorrResponse\n'
OUTFORMAT = '%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%s,%s,%s,%s\n'
# directly write tsv files in openfMRI format, can clip this as necessary to make regressor files
TSVKEYS = 'Onset\tDuration\tTrialTag\tABTag\tCDTag\tMatch\tABMainRel\tCDMainRel\tABSubRel\tCDSubRel\tProbeResp\tProbeCorr\tProbeArr\tAB\tCD\tProbe\n'
TSVFORMAT = '%.4f\t%.4f\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'

### display colors and instructions ###
BLACK = [-1, -1, -1]
WHITE = [1, 1, 1]
GRAY = [0, 0, 0]
WELCOMETEXT = \
"You will be shown two pairs of words, one pair after another. \
Please consider whether they indicate the same relation or not (yes or no) when prompted.\n \
Be careful, the yes and no buttons will switch places! \
Please answer as accurately and quickly as possible \
(And please try to remain as still as possible during the scan)"
BEGINTEXT = "The session is about to begin"


def initoutput(e):
    """
    Creates a text file that stores the timing and other variables within the script
    fileName = 'Output/' + expInfo['participant'] + '_' + expInfo['session']+ '_' +expInfo['dateStr']
    """
    dfileName = os.path.join('Output', e['participant'] + '_' + e['session'])
    # add check for pre-existing files here
    append=''
    if os.path.exists(dfileName+'_All.csv'):
        append='_duplicate'
        print "duplicate output file detected, fix this before next run"
    dfa = open(str(dfileName) + '_All' + append + '.csv', 'w')
    dfa.write(OUTKEYS)
    append=''
    tfileName = os.path.join('Output', 'Sub'+e['participant'] + '_Run' + e['session'])
    if os.path.exists(dfileName+'.tsv'):
        append='_duplicate'
        print "duplicate output file detected, fix this before next run"
    t = open(str(dfileName) + append + '.tsv', 'w')
    t.write(TSVKEYS)
    return dfa, t


def writetsv(f, t, on, dur, ):
    """
    write separate tsv files that will serve as regressors for each subject (might as well do it in real time...)
    split later to do contrasts of interest in univariate
    """

def getstiminfo(f):
    """
    assuming csvFile has header, read into a dictionary with corresponding lists. 
    For each run, write this file.
    Verify that this can handle multiple instances of the same trial
    """
    tt={}
    with open(f, "rb") as fl:
        csvFile = csv.DictReader(fl)
        for count, row in enumerate(csvFile,1):
            for col, val in row.iteritems():
                tt.setdefault(col, []).append(val)
                        
    ra = [i for i in xrange(count)]
    try:
        # if numpy can be loaded
        # randomize the presentation order
        np.random.shuffle(ra)
        # randomize the presentation of yes and no
        np.random.shuffle(tt['Qarrange'])
        j = np.random.exponential(JITTER_C, size=(count,2))
        print "numpy successfully loaded, using exponential jitter"
    except:
        # use uniform distribution multiplied by JITTER SCALE
        print "could not use numpy, using uniform random"
        ra = random.sample(ra, len(ra))
        tt['Qarrange'] = random.sample(tt['Qarrange'], len(tt['Qarrange']))
        j = []
        for ji in xrange(count):
            j.append([JITTER_C*random.random(), JITTER_C*random.random()]) 
            
    return tt, ra, j


def randomresponse(qc, qa, gc, cc, mw):
    """
    presents elements of QTEXT in differing spots on the screen
    qa: Qarrange-probe configuration
    qc: correct answer
    gc: global clock
    cc: trial clock
    mw: window
    """
    # conditional for qcor # i guess we should have qon and qdur here. make this work out
    if qa == '1':
        text = str('(' + QTEXT[1] + ')\t\t' + 
                     '\t\t(' + QTEXT[0] + ')')
        # text = str(QTEXT[0] + "\n\n\n\n" + QTEXT[1])
        if qc == '1':
            qcor = RESPONSE_LIST[0]
        elif qc == '0':
            qcor = RESPONSE_LIST[1]
    else:
        text = str('(' + QTEXT[0] + ')\t\t' + 
                     '\t\t(' + QTEXT[1] + ')')
        #text = QTEXT[1] + "\n\n\n\n" + QTEXT[0]
        if qc == '1':
            qcor = RESPONSE_LIST[1]
        elif qc == '0':
            qcor = RESPONSE_LIST[0]        
        
    stim = visual.TextStim(mw, pos=[0, 0], text=text,
                              wrapWidth=25, alignHoriz='center', alignVert='center', color=WHITE)
    # Waits for the pulse to come in before displaying the stimuli. necessary?
    # event.waitKeys(keyList=[MR_PULSE])  
    cc.reset()
    qon = gc.getTime()
    stim.draw()
    mw.flip()    
    rk = event.waitKeys(maxWait=RESP_DUR, keyList=RESPONSE_LIST)
    # Change the numbers in quotes to the keys used to answer the question.
    qdur = cc.getTime()
    return rk, qcor, qon, qdur
    

def randomresponse2(qc, qa, gc, cc, mw):
    """
    presents elements of QTEXT in differing spots on the screen
    qa: Qarrange-probe "match" (1) or "mismatch" (2)
    qc: correct answer
    gc: global clock
    cc: trial clock
    mw: window
    """
    # conditional for qcor # i guess we should have qon and qdur here. make this work out
    if qa == '1': # asking for HIT
        text = str('(' + QTEXT[0] + ')\t\t' + 
                    "HIT" + '\t\t(' + QTEXT[1] + ')')
        if qc == '1': # correct response is yes
            qcor = RESPONSE_LIST[0]
        elif qc == '0':
            qcor = RESPONSE_LIST[1]
    else: # asking for MISS
        text = str('(' + QTEXT[0] + ')\t\t' + 
                    "MISS" + '\t\t(' + QTEXT[1] + ')')
        if qc == '1': # correct response is no
            qcor = RESPONSE_LIST[1]
        elif qc == '0':
            qcor = RESPONSE_LIST[0]        
        
    stim = visual.TextStim(mw, pos=[0, 0], text=text,
                              wrapWidth=25, alignHoriz='center', alignVert='center', color=WHITE)
    # Waits for the pulse to come in before displaying the stimuli. necessary?
    # event.waitKeys(keyList=[MR_PULSE])  
    cc.reset()
    qon = gc.getTime()
    stim.draw()
    mw.flip()    
    rk = event.waitKeys(maxWait=RESP_DUR, keyList=RESPONSE_LIST)
    # Change the numbers in quotes to the keys used to answer the question.
    qdur = cc.getTime()
    return rk, qcor, qon, qdur
  
    
def singlestim(text, gc, cc, mw, vertspacing=1):
    """ 
    runs a single stimulus:
    text: text to be displayed (str or list of strings that will be vertically stacked)
    rarr: randomizedArray
    gc: global clock (never resets)
    cc: condition clock (resets for every stimulus)
    mw: my window
    vertspacing: vertical spacing of text
    """
    
    if isinstance(text, str):
        # dtext=text.replace(':', ' : ')
        stim = visual.TextStim(mw, pos=[0, 0], text=text.replace(':', ' : '),
                              wrapWidth=25, alignHoriz='center', alignVert='center', color=WHITE)
        stim.draw()
    else:
        parr = range(0,len(text),vertspacing) # because zero indexing
        parr.reverse()
        padj = float(max(parr)/2)
        for i, p in enumerate(parr):
            stim = visual.TextStim(mw, pos=[0, p-padj], text=text[i].replace(':', ' : '),
                                   wrapWidth=25, alignHoriz='center', alignVert='center', color=WHITE)
            stim.draw()

    if TIMELOCK:
        event.waitKeys(keyList=[MR_PULSE])  # Waits for the pulse to come in before displaying the stimuli.
    cc.reset()
    ton = gc.getTime()
    mw.flip()
    core.wait(AB_DUR)
    tdur = cc.getTime()
    return ton, tdur
    

def singletrial(tt, rt, dfa, tsv, gc, cc, j, fx, mw):
    """ 
    change this for each experiment, this is the skeleton of a single trial
    tt: dictionary where each item is a trial attribute, and contains a list corresponding to each trial
    rt: this trial index 
    dfa: output data file
    tsv: output tsv (will output in fMRI format)
    gc: global clock
    cc: trial clock
    j: jitter, list containing jitter for each presentation
    fx: fixation window
    mw: screen
    """
    # show AB
    if HARD:
    # hard version
        ab_on, ab_dur = singlestim(text=tt['AB'][rt], gc=gc, cc=cc, mw=mw)
    else: # easy version
        mask = ''.join(['#' for i in tt['CD'][rt]])
        abtext = [str(tt['AB'][rt]),'\n','\n','\n', str(mask)]
        ab_on, ab_dur = singlestim(text=abtext, gc=gc, cc=cc, mw=mw)
    fx.draw()
    mw.flip()
    core.wait(ISI1+j[0])
    
    # show CD
    
    if HARD:
        # hard version
        cd_on, cd_dur = singlestim(text=tt['CD'][rt], gc=gc, cc=cc, mw=mw)
    else:
        # easy version
        cdtext = [str(tt['AB'][rt]),'\n','\n','\n', str(tt['CD'][rt])]
        cd_on, cd_dur = singlestim(text=cdtext, gc=gc, cc=cc, mw=mw)
    fx.draw()
    mw.flip()
    core.wait(ISI2+j[1])
    
    # show Probe
    if RESP_TYPE == 1:
        responseKey, qcor, qon, qdur = randomresponse(qc=tt['Match'][rt], qa=tt['Qarrange'][rt],
                                                    gc=gc, cc=cc, mw=mw)
    else:
        responseKey, qcor, qon, qdur = randomresponse2(qc=tt['Match'][rt], qa=tt['Qarrange'][rt],
                                                    gc=gc, cc=cc, mw=mw)
    fx.draw()
    mw.flip()
    
    # write to files
    dfa.write(OUTFORMAT % (ab_on, ab_dur, cd_on, cd_dur, qon, qdur, tt['TrialTag'][rt], tt['Match'][rt], responseKey, qcor))
    tsv.write(TSVFORMAT % (ab_on, ab_dur, tt['TrialTag'][rt], tt['AB'][rt], 'None', 'None', \
                         tt['OverallRelationAB'][rt], 'None', tt['SpecificRelationAB'][rt], \
                         'None', 0, 0, 0, 1, 0, 0))
    tsv.write(TSVFORMAT % (cd_on, cd_dur, tt['TrialTag'][rt], 'None', tt['CD'][rt], tt['Match'][rt], \
                         'None', tt['OverallRelationCD'][rt], 'None',  \
                         tt['SpecificRelationCD'][rt], 0, 0, 0, 0, 1, 0))
    tsv.write(TSVFORMAT % (qon, qdur, tt['TrialTag'][rt], tt['AB'][rt], tt['CD'][rt], tt['Match'][rt], \
                         tt['OverallRelationAB'][rt], tt['OverallRelationCD'][rt], tt['SpecificRelationAB'][rt], \
                         tt['SpecificRelationCD'][rt], responseKey, qcor, tt['Qarrange'][rt], 0, 0, 1))
                        
    # command line show just for monitoring
    print (OUTFORMAT % (ab_on, ab_dur, cd_on, cd_dur, qon, qdur, tt['TrialTag'][rt], tt['Match'][rt], responseKey, qcor))


def main(argv):
    """
    should not need to modify this 
    """
    try:
        expInfo = misc.fromFile('lastParams.pickle')
    except:
        expInfo = {'participant':'','session':''}
        expInfo['dateStr']= datetime.time(datetime.now())
    # This function creates the dialog box at the beginning of the script that you
    # enter the subject's name and has the date automatically entered into it
    dlg = gui.DlgFromDict(expInfo, title='File Name', fixed=['dateStr'])
    if dlg.OK:
        misc.toFile('lastParams.pickle', expInfo)
    else:
        core.quit()
    ### initialize output5
    # Stores the information in the dialog box to a variable to be used to create a file
    dataFile_All, tsvFile = initoutput(expInfo)
    print dataFile_All
    TrialTimes, randomizedArray, jitters = getstiminfo(str(os.path.join('stimuli', 'run_'+expInfo['session']+'.csv')))
    
    ### INITIALIZE DISPLAY ###
    # keep in mind monitor resolution
    mywin = visual.Window(RESOLUTION,monitor=MONITOR, units="deg", color=BLACK)
    mouse = event.Mouse(visible=False, win=mywin)
    mouse.setVisible(0) # Sets mouse to invisible
    
    # Initial instructions before scan starts
    welcome = visual.TextStim(mywin, pos=[0,0],
                              text=WELCOMETEXT,
                              wrapWidth=20, alignHoriz='center', alignVert='center', color=WHITE)
    welcome.draw() # Displays the welcome stimulus
    mywin.update() # Updates the window to show the stimulus
    # Waits for the pulse senquence to send a 5. This is before the TRs to be deleted
    event.waitKeys(keyList=[MR_PULSE])
    # Informs participant that the experiment is beginning
    sessionStart = visual.TextStim(mywin, pos=[0,0],
                                   text=BEGINTEXT,
                                   wrapWidth=35, alignHoriz='center',alignVert='center', color=WHITE)
    
    #Creates a fixation cross stimulus to be used later
    fixation = visual.TextStim(mywin, pos=[0,0],
                               text="+", wrapWidth=25, alignHoriz='center',alignVert='center', color=WHITE)
    sessionStart.draw() # Displays the welcome stimulus
    mywin.update()# Updates the window to show the stimulus
    # Waits N TRs till global clock starts
    for i in xrange(WAIT_TRs):
        event.waitKeys(keyList=[MR_PULSE])

    globalClock = core.Clock() # Sets the global clock to globalClock variable
    globalClock.reset() # Resets the global clock
    trialClock = core.Clock() # sets a trial clock to trialClock variable
    condClock = core.Clock() # initializes condition clock which resets every time
    
    try:
        fixation.draw()
        mywin.flip()
        core.wait(PRETRIAL) # just using ITI for now...
        
        ### actual experiment loop ###
        for trialID in randomizedArray:
            # randTrial = rarr[c]
            if event.getKeys(keyList=ESCKEY):
                raise KeyboardInterrupt
            singletrial(tt=TrialTimes, rt=trialID, dfa=dataFile_All, tsv=tsvFile,
                        gc=globalClock, cc=condClock, j=jitters[trialID], fx=fixation, mw=mywin)
            core.wait(ITI)

        ### end of block, draw fixation and quit message ###

        core.wait(END_DUR)
        sessionEnd = visual.TextStim(mywin, pos=[0,0],text="Q", wrapWidth=35,
                                     alignHoriz='center', alignVert='center', color=[1, 1, 1])
        sessionEnd.draw()
        mywin.flip()
        event.waitKeys(keyList=["q"])
        
    except KeyboardInterrupt:
        print "manually aborted"
        
    except:
        print "error"
        
    finally:
        fixation.draw()
        mywin.update()
        dataFile_All.close()
        tsvFile.close()
        mywin.close()
        core.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
    

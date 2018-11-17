from datetime import datetime
from psychopy import core, visual, gui, data, misc, event, sound #Loads different libraries that will be used in this script
import csv,random
#This function creates the dialog box at the beginning of the script that you enter the subject's name and has the date automatically entered into it
try:
    expInfo = misc.fromFile('lastParams.pickle')
except:
    expInfo = {'participant':'','session':'001'}
    expInfo['dateStr']= datetime.time(datetime.now())
dlg = gui.DlgFromDict(expInfo, title='File Name', fixed=['dateStr'])
if dlg.OK:
    misc.toFile('lastParams.pickle', expInfo)
else:
    core.quit()

fileName = 'Output/'+expInfo['participant'] +'_'+expInfo['session']+'_'+expInfo['dateStr']#Stores the information in the dialog box to a variable to be used to create a file
dataFile_All = open(fileName+'_All'+'.csv','w') #Creates a text file that stores the timing and other variables within the script
dataFile_All.write('TrialTag,TrialStart,TrialDur,QStart,QDur,QResponse,QCorrResponse\n')
print dataFile_All

Col1 = "Sentence"
Col2 = "OpacityS"
Col3 = "Illustration"
Col4 = "OpacityI"
Col5 = "StimCat"
Col6 = "Family"
Col7 = "ActPass"
Col8 = "CanRel"
Col9 = "Stx"
Col10 = "Anlnan"
Col11 = "VrbType"
Col12 = "VerbTypeTxt"
Col13 = "TrialTag"
Col14 = "QText"
Col15 = "QDuration"
Col16 = "QFixDuration"
Col17 = "QCorrResp"
Col18 = "QDR"
TrialTimes={Col1:[], Col2:[], Col3:[],Col4:[],Col5:[], Col6:[], Col7:[],Col8:[], Col9:[],Col10:[], Col11:[], Col12:[], Col13:[],Col14:[],Col15:[], Col16:[], Col17:[],Col18:[]}
csvFile = csv.reader(open("/Users/CCN/Desktop/MontiLab/NewStimuli/Sentences_SessionL1.csv","rb"))
for row in csvFile:
  TrialTimes[Col1].append(row[0])
  TrialTimes[Col2].append(row[1])
  TrialTimes[Col3].append(row[2])
  TrialTimes[Col4].append(row[3])
  TrialTimes[Col5].append(row[4])
  TrialTimes[Col6].append(row[5])
  TrialTimes[Col7].append(row[6])
  TrialTimes[Col8].append(row[7])
  TrialTimes[Col9].append(row[8])
  TrialTimes[Col10].append(row[9])
  TrialTimes[Col11].append(row[10])
  TrialTimes[Col12].append(row[11])
  TrialTimes[Col13].append(row[12])
  TrialTimes[Col14].append(row[13])
  TrialTimes[Col15].append(row[14])
  TrialTimes[Col16].append(row[15])
  TrialTimes[Col17].append(row[16])
  TrialTimes[Col18].append(row[17])


#mywin = visual.Window([1280,780],monitor="testMonitor", units="deg", color=[-1,-1,-1]) #This is where to adjust the color. 1,1,1 is white and 0,0,0 is grey.
mywin = visual.Window([800,600],monitor="testMonitor", units="deg", color=[-1,-1,-1]) #This is where to adjust the color. 1,1,1 is white and 0,0,0 is grey.
mouse = event.Mouse(visible=False, win=mywin) 
mouse.setVisible(0) #Sets mouse to invisible
welcome=visual.TextStim(mywin, pos=[0,0],text="Get ready, the experiment will begin shortly! \n\n(And please try to remain as still as possible during the scan)", wrapWidth=25, alignHoriz='center',alignVert='center', color=[1,1,1]) #Initial instructions before scan starts
welcome.draw() #Displays the welcome stimulus
mywin.update() #Updates the window to show the stimulus
event.waitKeys(keyList=["5"]) #Waits for the pulse senquence to send a 5
sessionStart=visual.TextStim(mywin, pos=[0,0],text="The session is about to begin", wrapWidth=35, alignHoriz='center',alignVert='center', color=[1,1,1])#Informs participant that the experiment is beginning
fixation=visual.TextStim(mywin, pos=[0,0],text="+", wrapWidth=25, alignHoriz='center',alignVert='center', color=[1,1,1]) #Creates a fixation cross stimulus
sessionStart.draw() #Displays the welcome stimulus
mywin.update()#Updates the window to show the stimulus
event.waitKeys(keyList=["5"]) 
event.waitKeys(keyList=["5"]) 
event.waitKeys(keyList=["5"]) 
event.waitKeys(keyList=["5"]) #Waits 4 TRs till global clock starts
globalClock = core.Clock() #Sets the global clock to globalClock variable
globalClock.reset() #Resets the global clock
trialClock = core.Clock() #sets a trial clock to trialClock variable
condClock = core.Clock()
tg = 0
t = 0
tdur = 0 
ton = 0 
qon = 0
qdur=0 
randomArray = [0,1,2,3,4,5,6,7]#Change the number of elements in this array to match the number of rows - 1 (because this array starts at 0) in the csv file.
fixation.draw()
mywin.flip()
core.wait(3)
for repConditions in xrange(1):
    nRandom = random.sample(set(randomArray), 8)#Change the number to the number of rows in csv file.
    randomizedArray = nRandom
    for Conditions in xrange(len(TrialTimes[Col2])):
        randTrial = randomizedArray[Conditions]
        qText = TrialTimes[Col14][randTrial]
        iText = TrialTimes[Col1][randTrial]
        iPic = TrialTimes[Col3][randTrial]
        ilOpa = int(TrialTimes[Col4][randTrial])
        inOpa = int(TrialTimes[Col2][randTrial])
        TTag = TrialTimes[Col13][randTrial]
        qcor = TrialTimes[Col17][randTrial]
        #print iPic
        #illustrationStim = visual.ImageStim(mywin,image=iPic,size=[10,10],pos=[0,0])
        #illustrationStim = visual.SimpleImageStim(mywin,image='/Users/CCN/Desktop/MontiLab/NewStimuli/Illustrations/l_Touch_Touch_Inanim_Pass_Rel.jpg')
        #illustrationStim = visual.GratingStim(mywin,pos=(0,0),tex=iPic, size=[12,12])
        illustrationStim=visual.PatchStim(win=mywin, tex=iPic,pos=[0,0], size=[13,13])
        instructionsStim = visual.TextStim(mywin, pos=[0,0],text=iText, wrapWidth=25, alignHoriz='center',alignVert='center', color=[1,1,1])
        questionStim = visual.TextStim(mywin, pos=[0,0],text=qText, wrapWidth=25, alignHoriz='center',alignVert='center', color=[1,1,1])
        if inOpa == 0:
            illustrationStim.draw()
        else:
            instructionsStim.draw()
        event.waitKeys(keyList=["5"]) #Waits for the pulse to come in before displaying the stimuli.
        condClock.reset()
        ton = globalClock.getTime()
        mywin.flip()
        core.wait(3)
        tdur = condClock.getTime()
        fixation.draw()
        mywin.flip()
        core.wait(10)
        if qText == "0":
            fixation.draw()
            mywin.flip()
            qon = globalClock.getTime()
            qdur = 0
            dataFile_All.write('%s,%.4f,%.4f,%.4f,%.4f,0,0\n' %(TTag,ton, tdur,qon,qdur))
            print ('%s,%.4f,%.4f,%.4f,%.4f,0,0\n' %(TTag,ton, tdur,qon,qdur))
        else:
            condClock.reset()
            qon = globalClock.getTime()
            questionStim.draw()
            mywin.flip()
            responseKey = event.waitKeys(maxWait = 5, keyList=["3","4"]) #Change the numbers in quotes to the keys used to answer the question.
            qdur = condClock.getTime()
            dataFile_All.write('%s,%.4f,%.4f,%.4f,%.4f,%s,%s\n' %(TTag,ton, tdur,qon,qdur,responseKey,qcor))
            print ('%s,%.4f,%.4f,%.4f,%.4f,%s,%s\n' %(TTag,ton, tdur,qon,qdur,responseKey,qcor))
            fixation.draw()
            mywin.flip()
            core.wait(10)
fixation.draw()
mywin.update()
core.wait(5)
sessionEnd=visual.TextStim(mywin, pos=[0,0],text="Q", wrapWidth=35, alignHoriz='center',alignVert='center', color=[1,1,1])
sessionEnd.draw()
mywin.flip()
event.waitKeys(keyList=["q"])

# -*- coding: utf-8 -*-
from psychopy import event, core, data, gui, visual
from fileHandling import *
import speech_recognition as sr

class Experiment:
    def __init__(self, win_color, txt_color):
        self.stimuli_positions = [[-.2, 0], [.2, 0], [0, 0]]
        self.win_color = win_color
        self.txt_color = txt_color

    def create_window(self, color=(1, 1, 1)):

        color = self.win_color
        win = visual.Window(monitor="testMonitor",
                            color=color, fullscr=True)
        return win

    def settings(self):
        experiment_info = {'Full Name ': '', 'Subid': '', 'Age': '', 'Experiment Version': 0.1,
                           'Sex': ['Male', 'Female', 'Other'],
                           'Language': ['English', 'German'], u'date':
                               data.getDateStr(format="%Y-%m-%d_%H:%M")}

        info_dialog = gui.DlgFromDict(title='Stroop task', dictionary=experiment_info,
                                      fixed=['Experiment Version'])
        experiment_info[u'DataFile'] = u'Data' + os.path.sep + u'stroop.csv'

        if info_dialog.OK:
            return experiment_info
        else:
            core.quit()
            return 'Cancelled'

    def create_text_stimuli(self, text=None, pos=[0.0, 0.0], name='', color=None):
        '''Creates a text stimulus,
        '''
        if color is None:
            color = self.txt_color
        text_stimuli = visual.TextStim(win=window, ori=0, name=name,
                                       text=text, font=u'Arial',
                                       pos=pos, 
                                       color=color, colorSpace=u'rgb')
        return text_stimuli

    def create_trials(self, trial_file, randomization='random'):
        '''Doc string'''
        data_types = ['Response', 'Accuracy', 'RT', 'Sub_id', 'Sex', 'Name']
        with open(trial_file, 'r') as stimfile:
            _stims = csv.DictReader(stimfile)
            trials = data.TrialHandler(list(_stims), 1,
                                       method="random")
        [trials.data.addDataType(data_type) for data_type in data_types]

        return trials

    def present_stimuli(self, color, text, position, stim):
        _stimulus = stim
        color = color
        position = position
        if settings['Language'] == "German":
            text = German_task(text)
        else:
            text = text
        _stimulus.pos = position
        _stimulus.setColor(color)
        _stimulus.setText(text)
        return _stimulus

    def recognize_speech(recognizer, microphone):

        # check that recognizer and microphone arguments are appropriate type
        #if not isinstance(recognizer, sr.Recognizer):
            #raise TypeError("`recognizer` must be `Recognizer` instance")

        #if not isinstance(microphone, sr.Microphone):
           # raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone



        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }
        
        try:
            # if language==German_task:
            #     response["transcription"] = recognizer.recognize_google(audio, language="de_DE")
            # else:
            response["transcription"] = recognizer.recognize_google(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["success"] = False
            response["error"] = "Unable to recognize speech"
        
        return response


    def running_experiment(self, trials, testtype):
        _trials = trials
        testtype = testtype
        timer = core.Clock()
        stimuli = [self.create_text_stimuli(window) for _ in range(4)]
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        for trial in _trials:
            # Fixation cross
            fixation = self.present_stimuli(self.txt_color, '+', self.stimuli_positions[2],
                                            stimuli[3])
            fixation.draw()
            window.flip()
            #core.wait(.6)
            timer.reset()

            # Target word
            target = self.present_stimuli(trial['colour'], trial['stimulus'],
                                          self.stimuli_positions[2], stimuli[0])
            target.draw()
            window.flip()

            response = Experiment.recognize_speech(recognizer, microphone)
        
            resp_time = timer.getTime()
            if testtype == 'practice':
               
                if response["transcription"] != trial['correctresponse']:
                    instruction_stimuli['incorrect'].draw()

                else:
                    instruction_stimuli['right'].draw()

                window.flip()
                core.wait(2)

            if testtype == 'test':

                if response["transcription"] == trial['correctresponse']:
                    trial['Accuracy'] = 1
                else:
                    trial['Accuracy'] = 0
#writing csv results
                trial['RT'] = resp_time
                trial['Response'] = response["transcription"]
                trial['Sub_id'] = settings['Subid']
                trial['Name'] = settings['Full name']
                trial['Sex'] = settings['Sex']
                write_csv(settings[u'DataFile'], trial)

            event.clearEvents()
            print("response :{}".format(response))


def create_instructions_dict(instr):
    start_n_end = [w for w in instr.split() if w.endswith('START') or w.endswith('END')]
    keys = {}

    for word in start_n_end:
        key = re.split("[END, START]", word)[0]

        if key not in keys.keys():
            keys[key] = []

        if word.startswith(key):
            keys[key].append(word)
    return keys


def create_instructions(input, START, END, color="Black"):
    instruction_text = parse_instructions(input, START, END)
    print(instruction_text)
    text_stimuli = visual.TextStim(window, text=instruction_text, wrapWidth=1.2,
                                   alignHoriz='center', color=color,
                                   alignVert='center', height=0.06)

    return text_stimuli


def display_instructions(start_instruction=''):
    # Display instructions

    if start_instruction == 'Practice':
        instruction_stimuli['instructions'].pos = (0.0, 0.5)
        instruction_stimuli['instructions'].draw()

        positions = [[-.2, 0], [.2, 0], [0, 0]]
        examples = [experiment.create_text_stimuli() for pos in positions]
        example_words = ['green', 'blue', 'blue']
        if settings['Language'] == 'German':
            example_words = [German_task(word) for word in example_words]

        for i, pos in enumerate(positions):
            examples[i].pos = pos
            if i == 0:
                continue
            elif i == 1:
                continue
            elif i == 2:
                examples[2].setColor('Green')
                examples[2].setText(example_words[i])

        [example.draw() for example in examples]

        instruction_stimuli['practice'].pos = (0.0, -0.5)
        instruction_stimuli['practice'].draw()

    elif start_instruction == 'Test':
        instruction_stimuli['test'].draw()

    elif start_instruction == 'End':
        instruction_stimuli['done'].draw()

    window.flip()
    event.waitKeys(keyList=['space'])
    event.clearEvents()


def German_task(word):
    German = '+'
    if word == "blue":
        German = u"blau"
    elif word == "red":
        German = u"rot"
    elif word == "green":
        German = u"grün"
    elif word == "yellow":
        German = "gelb"
    return German


if __name__ == "__main__":
    background = "Black"
    back_color = (0, 0, 0)
    textColor = "White"
    # text_color = (1, 1, 1)
    experiment = Experiment(win_color=background , txt_color=textColor)
    settings = experiment.settings()
    language = settings['Language']
    instructions = read_instructions_file("INSTRUCTIONS", language, language + "End")
    instructions_dict = create_instructions_dict(instructions)
    instruction_stimuli = {}

    window = experiment.create_window(color=back_color)

    for inst in instructions_dict.keys():
        instruction, START, END = inst, instructions_dict[inst][0], instructions_dict[inst][1]
        instruction_stimuli[instruction] = create_instructions(instructions, START, END, color=textColor)

    # We don't want the mouse to show:
    event.Mouse(visible=False)
    # Practice Trials
    display_instructions(start_instruction='Practice')

    practice = experiment.create_trials('practice_list.csv')
    experiment.running_experiment(practice, testtype='practice')
    # Test trials
    display_instructions(start_instruction='Test')
    trials = experiment.create_trials('stimuli_list.csv')
    experiment.running_experiment(trials, testtype='test')

    # End experiment but first we display some instructions
    display_instructions(start_instruction='End')
    window.close()

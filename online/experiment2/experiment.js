
var researcher_name = "Almudena Ramirez"
var researcher_email = "A.RamirezHaro3@westernsydney.edu.au" 
var time_required = "15"

var debrief = '<p>Thank you for taking the time to complete this experiment.'+
    'The aim of this experiment is to better understand how objects are categorised in the brain, and investigate the contribution of visual features to object categorisation.'+
    'We predict that the speed at which you can correctly categorise objects is predicted by the presence and absence of a combination of visual features.</p>'

var finishURL = 'https://uws.sona-systems.com/webstudy_credit.aspx?experiment_id=1677&credit_token=94608e1eb3e04947bfe23ba90c186f61&survey_code='



/* initialize jsPsych */
var jsPsych = initJsPsych({
    show_progress_bar: true,
    auto_update_progress_bar: false,
    message_progress_bar: 'Experiment progress',
    show_preload_progress_bar: true,
    on_finish: function() { 
        endExperiment(jsPsych.data.get().csv(), function() {     
            document.write(HTMLExperimentEnd)
        })
    }
});




var surveyCode = jsPsych.data.getURLVariable('survey');

var debug = surveyCode==1234
/*var debug = 1*/


if (!surveyCode) {
    surveyCode = 'test'
    console.log(surveyCode)
}
var finishURLcode = finishURL + surveyCode;
var HTMLExperimentEnd = '<div id="endscreen" class="endscreen" style="width:1000px"><div class="endscreen" style="text-align:center; border:0px solid; padding:10px; font-size:120%; width:800px; float:right">'+
    '<p><br><br><br>Experiment Finished! Please click here to finish the experiment and return to SONA:<br><a href="'+finishURLcode+'" target="blank">'+finishURLcode+'</a><p>'+debrief+'</div></div>';   

if (Math.random()<.5) {
    var taskdescription = "[z] same or different [m]"
    var taskdescription2 = "Press 'z' when they are the same, and press 'm' when they are different."
} else {
    var taskdescription = "[z] different or same [m]"
    var taskdescription2 = "Press 'z' when they are different, and press 'm' when they are the same."
}

var online = document.currentScript.getAttribute('data-online')=="1"
if (online) {
    console.log("online mode")
} else {
    console.log("offline mode")
}
function endExperiment(dataset,callback) {
    console.log(dataset) // comment out to avoid console log
    setTimeout(callback,500)
}

// shuffle function
function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

/*stimuli = []
for (var i=0;i<stimlist.length;i++) {
    stimuli.push(stimlist[i])
}
shuffle(stimuli); */
//stimuli = stimuli.slice(0,5) //for debugging


var conditions = {};
for (var x of stimlist) {
    var o = Math.floor(Math.random() * 2);
    console.log("o:", o)
    if (o === 0 && dictcorrect[x]) {
        console.log("correct:", dictcorrect[x]);
        conditions[x] = dictcorrect[x];
      } else if (o === 1 && dictincorrect[x]) {
        shuffle(dictincorrect[x]);
        console.log("incorrect:", dictincorrect[x]);
        conditions[x] = dictincorrect[x][1];
      } 
    }

console.log("conditions:", conditions)

var stimuli = Object.keys(dictcorrect)
var wordstimuli = Object.values(dictcorrect)
shuffle(stimuli)

var stim_practice = ['stimuli/1511110_bio_cow1_front_invalid_triangle.png', 'stimuli/0233001_artif_table3_behind_valid_square.png'];
var obj_practice = ['obj_words/cow.png', 'obj_words/car.png']


//console.log(stimuli)
var nstimuli = stimuli.length
var ntrials = stimuli.length

/* create timeline */
var timeline = []

/* init connection with pavlovia.org */
if (online) {
    var pavlovia_init = {
        type: jsPsychPavlovia,
        command: "init"
    }
    timeline.push(pavlovia_init);
}

var preload = {
    type: jsPsychPreload,
    images: stimuli.concat(['fixation0.png']).concat(wordstimuli),
    max_load_time: 600000,
    message: 'Please wait while the experiment loads. This may take a few minutes.',
    error_message: 'The experiment failed to load. Please try again or contact the researcher.'
}
timeline.push(preload)

var consentform = {
    type: jsPsychHtmlButtonResponse,
    stimulus: '<p>Please read the following and press the button at the bottom of the screen to begin.</p><p></p>' + 
    '<p><h1><strong>PARTICIPANT INFORMATION STATEMENT</strong></h1></p><p></p>' + 
    '<div align=left>' +
    '<p><strong>Project Title: </strong>Decoding the Neural Basis of Object Perception</p>' + 
    '<p><strong>Project Summary:</strong><br />Our daily activities depend on accurate and rapid extraction of object identity. Object recognition seems effortless, but requires solving complex a computational problem: we detect and classify objects from among tens of thousands of possibilities across wide variations in scene properties, and we do so within a fraction of a second. The project aims to investigate object recognition, specifically focussing on how the brain constructs representations from retinal input.</p>' +
    '<p>You are invited to participate in an online study conducted by '+researcher_name+' from the MARCS Institute for Brain, Behaviour and Development. This study is an online behavioural experiment that can be accessed from your own computer.</p>' + 
    
    "<p><strong>How is the study being paid for?</strong><br />This project is funded by Western Sydney University internal funding awarded to Dr Tijl Grootswagers (Vice-Chancellor's Research Fellowship, Project Code 20211.31014).</p>" + 
    '<p><strong>What will I be asked to do?</strong><br />During the experiment, you will be asked to view visual stimuli on a computer screen. The visual stimuli may be presented in different ways and in different durations, and features of the stimuli may also change. You will be asked to respond to these stimuli in different ways. Responses may include pressing buttons or keys (either on a keyboard, mouse or button box), typing responses on a keyboard, or pressing a particular key when recalling visual material.</p>' + 
    '<p><strong>How much of my time will I need to give?</strong><br />The study will take roughly '+time_required+' minutes to complete.</p>' + 
    '<p><strong>What benefits will I, and/or the broader community, receive for participating?</strong><br />You will have the opportunity to learn more about object recognition and how the brain creates representations from visual information. As reimbursement, you will also receive 1 credit point per 10 minutes on SONA.</p>' + 
    '<p><strong>Will the study involve any risk or discomfort for me? If so, what will be done to rectify it?</strong><br />The study should not cause you any serious discomfort. You may feel slight discomfort and strain from watching the visual stimuli for short periods of time, but you will be allotted a break time between experimental blocks to rest your eyes.</p>'+
    '<p>However, please note that this experiment is not suitable for people with a history of photo-sensitive epilepsy due to the way the visual stimuli is presented.</p>' +
    '<p>If you ever experience discomfort, please let the researcher know via email. The experiment can be discontinued at any time.</p>' + 
    '<p><strong>How do you intend to publish or disseminate the results?</strong><br />It is anticipated that the results of this research project will be published and/or presented in a variety of forums. In any publication and/or presentation, information will be provided in such a way that the participant cannot be identified, except with your permission. The information we collect from you in this study will be made completely anonymous in all platforms we share this data to.</p>' + 
    "<p><strong>Will the data and information that I have provided be disposed of?</strong><br />No. Your data will be used as per Western Sydney University's Open Access Policy. This means that data collected from this study can be made available online and world-wide in perpetuity.</p>" + 
    '<p><strong>Can I withdraw from the study?</strong><br />Participation is entirely voluntary and you are not obliged to be involved. If you do participate you can withdraw at any time without giving reason.</p>'+
    '<p>If you do choose to withdraw, any information that you have supplied will be withdrawn from the database whenever possible. However, if your data is already in an Open Access repository, it may not be possible to fully withdraw your data. Please be assured that all data shared to these platforms will be de-identified.</p>' + 
    "<p><strong>Can I tell other people about the study?</strong><br />Yes, you can tell other people about the study by providing them with the Chief Investigator's and/or Research Assistant's contact details. They can contact the Chief Investigator and/or Research Assistant to discuss their participation in the research project and obtain a copy of the information sheet.</p>" + 
    '<p><strong>What if I require further information?</strong><br />Please contact '+researcher_name+' '+researcher_email+' if further information is required.</p>' + 
    '<p><strong>What if I have a complaint?</strong><br />If you have any complaints or reservations about the ethical conduct of this research, you may contact the Ethics Committee through Research Engagement, Development and Innovation (REDI) on Tel +61247360229 or email humanethics@westernsydney.edu.au<br />Any issues you raise will be treated in confidence and investigated fully, and you will be informed of the outcome.<br />If you agree to participate in this study, you may be asked to sign the Participant Consent Form.<br />This study has been approved by the Western Sydney University Human Research Ethics Committee. The Approval number is H15639.</p>' +
    '</div><p></p>' + 
    '<p><h1><strong>CONSENT FORM</strong></h1></p><p></p>' + 
    '<div align=left>' +
    '<p><strong>Project Title: </strong>Decoding the Neural Basis of Object Perception</p>' + 
    '<p>This study has been approved by the Human Research Ethics Committee at Western Sydney University. The ethics reference number is: H15639</p>' +
    '<p><strong>I hereby consent to participate in the above named research project.</strong></p>' + 
    '<p><strong>I acknowledge that:</strong></p>' + 
    '<p>- I have read the online participant information sheet.</p>' + 
    '<p>- The procedures required for the project and the time involved have been clearly explained.</p>' + 
    '<p><strong>I consent to:</strong></p>' +
    '<p>- The recording of behavioural responses to stimuli</p>' + 
    '<p><strong> Data publication, reuse and storage</strong></p>' +
    '<p>This project seeks consent for the data provided to be used in any other projects in the future.</p>' + 
    "<p>To make reuse of the data possible it will be stored under Western Sydney University's Open Access Policy.</p>" + 
    '<p><strong>I understand that:</strong></p>' + 
    '<p>- In relation to publication of the data my involvement is confidential and the information gained during the study may be published but no information about me will be used in any way that reveals my identity.</p>' + 
    '<p>- The researchers intend to make the non-identified data from this project available for other research projects.</p>' + 
    '<p>- I can withdraw from the study at any time without affecting my relationship with the researcher/s, and any organisations involved, now or in the future.</p>' + 
    '</div><p></p>',
    choices: ['I CONSENT TO PARTICIPATE IN THIS STUDY'],
    prompt: "<p><small>Click this button to continue, or close this page to exit.</small></p><p></p>",
    data: {stimulus: 'consentform'},
};
if (!debug) {timeline.push(consentform);}

var demo_form = {
    type: jsPsychSurveyHtmlForm,
    preamble: '<p> Please enter your details </p>',
    html: '<div align=left>'+
        '<p><b>Age</b><br><input name="age" type="number" required/></p>'+
        '<p><b>Gender:</b><br>'+
        '<input type="radio" id="male" name="gender" value="male" required><label for="male"> Male </label>'+
        '<input type="radio" id="female" name="gender" value="female" required><label for="female"> Female </label>'+
        '<input type="radio" id="non-binary" name="gender" value="nb" required><label for="other"> Other </label><br></p>'+
        '<p><b>Handedness:</b><br>'+
        '<input type="radio" id="left" name="handedness" value="left" required><label for="left"> Left </label>'+
        '<input type="radio" id="right" name="handedness" value="right" required><label for="right"> Right </label><br></p>'+
        '<p><b>Is English your native language:</b><br>'+
        '<input type="radio" id="no" name="native" value="no" required><label for="no"> No </label>'+
        '<input type="radio" id="yes" name="native" value="yes" required><label for="yes"> Yes </label><br></p>'+
        '</div>',
    data: {surveyCode:surveyCode,
        test_part:'demographics'},
};
if (!debug) {timeline.push(demo_form);}

var enter_fullscreen = {
    type: jsPsychFullscreen,
    fullscreen_mode: true
}
if (!debug) {timeline.push(enter_fullscreen);}

var measure_screen = {
    type: jsPsychResize,
    item_width: 3 + 3/8,
    item_height: 2 + 1/8,
    prompt: "<p>Click and drag the lower right corner of the box until the box is the same size as a credit card held up to the screen.</p>",
    pixels_per_unit: 100
};
timeline.push(measure_screen)

var instr = {
    type: jsPsychHtmlButtonResponse,
    stimulus: "Thank you for participating in our research project. This research will help us understand more about the human visual system."+
        "<br />This research would not be possible without your time and attention. "+
        "<br /><br /><br /><br /><br /><br /><br /><br /><br",
    choices: ['continue'],
    post_trial_gap: 500,
}
timeline.push(instr)

var instr = {
    type: jsPsychHtmlButtonResponse,
    stimulus: "In this experiment, you will see a word followed by an image."+
        "<br />Sometimes, only part of the image is visible."+
        "<br />Your task is to indicate if the image matches the word.<br />"+
        "<br />" +taskdescription2+ "<br />"+
        "<br />Try to respond as quickly and accurately as you can. "+
        "<br /><br /><br /><br /><br",
    choices: ['continue'],
    post_trial_gap: 500,
}
timeline.push(instr)

var instr = {
    type: jsPsychHtmlButtonResponse,
    stimulus: "Press continue to start two practice trials."+
    "<br />These trials are going to be slower than the experiment."+
    "<br /><br /><br /><br /><br /><br /><br /><br /><br",
    choices: ['continue'],
    on_start: function() {
        document.body.style.background = "#808080"
    },
    post_trial_gap: 1000,
}
timeline.push(instr)

var cursor_off = {
    type: jsPsychCallFunction,
    func: function() {
        document.body.style.cursor = "none";
    }
}
timeline.push(cursor_off);

for (let i = 0; i < 2; i++) {
    var stim = stim_practice[i]
    var obj = obj_practice[i]

    var practice_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: "<img width=256px; src='"+'fixation0.png'+"''></img>",
        choices: "NO_KEYS",
        prompt: "<br /><br /><br /><br /><br />",
        trial_duration: 1000,
    }
    timeline.push(practice_trial)

    var practice_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: "<img width=256px; src='"+obj+"''></img>", 
        choices: "NO_KEYS",
        prompt: "<br /><br /><br /><br /><br /><br />",
        trial_duration: 1000,
        post_trial_gap: 750,
    }
    timeline.push(practice_trial)

    var practice_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: "<img width=256px; src='"+stim+"''></img>", 
        choices: ['z','m'],
        prompt: "<br /><br /><br /><br /><br /><br />",
        trial_duration: 500,
        post_trial_gap: 500,
    }
    timeline.push(practice_trial)

    var practice_trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: taskdescription,
        choices: ['z','m'],
        prompt:  "<br /><br /><br /><br /><br /><br />",
        response_ends_trial: true,
        post_trial_gap: 500,
    }
    timeline.push(practice_trial)
}

var cursor_on = {
    type: jsPsychCallFunction,
    func: function() {
        document.body.style.cursor= "auto";
    }
}
timeline.push(cursor_on)

var instr = {
    type: jsPsychHtmlButtonResponse,
    stimulus: "In the experiment, the words and the images will be faster."+
        "<br />The experiment will begin now."+
        "<br /><br /><br /><br /><br /><br /><br /><br /><br",
    choices: ['continue'],
    on_start: function() {
        document.body.style.background = "#808080"
    },
    post_trial_gap: 1000,
}
timeline.push(instr)

var cursor_off = {
    type: jsPsychCallFunction,
    func: function() {
        document.body.style.cursor= "none";
    }
}
timeline.push(cursor_off);

for (var trialnr=0; trialnr<ntrials; trialnr++) { 
    var stim = stimuli[trialnr]
    var obj = conditions[stim]

    var trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: "<img width=256px; src='"+'fixation0.png'+"''></img>",
        choices: "NO_KEYS",
        prompt: "<br /><br /><br /><br /><br />",
        trial_duration: 500,
        data: {trialnr:trialnr,test_part:'fix',obj:obj,stim:stim,task:taskdescription}, 
    }
    timeline.push(trial)

    var trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: "<img width=256px; src='"+obj+"''></img>",
        choices: "NO_KEYS",
        prompt: "<br /><br /><br /><br /><br /><br />",
        trial_duration: 500,
        post_trial_gap: 500,
        data: {trialnr:trialnr,test_part:'object',obj:obj,stim:stim,task:taskdescription},
    }
    timeline.push(trial)

    var trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: "<img width=256px; src='"+stim+"''></img>",
        choices: ['z','m'],
        prompt: "<br /><br /><br /><br /><br /><br />",
        trial_duration: 100,
        post_trial_gap: 400,
        data: {trialnr:trialnr,test_part:'stim',obj:obj,stim:stim,task:taskdescription},
        on_finish: function(){
            var count = jsPsych.data.get().filter({test_part: 'stim'}).count()
            jsPsych.setProgressBar(count/ntrials)
        }
    }
    timeline.push(trial)
    var trial = {
        type: jsPsychHtmlKeyboardResponse,
        stimulus: taskdescription,
        choices: ['z','m'],
        prompt:  "<br /><br /><br /><br /><br /><br />",
        response_ends_trial: true,
        post_trial_gap: 500,
        data: {trialnr:trialnr,test_part:'response',obj:obj,stim:stim,task:taskdescription},
        on_finish: function(){
            var count = jsPsych.data.get().filter({test_part: 'stim'}).count()
            jsPsych.setProgressBar(count/ntrials)
        }
    }
    timeline.push(trial)
    if (trialnr>0 && !(trialnr%101)) {
        var breaktrial = {
            type: jsPsychHtmlButtonResponse,
            stimulus: "Take a short break."+
                "<br />Press the button to continue.",
            choices: ['continue'],
            post_trial_gap: 1000,
        }
        timeline.push(breaktrial)
    }
}

var cursor_on = {
    type: jsPsychCallFunction,
    func: function() {
        document.body.style.cursor= "auto";
    }
}
timeline.push(cursor_on)

/* finish connection with pavlovia.org */
if (online) {
    var pavlovia_finish = {
        type: jsPsychPavlovia,
        command: "finish"
        }
    timeline.push(pavlovia_finish);
}

var exit_fullscreen = {
    type: jsPsychFullscreen,
    fullscreen_mode: false,
    on_start: function() {
        document.body.style.background = "#FFFFFF"
    },
}
timeline.push(exit_fullscreen)

/* start the experiment */
jsPsych.run(timeline)

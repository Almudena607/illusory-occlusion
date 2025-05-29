import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression,Ridge,LinearRegression
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import LinearSVR,LinearSVC

import mne
from mne.decoding import (
    SlidingEstimator,
    GeneralizingEstimator,
    Scaler,
    cross_val_multiscore,
    LinearModel,
    get_coef,
    Vectorizer,
    CSP,
)

datapath = os.path.expanduser('~/illusory-occlusion/eeg/data')

#%% -------------------------------------------- PREPROCESSING --------------------------------------------

def run_preprocess(subjectnr,overwrite=0):
    '''
    Preprocess the EEG data of a single subject
    This function loads the raw EEG data, preprocesses it, and saves the preprocessed data to a new file.
    
    Parameters
    ----------
    subjectnr : str
        Subject number
    overwrite : bool
        Overwrite existing files. 0 does not overwrite, 1 overwrites
        
    Returns
    -------
    Processed EEG data and behavioural data in BIDS format
    
    Notes
    -----
    high-pass filter: 0.1 Hz
    low-pass filter: 100 Hz
    resample: 1000 Hz
    epoch: -0.1 to 0.8 s relative to stimulus onset
    baseline: -0.1 to 0 s
    '''
    # subject to run
    print(f'preprocessing sub-{subjectnr}')
    os.makedirs(f'{datapath}\derivatives\mne', exist_ok=True)

    outfn = f'{datapath}\derivatives\mne\sub-{subjectnr}_mne_epo.fif'
    behavfn = f'{datapath}\sub-{subjectnr}\eeg\sub-{subjectnr}_task-detection_events.tsv'
    source_behavfn = f'{datapath}\sourcedata\sub-{subjectnr}_task-detection_events.csv'
    source_filename = f'{datapath}\sourcedata\sub-{subjectnr}_task-detection_eeg.bdf'
    raw_filename = f'{datapath}\sub-{subjectnr}\eeg\sub-{subjectnr}_task-detection_eeg.bdf'
    
    if os.path.exists(outfn) and not overwrite:
        print('file exists:',outfn)
        return
    
    if not os.path.exists(source_behavfn):
        print('file does not exists:',source_behavfn)
        return
    
    if not (os.path.exists(source_filename) or os.path.exists(raw_filename)):
        print('file does not exists:',source_filename)
        return

    if not os.path.exists(raw_filename):
        os.makedirs(os.path.dirname(raw_filename), exist_ok=True)
        os.rename(source_filename, raw_filename)

    # Load EEG file
    raw = mne.io.read_raw_bdf(raw_filename, preload=True)
    sfreq = raw.info['sfreq']

    # Read events
    T = pd.read_csv(source_behavfn)

    # Find the STATUS channel and read the values from it
    stim_channel = raw.ch_names.index('Status')
    stim_data = raw.get_data(picks=stim_channel)
    
    # %matplotlib qt
    # raw.plot();
        
    triggertimes = [x for x in 1+np.where((np.diff(stim_data)[0]!=0))[0]]
    triggervalues = stim_data[0][triggertimes]
    
    a,b = np.unique(triggervalues,return_counts=1)
    for x,y in zip(a,b):print('%d %d'%(x,y))
    
    stim_onset_sample = [x for x,y in zip(triggertimes,triggervalues) if y==40708]
    
    seq_onset_sample = [x for x,y in zip(triggertimes,triggervalues) if y==34564]

    if subjectnr == '22':
        stim_onset_sample = [x for x,y in zip(triggertimes, triggervalues) if y == 40708] #sub 22 - technical error, excluded from sample

    elif subjectnr=='26':
        stim_onset_sample = [x for x,y in zip(triggertimes,triggervalues) if y==40708] #didn't get preprocessed without doing this
    
    #stim_offset_sample = [x for x,y in zip(triggertimes,triggervalues) if y==40704]
    #[(x-y)/sfreq for x,y in list(zip(stim_offset_sample,stim_onset_sample))[:20]]
    
    # fix missing triggers
    missingtriggers = len(T)-len(stim_onset_sample)
    if missingtriggers>0:
        print('reconstructing %i triggers'%(missingtriggers))
        print('triggers: %i'%len(stim_onset_sample),'expected: %i'%len(T))
        assert missingtriggers<100, 'too many missing triggers'
        a=[int(x)/sfreq for x in stim_onset_sample]
        b=[x for x in T['time_stimon']]
        for j in range(1,len(a)):
            da = a[j]-a[j-1]
            db = b[j]-b[j-1]
            if da-db > .11:
                print('inserting pos:%i +%.3fs'%(j,a[j-1]+db),'data:%.3fs_diff(%.3fs,%.3fs])'%(da,a[j-1],a[j]),
                      'expected:%.3fs_diff(%.3fs,%.3fs])'%(db,b[j-1],b[j]))
                a.insert(j,a[j-1]+db)
                stim_onset_sample.insert(j,int(round(sfreq*(a[j-1]+db))))
    if len(stim_onset_sample) > len(T):
        print('found not enough events!',len(stim_onset_sample), len(T))
        
    assert len(stim_onset_sample) <= len(T), 'found too many events!'
    assert len(stim_onset_sample) >= len(T), 'found not enough events!'
    stim_onset_sample = np.array(stim_onset_sample)
    events = np.transpose(np.vstack((stim_onset_sample,0*stim_onset_sample,range(0,len(stim_onset_sample)))));
    
    # Behaviour
    T2 = pd.DataFrame({
        'onset': [int(x)/sfreq for x in stim_onset_sample],
        'duration': 0.20,
        'onsetsample': [int(x) for x in stim_onset_sample],
        'eventnumber': range(0, len(stim_onset_sample)),
        'subjectnr': int(subjectnr)
        })
    T2 = pd.concat((T2,T),axis=1)
    
    assert all(np.diff(T2['onset']) - np.diff(T2['time_stimon']) < 0.11), 'event times do not seem to match'
    T2.to_csv(behavfn, sep='\t', index=False)
    T2.to_csv(behavfn.replace('.tsv','.csv'), sep=',', index=False)

    # layout = mne.channels.read_layout('biosemi')
    # raw.set_montage()
    print(raw)
    raw.pick('eeg')
    if subjectnr=='26':
        raw.pick(range(64)) #recorded external electrodes without info, only taking the 64 non-external 

    montage = mne.channels.make_standard_montage("biosemi64")
    #raw.info.ch_names = montage.ch_names
    
    # rename A1 A2 etc to Fp1 AF7 etc
    mne.rename_channels(raw.info,dict(zip(raw.info.ch_names,montage.ch_names)))
    print(raw.info.ch_names)
    raw.set_montage(montage)
    raw.set_eeg_reference()
    raw.filter(l_freq=0.1, h_freq=100)

    epochs = mne.Epochs(raw, events, tmin=-0.1, tmax=0.8, baseline=(-0.1, 0), detrend=0, proj=False, preload=True)
    
    # Resample
    epochs.resample(1000)
    print(epochs)
    epochs.save(outfn,overwrite=1)

    print('Done')



#%% -------------------------------------------- DECODING --------------------------------------------

#%%Control decoding

def run_control_decoding(subjectnr, decode, overwrite=0):
    """
    Run decoding analysis on a single subject
    This function loads the preprocessed data and the behavioural data and runs a decoding analysis using a linear discriminant analysis.
    
    Parameters
    ----------
    subjectnr : str
        Subject number
    decode : str
        Decoding type (position, validity, empty_illusion)
    overwrite : bool
        Overwrite existing files. 0 does not overwrite, 1 overwrites

    Returns
    -------
    scores : array
        The decoding scores

    Notes
    -----
    y : array  
        The target variable. In this case it is determined by the decoding type (decode parameter)
    groups : array
        The groups variable. In this case it is the block sequence number.
    cv : cross-validation generator
    scoring : str
    n_jobs : int
    verbose : int
    """

    infn = f'{datapath}/derivatives/mne/sub-{subjectnr}_mne_epo.fif'
    behavfn = f'{datapath}/sub-{subjectnr}/eeg/sub-{subjectnr}_task-detection_events.tsv'
    outfn = f'{datapath}/derivatives/results_control/sub-{subjectnr}_control_{decode}.csv'
    fig1fn = f'{datapath}/derivatives/results_control/figures/sub-{subjectnr}_control_{decode}.png'
    fig2fn = f'{datapath}/derivatives/results_control/figures/sub-{subjectnr}_control_{decode}_plot.png'
    
    if os.path.exists(infn) and os.path.exists(behavfn):
        if os.path.exists(outfn) and not overwrite:
            print('file exists:',outfn)
            return
        else:
            epochs = mne.read_epochs(infn)

            avg = epochs.average()
            p=avg.plot_joint(show=0)
            p.savefig(fig1fn)

            T_all = pd.read_csv(behavfn,delimiter='\t')
            #idx = ['_invalid_' in x for x in T['stimpath']]
            idx = [not x for x in T_all['istarget']]
            T = T_all[idx]
            X = epochs.get_data()[idx,:,:]
            Y = pd.DataFrame({'time':epochs.times})

            # applying the decoding
            #c,y = np.unique(T['category_name'],return_inverse=True)

            if decode == 'position':
                y = ['_behind_' in x for x in T['stimpath']]
                decode_label = 'behind vs infront'
            elif decode == 'validity':
                y = ['_valid_' in x for x in T['stimpath']]
                decode_label = 'valid vs invalid'
            elif decode == 'shape':
                y = ['_triangle' in x for x in T['stimpath']]
                decode_label = 'triangle vs square'

            if decode == 'illusion':
                idx = [x == 1 for x in T_all['istarget']] #index of the targets
                T = T_all[idx] # T dataframe with only the targets
                y = ['invalid_' in x for x in T['stimpath']]
                if len(y) == 0:
                    print('no targets found')
                    return
                decode_label = 'illusion vs no illusion'

            groups = np.array(T['blocksequencenumber'])
            unique_groups = np.unique(groups)
            #print(unique_groups)
            if len(unique_groups) < 2:
                #in case there are not enough unique groups
                print("Not enough unique groups for LeaveOneGroupOut cross-validation.")
            else:
                groups = T['sequencenumber']
                unique_groups = np.unique(groups)
                


            clf = make_pipeline(LinearDiscriminantAnalysis(priors=(1+0*np.unique(y))/len(np.unique(y))))
            #clf = make_pipeline(StandardScaler(),LinearModel(LinearSVC(dual="auto")))
            time_decod = SlidingEstimator(clf, n_jobs=-1, scoring="balanced_accuracy", verbose=0)
    

            scores = cross_val_multiscore(time_decod, X, y, groups=groups, cv=LeaveOneGroupOut(), n_jobs=-1)
            Y[f'{decode}_decoding'] = np.mean(scores, axis=0)


            # plot decoding per subject
            #overall_y_min = float('inf')
            #overall_y_max = float('-inf')

            ##for subject_data in range(50):
            ### Calculate the y-axis limits for the current subject
            #subject_y_min = min(Y[f'{decode}_decoding'].min())
            #subject_y_max = max(Y[f'{decode}_decoding'].max())

            ### Update the overall minimum and maximum values
            #overall_y_min = min(overall_y_min, subject_y_min)
            #overall_y_max = max(overall_y_max, subject_y_max)
            fig, ax = plt.subplots()
            ax.plot(epochs.times, Y[f'{decode}_decoding'], label=decode_label)
            ax.axhline(1/len(np.unique(y)), color="k", linestyle="--", label="chance")
            ax.set_xlabel("Time (s) relative to stimulus onset")
            ax.set_ylabel("Accuracy")
            ax.legend()
            ax.axvline(0.0, color="k", linestyle="-")
            ax.set_title(f"{decode} decoding")
            #ax.set_ylim(overall_y_min, overall_y_max)
            ax.set_xlim(-0.1, 0.8)
            fig.savefig(fig2fn)

            Y.to_csv(outfn)

    print(f'Control decoding participant {subjectnr} done')


#%% Main decoding


def run_main_decoding(subjectnr,overwrite=0):
    """
    Run decoding analysis on a single subject
    This function loads the preprocessed data and the behavioural data and runs a decoding analysis using a linear discriminant analysis.

    Parameters
    ----------
    subjectnr : str
        Subject number
    overwrite : bool
        Overwrite existing files. 0 does not overwrite, 1 overwrites

    """
    os.makedirs(f'{datapath}/derivatives/results_main', exist_ok=True) 
    infn = f'{datapath}/derivatives/mne/sub-{subjectnr}_mne_epo.fif'
    behavfn = f'{datapath}/sub-{subjectnr}/eeg/sub-{subjectnr}_task-detection_events.tsv'
    fig1fn = f'{datapath}/derivatives/results_main/figures/sub-{subjectnr}_epochs.png'
    
    posval_codes = {'_front_valid_': 'frval', '_front_invalid_': 'frinval', 
                   '_behind_valid_': 'behval', '_behind_invalid_': 'behinval'}
    cat_codes = {'supraordinate': 'sup', 'category': 'cat', 
                   'object': 'obj', 'image': 'im'}

    if os.path.exists(infn) and os.path.exists(behavfn) and not overwrite:
        epochs = mne.read_epochs(infn)
        
        avg = epochs.average()
        p=avg.plot_joint(show=0)
        p.savefig(fig1fn)
    
        TT = pd.read_csv(behavfn,delimiter='\t')
        
        
        for c in posval_codes: 
            outfn = f'{datapath}/derivatives/results_main/sub-{subjectnr}_results_{posval_codes[c]}.csv' 

            if not os.path.exists(outfn):
                idx = [c in x for x in TT['stimpath']]
                T = TT[idx]                
                X = epochs.get_data()[idx,:,:]
                Y = pd.DataFrame({'time':epochs.times})
                
                
                for l in cat_codes:
                    print(f'decoding participant {subjectnr} condition {c} category {l}')
                    # decoding category
                    #j,y = np.unique([x[5:9] for x in T['stimpath']],return_inverse=True)
                    #y = ['_triangle' in x for x in T['stimpath']]
                    
                    supraordinate_y = [int(x[5]) for x in T['stimpath'] if l == list(cat_codes)[0]] #supraordinate
                    category_y = [int(x[5:7]) for x in T['stimpath'] if l == list(cat_codes)[1]] #category
    
                    object_y = [int(x[5:8]) for x in T['stimpath'] if l == list(cat_codes)[2]] #object
                    image_y = [int(x[5:9]) for x in T['stimpath'] if l == list(cat_codes)[3]] #image
                    groups = np.array(T['blocksequencenumber'])
                    
                    if l == list(cat_codes)[0]:
                        y = supraordinate_y
                    elif l == list(cat_codes)[1]:
                        y = category_y
                    elif l == list(cat_codes)[2]:
                        y = object_y
                    elif l == list(cat_codes)[3]:
                        y = image_y
                    
                    clf = make_pipeline(LinearDiscriminantAnalysis(priors=(1+0*np.unique(y))/len(np.unique(y))))
                    #clf = make_pipeline(StandardScaler(),LinearModel(LinearSVC(dual="auto")))
                    time_decod = SlidingEstimator(clf, n_jobs=-1, scoring="balanced_accuracy", verbose=0)
                    scores = cross_val_multiscore(time_decod, X, y, groups=groups, cv=LeaveOneGroupOut(), n_jobs=-1)

                    # Mean scores across cross-validation splits
                    Y[l] = np.mean(scores, axis=0)

                    
                    # Plot
                    fig, ax = plt.subplots()
                    ax.plot(epochs.times, Y[l], label="score")
                    ax.axhline(1/len(np.unique(y)), color="k", linestyle="--", label="chance")
                    ax.set_xlabel("Times")
                    ax.set_ylabel("Accuracy")
                    ax.legend()
                    ax.axvline(0.0, color="k", linestyle="-")
                    ax.set_title("Category decoding")
                    fig.savefig(fig1fn.replace('_epochs',f'_decoding-{l}'))
                
                    Y.to_csv(outfn)
    print('Done')


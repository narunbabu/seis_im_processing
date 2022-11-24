import cv2
# import pytesseract
import pandas as pd
import numpy as np
import segyio
from segyio import TraceField ,BinField
# import matplotlib.pyplot as plt
# from segpy.dataset import Dataset
import logging
from pathlib import Path
from scipy import signal
import toml
from PIL import Image, ImageOps
import datetime 
logger = logging.getLogger(__name__)
import os
from scipy.signal import butter, lfilter, freqz
inputdict=dict(dstpath='_raw.sgy',srcpath='bak_test2.sgy',mintime=1300,mxtime=1500,dt=1,iline=1, xline=169, offset=0)

def doubleInterval(filttrcs,dt):
    #Resampling at 4ms
#     four_secfilttrcs= 
    return filttrcs[::2,:],2*dt
# #     print(four_secfilttrcs.shape)
#     filttrcs=four_secfilttrcs.copy()
#     filttrcs=
#     filttrcs.astype(np.float64)
#     print(filttrcs.shape)
def halftheInterval(filttrcs,dt):
    #Resampling at 1ms
    resfilttrcs= np.zeros((filttrcs.shape[0]*2,filttrcs.shape[1]))
#     print(resfilttrcs.shape)

    resfilttrcs[::2,:]=filttrcs

    # filttrcs.shape
    for i in range(1,len(resfilttrcs[:,0])-1,2):
    #     print(i)
    #     if i==10: break
        resfilttrcs[i,:]=(resfilttrcs[i-1,:]+resfilttrcs[i+1,:])/2
#     filttrcs=resfilttrcs.copy()
#     filttrcs=
    return resfilttrcs.astype(np.float64),int(dt/2)
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def myplot(t,datalist,datainfolist,mtitle='Title'):
#     [data,lfdata,hfdata,output]
    plt.figure(figsize=(12,2))
#     plt.subplot(2, 1, 1)
#     plt.plot(t, data/max(data[nclip:])-np.mean(data/max(data[nclip:]))-lfdata, 'b-', label='data')
    k=0
    for data,info in zip(datalist,datainfolist):
        if k==0: data=data/max(data)
#         if k==0: data=data/max(data)-np.mean(data/max(data))
        plt.plot(t, data,  label=info)
        k+=1
#     plt.plot(t, output,'r-', label='filtered')
    plt.xlabel('Time [sec]')
    plt.title(mtitle)
    plt.grid()
    plt.legend()
    plt.show()
def ampspec(signal,dt,smooth=False): #dt in milliseconds
    SIGNAL = np.fft.fft(signal)
    freq = np.fft.fftfreq(signal.size, d=dt*0.001)
    keep = freq>=0
    SIGNAL = np.abs(SIGNAL[keep])
    freq = freq[keep]
    if smooth:
        freq0=np.linspace(freq.min(),freq.max()/2,freq.size*10)
        f = interp1d(freq, SIGNAL, kind='cubic')
        return freq0, f(freq0)
    else:
        return freq, SIGNAL
def plot_ampspec(freq,amp,name=None,img_fpath=None):
    '''
    plot_ampspec (C) aadm 2016-2018
    Plots amplitude spectrum calculated with fullspec (aageofisica.py).

    INPUT
    freq: frequency
    amp: amplitude
    f_peak: average peak frequency
    '''
    db = 20 * np.log10(amp)
    db = db - np.amax(db)
    f, ax = plt.subplots(nrows=1,ncols=2,figsize=(12,5),facecolor='w')
    ax[0].plot(freq, amp, '-k', lw=2)
    ax[0].set_ylabel('Power')
    ax[1].plot(freq, db, '-k', lw=2)
    ax[1].set_ylabel('Power (dB)')
    for aa in ax:
        aa.set_xlabel('Frequency (Hz)')
        aa.set_xlim([0,np.amax(freq)/1.5])
        aa.set_xlim([0,100])
        aa.grid()
#         aa.axvline(f_peak, color='r', ls='-')
        if name!=None:
            aa.set_title(name, fontsize=16)
    if(img_fpath):
        plt.savefig(img_fpath)
def windowFilt(tarray,data,nclip=0,window=(3,80),order=3,retain_originalscale=False):
    fs=len(tarray)/((tarray[-1]-tarray[0])/1000)
    maxai=np.nanmax(data[nclip:])
    normdata=data[nclip:]/maxai
#     print(maxai)
#     meanai=np.nanmean(normdata)
#     normdata=normdata-meanai
    fc = window[0]  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
#     order=order
    b, a = signal.butter(order, w, 'low')
    lowfreq_data = signal.filtfilt(b, a, normdata)

#     ########################################################
    normdata=normdata-lowfreq_data #removing low frequency component
#     ########################################################
    fc = window[1]  # Cut-off frequency of the filter 70 gave 36%, 12.6ms bs
    w = fc / (fs / 2) # Normalize the frequency fs/2 is the nyquist frequency
    b, a = signal.butter(order, w, 'low')
    window_freq_data = signal.filtfilt(b, a, normdata)
    highfreq_data=normdata-window_freq_data
    return lowfreq_data,window_freq_data,highfreq_data,maxai
def convert(image_filepath: Path, segy_filepath: Path=None, config_filepath: Path=None, *, force=False):
    image_filepath = Path(image_filepath)
    segy_filepath = (segy_filepath and Path(segy_filepath)) or image_filepath.with_suffix(".segy")
    config_filepath = (config_filepath and Path(config_filepath)) or image_filepath.with_suffix(".toml")

    logger.info("segy_filepath = %s", segy_filepath)
    logger.info("image_filepath = %s", image_filepath)
    logger.info("config_filepath = %s", config_filepath)
#     print(segy_filepath)
    return image_filepath,segy_filepath,config_filepath
# def gethorizontalLineFilter(hf_data):
#     hf_data[hf_data>0]=0
#     hf_data[hf_data>-0.05]=0
#     hf_data[hf_data<=-0.05]=1
    
#     ids=np.where(hf_data==1)
#     difids=np.diff(ids)
#     difids[difids>1]
#     spike_interval=int(np.median(difids[difids>1]))
#     # ,np.mean(difids[difids>1])
#     _,spikewidths=np.where(difids>1)
#     spikewidth=int(np.median(np.diff(spikewidths)))
# #     spike_interval,spikewidth
#     halfspikew=int(spikewidth/2)
#     x = np.arange(-halfspikew+1, 1,1)
#     mfilter=x**2/40+0.01
#     if len(mfilter)*2==spikewidth:
#         mfilter=np.array([*mfilter,*mfilter[::-1]])
#     else:
#         mfilter=np.array([*mfilter,mfilter[-1],*mfilter[::-1]])
#     smallfilter=np.append([1]*spike_interval,mfilter)
#     times=int(len(sgray)/len(smallfilter))
#     fullfilter=np.array([*smallfilter]*(times+1))[:len(sgray)]
#     return fullfilter
def gethorizontalLineFilter(hf_data,sgray):
    # hf_data[hf_data>0]=0
    # hf_data[hf_data>-0.05]=0
    # hf_data[hf_data<=-0.05]=1

    nmin=np.mean(hf_data[hf_data<0])
    hf_data[hf_data>nmin]=0
    hf_data[hf_data<=nmin]=1
    
    ids=np.where(hf_data==1)
    difids=np.diff(ids)
    difids[difids>1]
    spike_interval=int(np.nanmedian(difids[difids>1]))
    # ,np.mean(difids[difids>1])
    _,spikewidths=np.where(difids>1)
    spikewidth=int(np.median(np.diff(spikewidths)))
#     spike_interval,spikewidth
    halfspikew=int(spikewidth/2)
    x = np.arange(-halfspikew+1, 1,1)
    mfilter=x**2/40+0.01
    if len(mfilter)*2==spikewidth:
        mfilter=np.array([*mfilter,*mfilter[::-1]])
    else:
        mfilter=np.array([*mfilter,mfilter[-1],*mfilter[::-1]])
    smallfilter=np.append([1]*spike_interval,mfilter)
    times=int(len(sgray)/len(smallfilter))
    fullfilter=np.array([*smallfilter]*(times+1))[:len(sgray)]
    return fullfilter
def getHorizontalRawFilter(hf_data):
    hf_data[hf_data>0]=0
    hf_data[hf_data>-0.05]=1
    hf_data[hf_data<=-0.05]=0.01
    return hf_data
def getSegyKeyprops(file,viennadf,timeranges):
    # viennadf.Start
    names=viennadf['File Name'].apply(lambda x: str(x)[:-4]).values
    try:
        idx=np.where(names==file.replace('_crop.png',''))[0][0]
    except:
        
        try:
            idx=np.where(names==file.replace('_crop_extra.png',''))[0][0]
        except:
            idx=np.where(names==file.replace('_crop.jpg',''))[0][0]
    
    viennadf.iloc[idx]
    ntraces,startsp,endsp=viennadf.iloc[idx][['No. Traces','Start','End']]
    print('ntraces,startsp,endsp ',ntraces,startsp,endsp)
    strc=101
    ntrc=int(ntraces)
    etrc=strc+ntrc-1
    isset=False
    for key in timeranges:
        if key in file:
#             print(key,file)
            stime=timeranges[key][0]
            etime=timeranges[key][1]*1000
            isset=True
            break

    if not isset: 
        print('please check {} is not there in file: {}'.format(key,file))
        return 0
        
    return startsp,endsp,strc,etrc,ntrc,stime,etime


def getmydict(i,filttrcs,delrt,strc):
    return {TraceField.TRACE_SEQUENCE_LINE: i+1,
 TraceField.TraceNumber: i+strc,
 TraceField.EnergySourcePoint: i+1,
 TraceField.CDP: i+strc,
 TraceField.SourceX: 0,
 TraceField.SourceY: 0,
 TraceField.LagTimeA: 0,
 TraceField.DelayRecordingTime: 0,
 TraceField.TRACE_SAMPLE_COUNT: filttrcs.shape[0],
 TraceField.TRACE_SAMPLE_INTERVAL: delrt*1000,
 TraceField.CDP_X: 0,
 TraceField.CDP_Y: 0,
 TraceField.ShotPoint: i+1*100}

# op=[-3,-1,2,4,2,-1,-3]

# op=[-5,-3,-1,2,3.5,7,3.5,2,-1,-3,-5]
# np.conv(traces[10],op)

def getOpProcTraces(traces,op,trange):
    halflenop=int(len(op)/2)
    proctrcs=[]
    for trc in traces:
    #     res=np.convolve(trc,op)[3:len(trc)+3]
        res=np.convolve(trc,op)[halflenop:len(trc)+halflenop]
        f = signal.resample(res, len(trange))
        proctrcs.append(f)
    return proctrcs

def getLowPassfilteredTraces(proctrcs,cutoff = 35.0 ):
    filttrcs=[]
    order = 6
    fs = 500.0       # sample rate, Hz
    # cutoff = 35.0  # desired cutoff frequency of the filter, Hz
    freq=cutoff
    smpls2shift=round(900*pow(freq,-1.274))
    fromsample=smpls2shift
    # Filter the data, and plot both the original and filtered signals.
    for trc in proctrcs:
        y = butter_lowpass_filter(trc, cutoff, fs, order)
        filttrcs.append(np.append(y[fromsample:],np.zeros(fromsample)))
    return np.array(filttrcs)

def default_text_header(inputdict):
    iline, xline, offset,mypath=inputdict['iline'],inputdict['xline'], inputdict['offset'],inputdict['dstpath']
    lines = {
        1: "DATE %s" % datetime.date.today().isoformat(),
        2: "Name: %10s Type: 2D seismic"%mypath,
        3: "For Bhugarbho ",
        4: "Image to segy conversion by Ameyem Geosolutions",
        5: "First CDP: 1.000000 Last CDP: %03d.000000" % xline,
        6: "First SP:  1.000000 Last SP:  %03d.000000" % xline,
        8: " Time min: %03d max: %03d delta: %03d" %(inputdict['mintime'],inputdict['mxtime'], inputdict['dt']),
        9: " Lat min: - max: - delta: -",
        10: " Long min: - max: - delta: -",        
        11: "TRACE HEADER POSITION:",
        12: "  INLINE BYTES %03d-%03d    | OFFSET BYTES %03d-%03d" % (iline, iline + 4, int(offset), int(offset) + 4),
        13: "  CROSSLINE BYTES %03d-%03d |" % (xline, xline + 4),
        
        15: " Trace sample format: IEEE floating point",
        16: " Coordinate scale factor: 1.00000",
        17: "",
        18: " Binary header locations:",
        19: " Sample interval             : bytes 17-18",
        20: " Number of samples per trace : bytes 21-22",
        21: " Trace date format           : bytes 25-26",
        22: "",
        23: " Trace header locations:",
        24: " Inline number               : bytes 5-8",
        25: " SP Number                   : bytes 17-20",
        26: " CDP number                  : bytes 21-24",
        27: " Coordinate scale factor     : bytes 71-72",
        28: " X coordinate                : bytes 73-76",
        29: " Y coordinate                : bytes 77-80",
        30: " Trace start time/depth      : bytes 109-110",
        31: " Number of samples per trace : bytes 115-116",
        32: " Sample interval             : bytes 117-118",        
        39: "END EBCDIC HEADER",
    }
    rows = segyio.create_text_header(lines)
    rows = bytearray(rows, 'ascii')  # mutable array of bytes
    rows[-1] = 128  # \x80 -- Unsure if this is really required...
    return bytes(rows)  # immutable array of bytes that is compatible with strings


def saveAsSegy(filttrcs,inputdict=inputdict,delrt=2,strc=1,setimes=[0,5000]):
    # dstpath,len(spec.samples),filttrcs.shape[0]
    print(filttrcs.shape)   
    f = segyio.open( inputdict['srcpath'], iline=inputdict['iline'], xline=inputdict['xline'], strict=True, ignore_geometry=False, endian='big')
    spec = segyio.tools.metadata(f)
    spec.ilines=np.arange(1,filttrcs.shape[1]+1)
    stime,etime=setimes
    spec.samples = np.arange(stime,etime+2,delrt)

    if len(spec.samples)!=filttrcs.shape[0]:
        print('.error() mismatch', len(spec.samples),filttrcs.shape[0])
        return False
    else:
        print('Reday to go')        
    rows=default_text_header(inputdict )
    theader=bytearray(rows)
    mybin=[]
    i=0
    with segyio.open(inputdict['srcpath'] , iline=inputdict['iline'], xline=inputdict['xline'], strict=True, ignore_geometry=False, endian='big') as src:
        with segyio.create(inputdict['dstpath'], spec) as dst:
            dst.text[0] = theader
            dst.header[i] = src.header[0]
            print(len(dst.header))
            for i,x in enumerate(dst.header[:]):
                x.update(getmydict(i,filttrcs,delrt,strc))
            dst.bin = src.bin
            dst.bin.update({BinField.Interval:delrt*1000,BinField.Samples: filttrcs.shape[0]})
#             print(dst.bin)
            dst.trace = list(filttrcs.T)            
    return True

def getDirections(case):
    useHorfilter=False
    crude_hor_filter= False
    useStepOp=False
    if case==1:
        useHorfilter=True
        
    if case==2:
        useHorfilter=True
        crude_hor_filter= True
        
    if case==3:       
        useHorfilter=True
        useStepOp=True
        
    if case==4:
        useHorfilter=True
        crude_hor_filter= True
        useStepOp=True   
    if case==5:
        useStepOp=True 

    return crude_hor_filter,useStepOp,useHorfilter
def successiveDeduction(traces,ntraces=100):
    for i in range(0,len(traces),ntraces):
        start=i
        endt=i+ntraces
    #     print(start,endt)
        if endt>len(traces):
            endt=len(traces)
        parttraces=traces[i:i+ntraces]
        meantrc=np.mean(parttraces,axis=0)
        maxval=np.max(meantrc)
        meantrc[meantrc<maxval-0.02*maxval]=0
        traces[i:i+ntraces]=parttraces-meantrc
    return traces

def getCounts(mtrc):
    counts={}
    for i in np.unique(mtrc):
        counts[i]=[]
    count=0
    for i in range(1,len(mtrc)):
    #     st=mtrc[i-1]
        if mtrc[i-1]==mtrc[i]:
            count+=1
        else:
            counts[mtrc[i-1]].append(count)
            count=0
    return counts
def getOperatorStep(mtrc,old=True):
    counts=getCounts(mtrc)
    countmeans={}
    for k in counts  :
    #     print(k,': ',np.mean(counts[k]))
        countmeans[k]=np.mean(counts[k])
    mkeys=np.array(list(countmeans.keys()))
    nkeys=len(mkeys)
    opvalues=mkeys+0.5-nkeys/2
    nopdigits=[]
    for k in countmeans:
        val=np.round(countmeans[k])
        nopdigits.append(val)
    nopdigits
    op=[]
    for i in range(len(nopdigits)):
        op.extend([opvalues[i]]*int(nopdigits[i]))
    nopdigits=nopdigits[::-1][1:]
    opvalues=opvalues[::-1][1:]
    for i in range(len(nopdigits)):
        op.extend([opvalues[i]]*int(nopdigits[i]))
    op=np.array(op)
    op-=np.mean(op)
    if not old:
        return op[::2]
    return op
def getOperator(mtrc,old=True):
    
    counts=getCounts(mtrc)
    countmeans={}
    for k in counts  :
        # print(k,': ',np.mean(counts[k]))
        if len(counts[k])>0:
            countmeans[k]=np.mean(counts[k])
        
    hlfop_len=int(np.sum([countmeans[k] for k in countmeans]))
    f=10
    signal_len=2*hlfop_len/1000
    print('signal_len ',signal_len)
    # print(2*hlfop_len)
    dt=0.002

    # mlen=peak_loc*2
    if old:
        mlen=2*signal_len
    else:
        mlen=signal_len
    peak_loc=mlen/2
    t = np.linspace(-peak_loc, mlen - peak_loc - dt, int(mlen / dt))

    # Shift time to the correct location
    # t_out = t + peak_loc  # time shift Ricker wavelet based on peak_loc

    # Generate Ricker wavelet signal based on reference
    op = (1 - 2 * np.pi ** 2 * f ** 2 * t ** 2) * np.exp(
        -np.pi ** 2 * f ** 2 * t ** 2)    
    op=op-op.mean()
    return op
def findMidpointsofHorlines(selim,w):
    res=selim.sum(axis=1).astype(float)
    res[res<=w*0.8]=0
    res[res>w*0.8]=1.0
    diff=np.diff(res)
    posids=np.where(diff==1.0)[0]
    negids=np.where(diff==-1.0)[0]
    print(posids,negids)
    arrlen=len(negids) if len(posids)>len(negids) else len(posids)
    midpoints=((posids[:arrlen]+negids[:arrlen])/2).astype(int)    
    return midpoints
# for i,j in zip(posids,negids)
# plt.plot(res)
# array([  25,  253,  820, 1610, 2397, 3191, 3954])


def getWidthofHorline(resim): #having a line
    widths=[]
    for i in range(15):
        diff=np.diff(resim[:,i].astype(float))
        idxs=np.where(diff!=0)[0]

        if len(idxs)>1:
            npixels=idxs[1]-idxs[0]
            widths.append(npixels)
    #         print()
#             plt.plot(resim[:,i])
    width=np.median(widths)
    return width

def precisionFiltering(clipped_im):
    ncols=3
    resim=clipped_im[:100,30:200] # This to be checked with image
    width=int(getWidthofHorline(resim))
    print('width',width)
    
    # Finding the midpoints of horizontal lines
    selim=clipped_im[:,:200]
    h,w=selim.shape
    midpoints=findMidpointsofHorlines(selim,w)
    print('midpoints ',midpoints)
    mfilter=np.vstack([np.zeros((width,ncols))+0.5,np.ones((width,ncols)),np.zeros((width,ncols))+0.5])
    
    #Application of filter
    for mp in midpoints:
    #     mp=midpoints[0]
        pad=20
        if pad>mp:
            pad=mp
        resim=clipped_im[mp-pad:mp+pad,:]
        if mp==midpoints[0]:
            plt.figure(figsize=(12,4))
            plt.imshow(resim[:,:200])
        opencvOutput = cv2.filter2D(resim, -1, mfilter)
        resim[(opencvOutput>(ncols*4-1))&(opencvOutput<ncols*7)]=0
        clipped_im[mp-pad:mp+pad,:]=resim
        if mp==midpoints[0]:
            plt.figure(figsize=(12,4))
            plt.imshow(resim[:,:200])
    return clipped_im
# def img2rawtrace(mthresh,stime,etime,ntrc): #key function need filters before
#     thresh=mthresh.copy()
#     trange=np.arange(stime,etime+1,2).astype(int)
#     pixper_trc=thresh.shape[1]/ntrc
#     print('ntrc,thresh.shape,pixper_trc ',ntrc,thresh.shape,pixper_trc)

#     pixrange=np.arange(0,thresh.shape[1]+1,pixper_trc).astype(int)
#     # # 
#     # thresh[thresh<100]=0
#     # thresh[thresh>100]=1
    
#     tmean=thresh.mean()
#     if tmean>100:
#         tmean=100
    
#     thresh[thresh<tmean]=0
#     thresh[thresh>tmean]=1
#     # plt.hist(thresh)

#     traces=[]
#     for i in range(len(pixrange)-1):
#     #     print(pixrange[i],pixrange[i+1])
#         trc=pixper_trc*thresh[:,pixrange[i]:pixrange[i+1]].sum(axis=1)/(pixrange[i+1]-pixrange[i])
#         nlesThalf=np.sum(trc<=pixper_trc/2)
#         ngreThalf=np.sum(trc>pixper_trc/2)
#         if ngreThalf/nlesThalf<0.01:
#             trc[trc<=pixper_trc/2]=trc[trc<=pixper_trc/2]*0.3
# #     print(nlesThalf,ngreThalf,ngreThalf/nlesThalf)
    
#         traces.append(trc)
#     traces=np.array(traces).astype(float)
#     return traces
def img2rawtrace(mthresh,stime,etime,ntrc): #key function need filters before
    thresh=mthresh.copy()
    trange=np.arange(stime,etime+1,2).astype(int)
    pixper_trc=thresh.shape[1]/(ntrc+1)
    halfpixper_trc=int(pixper_trc/2)
    print('ntrc,thresh.shape,pixper_trc ',ntrc,thresh.shape,pixper_trc)

    pixrange=np.arange(halfpixper_trc,thresh.shape[1]-halfpixper_trc,pixper_trc).astype(int)
    # # 
    # thresh[thresh<100]=0
    # thresh[thresh>100]=1
    
    tmean=thresh.mean()
    if tmean>100:
        tmean=100
    
    thresh[thresh<tmean]=0
    thresh[thresh>tmean]=1
    # plt.hist(thresh)

    traces=[]
    for i in range(len(pixrange)-1):
        # trc=pixper_trc*thresh[:,pixrange[i]-halfpixper_trc:pixrange[i+1]+halfpixper_trc].sum(axis=1)/(pixrange[i+1]-pixrange[i]+pixper_trc)
    #     print(pixrange[i],pixrange[i+1])
        n=5
        trc=pixper_trc*thresh[:,pixrange[i]-halfpixper_trc-n:pixrange[i+1]+halfpixper_trc+n].sum(axis=1)/(pixrange[i+1]-pixrange[i]+pixper_trc+2*n)
        nlesThalf=np.sum(trc<=pixper_trc/2)
        ngreThalf=np.sum(trc>pixper_trc/2)
        if ngreThalf/nlesThalf<0.01:
            trc[trc<=pixper_trc/2]=trc[trc<=pixper_trc/2]*0.3

    
        traces.append(trc)
    traces=np.array(traces).astype(float)
    return traces
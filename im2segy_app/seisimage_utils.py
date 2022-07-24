import cv2
import numpy as np
# import matplotlib.pyplot as plt
import os
# from scipy import convolve
from scipy.signal import savgol_filter
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
# def rollavg_convolve(a,n):
#     'scipy.convolve'
#     assert n%2==1
#     return convolve(a,np.ones(n,dtype='float')/n, 'same')[n//2:-n//2+1] 

def getedgeIndexes(res):
    a,b=np.histogram(res,50)
    a[a<len(res)*0.002]=0
    idxs=np.where(a==0)
    res[res<=b[idxs[0][0]]]=0
    res[res>=b[idxs[0][0]]]=1
    diff=np.diff(res)
    # diff=np.diff(res)
    return np.where(diff!=0)
def cleanbigarray(idyes):
    if len(idyes)>2:
        diff=np.diff(idyes)
    #         print(diff)
        idy=np.argmax(diff)
        return np.array([idyes[idy],idyes[idy+1]])
    else:
        return idyes
        
def getSectionBoundary(gray): #with 0 and 1s
    thresh=gray.mean()
    gray[gray<=thresh]=1
    gray[gray>=thresh]=0
    resx=gray.sum(axis=0)
    resy=gray.sum(axis=1)
    idxes=getedgeIndexes(resx)
    idyes=getedgeIndexes(resy)
    idxes,idyes=idxes[0],idyes[0]
    idyes=cleanbigarray(idyes)
    idxes=cleanbigarray(idxes)
    return idxes,idyes

# Following three functions are for horizontal filtering
def findMidpointsofHorlines_old(selim):
    res=selim.sum(axis=1).astype(float)
    h,w=selim.shape
    res[res<=w*0.8]=0
    res[res>w*0.8]=1.0
    diff=np.diff(res)
    posids=np.where(diff==1.0)[0]
    negids=np.where(diff==-1.0)[0]
    print('posids,negids in findMidpointsofHorlines',posids,negids)
    arrlen=len(negids) if len(posids)>len(negids) else len(posids)
    midpoints=((posids[:arrlen]+negids[:arrlen])/2).astype(int)    
    return midpoints

def precisionFiltering(clipped_im):
    ncols=3
    resim=clipped_im[:100,30:200] # This to be checked with image
    width=int(getWidthofHorline(resim))
    print('width',width)
    
    # Finding the midpoints of horizontal lines
    selim=clipped_im[:,:200]
    h,w=selim.shape
    midpoints=findMidpointsofHorlines(selim)
    print('midpoints ',midpoints)
    mfilter=np.vstack([np.zeros((width,ncols))+0.5,np.ones((width,ncols)),np.zeros((width,ncols))+0.5])
    
    #Application of filter
    for mp in midpoints:
    #     mp=midpoints[0]
        pad=20
        if pad>mp:
            pad=mp
        resim=clipped_im[mp-pad:mp+pad,:]
        # if mp==midpoints[0]:
        #     plt.figure(figsize=(12,4))
        #     plt.imshow(resim[:,:200])
        opencvOutput = cv2.filter2D(resim, -1, mfilter)
        resim[(opencvOutput>(ncols*4-1))&(opencvOutput<ncols*7)]=0
        clipped_im[mp-pad:mp+pad,:]=resim
        # if mp==midpoints[0]:
        #     plt.figure(figsize=(12,4))
        #     plt.imshow(resim[:,:200])
    return clipped_im


def getRotationAngle(clipped_im):
    red_im = cv2.resize(clipped_im, (0, 0), fx = 0.1, fy = 0.1)
    # red_im=clipped_im
    (h, w) = red_im.shape[:2]
    print(h,w)
    (cX, cY) = (w // 2, h // 2)
    score=[]
    angles=np.arange(-5,5,0.1)
    for angle in angles:
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        rotated = cv2.warpAffine(red_im, M, (w, h))
        res=rotated.sum(axis=0)
        sres=np.sort(res)[::-1]
        
        score.append(np.sum(sres[:10]))
    idmax=np.argmax(score)
    # print(idmax,angles[idmax],score[idmax])
    return angles[idmax]

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
def movAverage(arr,window_size):
    moving_averages = []
    i = 0
    # Loop through the array t o
    #consider every window of size 3
    while i < len(arr) - window_size + 1:

        # Calculate the average of current window
        window_average = round(np.sum(arr[
          i:i+window_size]) / window_size, 2)

        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)

        # Shift window to right by one position
        i += 1
    return np.array(moving_averages)

def getColumnShifts_old(clipped_im,zerotlineid,pad2blookedat,mfilter):
    mp=zerotlineid
    pad=pad2blookedat
    if pad>mp:
        pad=mp
    print('padding ',pad)
    resim=clipped_im[mp-pad:mp+pad,:].astype(float)
    resim[resim<=0]=-1.0

    res=resim.sum(axis=0)
    nonzeroid=np.where(res[:50]>-resim.shape[0] )[0][0]
    
    opencvOutput = cv2.filter2D(resim, -1, mfilter)

    mid=np.argmax(opencvOutput[:,nonzeroid])
    linelocations=[mid]
    for i in range(nonzeroid+1,opencvOutput.shape[1]):   
        if linelocations[-1]>=1:
            mid=np.argmax(opencvOutput[linelocations[-1]-1:linelocations[-1]+2,i])
            linelocations.append(linelocations[-1]-1+mid)
        else:
            mid=np.argmax(opencvOutput[:,i])
            linelocations.append(mid)
        if len(linelocations)>6:
            if np.mean(linelocations[-5:-1])<linelocations[-1]-2:
#                 print(i,np.mean(linelocations[-5:-1]),linelocations[-1]-2)
                mid=np.argmax(opencvOutput[:,i])
                linelocations[-1]=mid

    return np.arange(nonzeroid,len(linelocations)+nonzeroid),np.array(linelocations)
def getCleanedCurve_old(shifts2bapplied):
    # mav=movAverage(shifts2bapplied,5)
    mav = savgol_filter(shifts2bapplied, 101, 3) # window size 51, polynomial order 3
    pttable=shifts2bapplied>mav+1
    nttable=shifts2bapplied<mav-1
    shifts2bapplied[pttable]=mav[pttable]+1
    shifts2bapplied[nttable]=mav[nttable]+1
    return shifts2bapplied
def findHorlineIndex(clipped_im):
    h,w=clipped_im.shape
    selim=clipped_im[:int(h/10),:int(w/55)]
    horizontal = cv2.adaptiveThreshold(selim,255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,-2)
    rows,cols = horizontal.shape
    horizontalsize = 10
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize,1))
    # horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1))
    horizontal = cv2.dilate(horizontal, horizontalStructure, (-1, -1))
    selim=horizontal.astype(float)

    # selim[selim<=127.0]=1
    # selim[selim>127.0]=0
    res=selim.sum(axis=1)
#     # print(res.mean())
#     res[res<=res.mean()]=1
#     res[res>res.mean()]=0

#     # h,w=selim.shape
#     # res[res<=w*0.8]=0
#     # res[res>w*0.8]=1.0
#     diff=np.diff(res)
#     posids=np.where(diff==1.0)[0]
#     negids=np.where(diff==-1.0)[0]
#     # print('posids,negids in findMidpointsofHorlines',posids,negids)
#     arrlen=len(negids) if len(posids)>len(negids) else len(posids)
#     midpoints=((posids[:arrlen]+negids[:arrlen])/2).astype(int)  
    return np.argmin(res)
def findMidpointsofHorlines(clipped_im):
    h,w=clipped_im.shape
    selim=clipped_im[:int(h/5),:int(w/55)]
    print('selim.shape in findMidpointsofHorlines',selim.shape)
    horizontal = cv2.adaptiveThreshold(selim,255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,-2)
    rows,cols = horizontal.shape
    # horizontalsize = int(cols / 10)
    horizontalsize=5
    print('horizontalsize ',horizontalsize)
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize,1))
    # horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1))
    horizontal = cv2.dilate(horizontal, horizontalStructure, (-1, -1))
    selim=horizontal.astype(float)

    # selim[selim<=127.0]=1
    # selim[selim>127.0]=0
    res=selim.sum(axis=1)
    # print(res.mean())
    res[res<=res.mean()]=1
    res[res>res.mean()]=0

    # h,w=selim.shape
    # res[res<=w*0.8]=0
    # res[res>w*0.8]=1.0
    diff=np.diff(res)
    posids=np.where(diff==1.0)[0]
    negids=np.where(diff==-1.0)[0]
    print('posids,negids in findMidpointsofHorlines',posids,negids)
    arrlen=len(negids) if len(posids)>len(negids) else len(posids)
    midpoints=((posids[:arrlen]+negids[:arrlen])/2).astype(int)  
    print('midpoints ',midpoints)
    return midpoints

def getColumnShifts_old(clipped_im,zerotlineid,pad2blookedat):
    
    mp=zerotlineid
    pad=pad2blookedat
    fpad,bpad=pad,pad
#     print(mp,pad)
    if pad>mp:
        fpad=mp
    resim=clipped_im[mp-fpad:mp+bpad,:]
    horizontal = cv2.adaptiveThreshold(resim,255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,-2)
    rows,cols = horizontal.shape
#     print('rows,cols ',rows,cols )
#     horizontalsize = int(cols / 250)
    horizontalsize=10
#     print('horizontalsize',horizontalsize)
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize,1))
    # horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1))
    horizontal = cv2.dilate(horizontal, horizontalStructure, (-1, -1))
    resim=horizontal.astype(float)
    width=5
    ncols=horizontalsize
    mfilter=np.vstack([np.zeros((width,ncols))-0.5,np.ones((width,ncols)),np.zeros((width,ncols))-0.5])
    opencvOutput = cv2.filter2D(resim, -1, mfilter)
    idxs=np.argmin(opencvOutput,axis=0)
    clnidxs=getCleanedCurve(idxs)
    
    return np.arange(len(clnidxs)),clnidxs

def getCleanedCurve(shifts2bapplied,returnsmooth=False):
    # mav=movAverage(shifts2bapplied,5)
    x=np.arange(len(shifts2bapplied))
#     y=idxs
    z = np.polyfit(x, shifts2bapplied, 3)
    f = np.poly1d(z)
    mav = f(x)
#     mav = savgol_filter(shifts2bapplied, 101, 3) # window size 51, polynomial order 3
    pttable=shifts2bapplied>mav+1
    nttable=shifts2bapplied<mav-1
    if sum(pttable)>0: shifts2bapplied[pttable]=mav[pttable]+1
    if sum(nttable)>0:shifts2bapplied[nttable]=mav[nttable]-1
    if returnsmooth:
        return mav.astype(int)
    return shifts2bapplied
def getColumnShifts(clipped_im,zerotlineid,pad2blookedat):
    mp=zerotlineid
    pad=int(clipped_im.shape[0]/30)
    fpad,bpad=pad,pad
    #     print(mp,pad)
    if pad>mp:
        fpad=mp
    resim=clipped_im[mp-fpad:mp+bpad,:]

    horizontal = cv2.adaptiveThreshold(resim,255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,15,-2)
    rows,cols = horizontal.shape
    horizontalsize=10
    #     print('horizontalsize',horizontalsize)
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize,1))
    # horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1))
    horizontal = cv2.dilate(horizontal, horizontalStructure, (-1, -1))

    resim=horizontal.astype(float)
    width=5
    ncols=horizontalsize
    mfilter=np.vstack([np.zeros((width,ncols))-0.5,np.ones((width,ncols)),np.zeros((width,ncols))-0.5])
    opencvOutput = cv2.filter2D(resim, -1, mfilter)
    ffpad=3 if fpad/2 >3 else int(fpad/2 )
    fbpad=3
    midxs=[]
    window=10
    for i in range(window,opencvOutput.shape[1],window):
        start,endx=mp-ffpad,mp+fbpad
        if start<0:
            start=0
        poo=opencvOutput[start:endx,i-window:i]    
    #     print(i)
        idxs=np.argmin(poo,axis=0)
        nowidxs=start+idxs

        # poo=opencvOutput[mp-ffpad:mp+fbpad,i-window:i]    
        # idxs=np.argmin(poo,axis=0)
        # nowidxs=mp-ffpad+idxs
        midxs.extend(list(nowidxs))
        mp=int(np.mean(nowidxs))
    poo=opencvOutput[mp-ffpad:mp+fbpad,i:]    
    idxs=np.argmin(poo,axis=0)
    nowidxs=mp-ffpad+idxs
    midxs.extend(list(nowidxs))
    return np.arange(len(midxs)), np.array(midxs)


def getStraightenedImage(clipped_im,colnumbers,shifts2bapplied):
    # shifted_image=np.zeros_like(clipped_im).astype(np.uint8)
    shifted_image=clipped_im.copy()
    shape=clipped_im.shape
    if len(shape)==2:

    # idlist=np.arange(nonzeroid,len(linelocations)+nonzeroid)
        for i,cor in zip(colnumbers,shifts2bapplied):
            if cor!=0:
                shifted_image[:-cor,i]=clipped_im[cor:,i]
            else:
                shifted_image[:,i]=clipped_im[:,i]
    else:
        for i,cor in zip(colnumbers,shifts2bapplied):
            if cor!=0:
                shifted_image[:-cor,i,:]=clipped_im[cor:,i,:]
            else:
                shifted_image[:,i,:]=clipped_im[:,i,:]
    return shifted_image
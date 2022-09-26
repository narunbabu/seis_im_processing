import pandas as pd
# from PyQt5 import QtCore
import numpy as np
def tryconvert(value, default, *types):
    for t in types:
        try:
            return t(value)
        except (ValueError, TypeError):
            continue
    return default
def getOriginsValperUnit(locations,values):
    def getXdYd(twopoints,twovals,isy=True):
        distance=twovals[1]-twovals[0]
        y=twopoints[1,1]-twopoints[0,1]
        x=twopoints[1,0]-twopoints[0,0]        
        theta=abs(np.arctan(y/x))
        xd=distance*np.cos(theta)
        yd=distance*np.sin(theta)

        if not isy:
            xperpixunit=xd/x
            minval=twovals[0]
            minx=twopoints[0,0]
            xval_at_orgin=minval-minx*xperpixunit
            return xval_at_orgin,xperpixunit
        else:
            yperpixunit=yd/y
            minval,miny=twovals[0],twopoints[0,1]           
            yval_at_orgin=minval-miny*yperpixunit
            return yval_at_orgin,yperpixunit
#         return x,y,xd,yd,xsignval,ysignval

    #X-axis
    twovals=np.array(values[:2])
    twopoints=locations[:2,:]
    idxs=np.argsort(twopoints[:,0])

    twopoints=twopoints[idxs,:]
    twovals=twovals[idxs]    
    xval_at_orgin,xperpixunit=getXdYd(twopoints,twovals,isy=False)
#     print('xval_at_orgin,xperpixunit',xval_at_orgin,xperpixunit)
#     print('***********************************************')

    #Y-axis
    twovals=np.array(values[2:])
    twopoints=locations[2:,:]
    idys=np.argsort(twopoints[:,1])
    twopoints=twopoints[idys,:]
    twovals=twovals[idys]
    yval_at_orgin,yperpixunit=getXdYd(twopoints,twovals,isy=True)
#     print('yval_at_orgin,yperpixunit',yval_at_orgin,yperpixunit)
    return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit
class CoordConverter:
    def __init__(self,coords,lines):
        super().__init__()
        self.coords=coords
        self.lines=lines
    def processCoordinates(self):
        locations=[]
        values=[]
        for row in self.coords:
        #     print(row['name'],row['pixel_loc'],row['value'])
            locations.append([row['pixel_loc'].x(),row['pixel_loc'].y()])
            values.append(row['value'])
        locations=np.array(locations)
        xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit = getOriginsValperUnit(locations,values)
        return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit
    def getLineCoords(self):
        xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit=self.processCoordinates()
        lno=[]
        xs=[]
        ys=[]
        attr=[]
        for key in self.lines:
            if len(self.lines[key])>0:
                for a,l in self.lines[key]:
                    xs.append(l.x())
                    ys.append(l.y())
                    lno.append(key)
                    attr.append(a)
        df=pd.DataFrame({'lno':lno,'shotpoint':attr,'X':xs,'Y':ys})
        df['X-Coord']=xval_at_orgin+df.X*xperpixunit
        df['Y-Coord']=yval_at_orgin+df.Y*yperpixunit
        df=df.drop_duplicates(subset=['X','Y'])        
        df.loc[df.index,['shotpoint']]=df.shotpoint.apply(lambda x: tryconvert(x, np.nan, int))
        df = df[df['shotpoint'].notna()]
        return df.sort_values(by=['lno','shotpoint'])
# def getOriginsValperUnit(locations,values):

#     def getXdYd(twopoints,twovals):
#         distance=twovals[1]-twovals[0]

#         y=twopoints[1,1]-twopoints[0,1]
#         x=twopoints[1,0]-twopoints[0,0]
#         print(distance,y)
#         theta=np.arctan(y/x)
#         print(x,y,theta)
#         theta,np.tan(theta),y/x
#         xd=distance*np.cos(theta)
#         yd=distance*np.sin(theta)
#         aytest=y>0
#         bytest=distance>0
#         if not all([aytest,bytest]):
#             ysignval=-1
#         else:
#             ysignval=1     

#         axtest=x>0
#         bxtest=distance>0
#         if not all([axtest,bxtest]):
#             xsignval=-1
#         else:
#             xsignval=1
#         return x,y,xd,yd,xsignval,ysignval

#     #X-axis
#     twovals=values[:2]
#     twopoints=locations[:2,:]
#     x,y,xd,yd,xsignval,ysignval=getXdYd(twopoints,twovals)

#     minidx=np.argmin(twopoints[:,0])
#     minval=twovals[minidx]
#     minx=twopoints[minidx,0]
#     xperpixunit=xd/x
#     xval_at_orgin=minval-minx*xperpixunit*xsignval

#     #Y-axis
#     twovals=values[2:]
#     twopoints=locations[2:,:]
#     x,y,xd,yd,xsignval,ysignval=getXdYd(twopoints,twovals)
#     # print(xd,yd)

#     midy=np.argmin(twopoints[:,1])
#     minval=twovals[midy]
#     miny=twopoints[midy,1]
#     yperpixunit=yd/y
#     yval_at_orgin=minval-miny*yperpixunit*ysignval

#     return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit

# class CoordConverter:
#     def __init__(self,coords,lines):
#         super().__init__()
#         self.coords=coords
#         self.lines=lines

# # class CoordConverter:
# #     def __init__(self,coords,lines):
# #         super().__init__()
# #         self.coords=coords
# #         self.lines=lines

#     # def processCoordinates(self):
#     # #     rows=np.load(coordsfile,allow_pickle=True)
#     # #     rows
#     #     locations=[]
#     #     values=[]
#     #     for row in self.coords:
#     #     #     print(row['name'],row['pixel_loc'],row['value'])
#     #         locations.append([row['pixel_loc'].x(),row['pixel_loc'].y()])
#     #         values.append(row['value'])
#     #     locations=np.array(locations)
#     #     xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit = self.getOriginsValperUnit(locations,values)
#     #     return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit
#     # def getLineCoords(self):
#     #     lno=[]
#     #     xs=[]
#     #     ys=[]
#     #     attr=[]
#     #     for key in self.lines:
#     #         if len(self.lines[key])>0:
#     #             for a,l in self.lines[key]:
#     #                 xs.append(l.x())
#     #                 ys.append(l.y())
#     #                 lno.append(key)
#     #                 attr.append(a)
#     #     xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit=self.processCoordinates()
#     #     df=pd.DataFrame({'lno':lno,'shotpoint':attr,'X':xs,'Y':ys})
#     #     df['X-Coord']=xval_at_orgin+df.X*xperpixunit
#     #     df['Y-Coord']=yval_at_orgin+df.Y*yperpixunit
#     #     return df
    
#     def processCoordinates(self):
#     #     rows=np.load(coordsfile,allow_pickle=True)
#     #     rows
#         locations=[]
#         values=[]
#         for row in self.coords:
#         #     print(row['name'],row['pixel_loc'],row['value'])
#             locations.append([row['pixel_loc'].x(),row['pixel_loc'].y()])
#             values.append(row['value'])
#         locations=np.array(locations)
#         xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit = getOriginsValperUnit(locations,values)
#         return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit
#     def getLineCoords(self):
#         xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit=self.processCoordinates()
#         A,B=self.coords[2],self.coords[3]
#         if not (A['value']>B['value'])==(A['pixel_loc'].y()>B['pixel_loc'].y()):
#             yperpixunit=-yperpixunit
#         A,B=self.coords[0],self.coords[1]
#         print('A,B ',A,B,[A['value']>B['value'],A['pixel_loc'].x()>B['pixel_loc'].x()],all([A['value']>B['value'],A['pixel_loc'].x()>B['pixel_loc'].x()]))
#         if not (A['value']>B['value'])==(A['pixel_loc'].x()>B['pixel_loc'].x()):
#             xperpixunit=-xperpixunit
#         lno=[]
#         xs=[]
#         ys=[]
#         attr=[]
#         for key in self.lines:
#             if len(self.lines[key])>0:
#                 for a,l in self.lines[key]:
#                     xs.append(l.x())
#                     ys.append(l.y())
#                     lno.append(key)
#                     attr.append(a)
#         df=pd.DataFrame({'lno':lno,'shotpoint':attr,'X':xs,'Y':ys})
#         df['X-Coord']=xval_at_orgin+df.X*xperpixunit
#         df['Y-Coord']=yval_at_orgin+df.Y*yperpixunit
#         return df
#     # def getOriginsValperUnit(self,locations,values):

#     #     def getXdYd(twopoints,twovals):
#     #         distance=twovals[1]-twovals[0]
#     #         y=twopoints[1,1]-twopoints[0,1]
#     #         x=twopoints[1,0]-twopoints[0,0]
#     #         theta=np.arctan(y/x)
#     #         # print(x,y,theta)
#     #         theta,np.tan(theta),y/x
#     #         xd=distance*np.cos(theta)
#     #         yd=distance*np.sin(theta)
#     #         return x,y,xd,yd

#     #     #X-axis
#     #     twovals=values[:2]
#     #     twopoints=locations[:2,:]
#     #     x,y,xd,yd=getXdYd(twopoints,twovals)

#     #     minidx=np.argmin(twopoints[:,0])
#     #     minval=twovals[minidx]
#     #     minx=twopoints[minidx,0]
#     #     xperpixunit=xd/x
#     #     xval_at_orgin=minval-minx*xperpixunit

#     #     #Y-axis
#     #     twovals=values[2:]
#     #     twopoints=locations[2:,:]
#     #     x,y,xd,yd=getXdYd(twopoints,twovals)
#     #     # print(xd,yd)

#     #     midy=np.argmin(twopoints[:,1])
#     #     minval=twovals[midy]
#     #     miny=twopoints[midy,1]
#     #     yperpixunit=yd/y
#     #     yval_at_orgin=minval-miny*yperpixunit

#     #     return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit

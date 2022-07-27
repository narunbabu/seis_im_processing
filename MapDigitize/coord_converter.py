import pandas as pd
from PyQt5 import QtCore
import numpy as np
class CoordConverter:
    def __init__(self,coords,lines):
        super().__init__()
        self.coords=coords
        self.lines=lines
    def getOriginsValperUnit(self,locations,values):

        def getXdYd(twopoints,twovals):
            distance=twovals[1]-twovals[0]
            y=twopoints[1,1]-twopoints[0,1]
            x=twopoints[1,0]-twopoints[0,0]
            theta=np.arctan(y/x)
            # print(x,y,theta)
            theta,np.tan(theta),y/x
            xd=distance*np.cos(theta)
            yd=distance*np.sin(theta)
            return x,y,xd,yd

        #X-axis
        twovals=values[:2]
        twopoints=locations[:2,:]
        x,y,xd,yd=getXdYd(twopoints,twovals)

        minidx=np.argmin(twopoints[:,0])
        minval=twovals[minidx]
        minx=twopoints[minidx,0]
        xperpixunit=xd/x
        xval_at_orgin=minval-minx*xperpixunit

        #Y-axis
        twovals=values[2:]
        twopoints=locations[2:,:]
        x,y,xd,yd=getXdYd(twopoints,twovals)
        # print(xd,yd)

        midy=np.argmin(twopoints[:,1])
        minval=twovals[midy]
        miny=twopoints[midy,1]
        yperpixunit=yd/y
        yval_at_orgin=minval-miny*yperpixunit

        return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit
    def processCoordinates(self):
    #     rows=np.load(coordsfile,allow_pickle=True)
    #     rows
        locations=[]
        values=[]
        for row in self.coords:
        #     print(row['name'],row['pixel_loc'],row['value'])
            locations.append([row['pixel_loc'].x(),row['pixel_loc'].y()])
            values.append(row['value'])
        locations=np.array(locations)
        xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit = self.getOriginsValperUnit(locations,values)
        return xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit
    def getLineCoords(self):
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
        xval_at_orgin,xperpixunit,yval_at_orgin,yperpixunit=self.processCoordinates()
        df=pd.DataFrame({'lno':lno,'shotpoint':attr,'X':xs,'Y':ys})
        df['X-Coord']=xval_at_orgin+df.X*xperpixunit
        df['Y-Coord']=yval_at_orgin+df.Y*yperpixunit
        return df
import pickle
import numpy as np
zvals = {}
rimOffset = 0
backXMax = 8 #width of 16, origin is at center of bottom of backboard, +x is to the right
backYMax = 9-rimOffset #measured from bottom of center of rim, +y is vertically up
backYMin = rimOffset
backLengthStep = 1
#generates points of flat backboard
for backX in np.arange(0,backXMax+backLengthStep,backLengthStep):
    for backY in np.arange(backYMin,backYMax+backLengthStep,backLengthStep):
        print(backX,backY)
        zvals[(backX,backY)] = 0
file = open('zvals','wb')
pickle.dump(zvals,file)
file.close()

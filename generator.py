import pickle
import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

rimOffset = 0
backXMax = 8 #width of 16, origin is at center of bottom of backboard, +x is to the right
backYMax = 9-rimOffset #measured from bottom of center of rim, +y is vertically up
backYMin = rimOffset
backLengthStep = 1

file = open('angles','rb')
output = pickle.load(file)
file.close()
fig = plt.figure()
ax = plt.axes(projection='3d')
#find parabola on yz plane
inputs = []
derivatives = []
#finds the derivatives pts for the function representating a cross section
for backY in np.arange(backYMin,backYMax+backLengthStep,backLengthStep):
    inputs.append(backY)
    derivatives.append(np.tan(output[(0,backY)][1]))
    print(derivatives[-1])
inputvals = np.array([inputs]).T
derivativevals = np.array([derivatives]).T
intercepts = np.ones(inputvals.shape)
A = np.hstack((inputvals,intercepts))
#least squares to find derivative function
ml,bl = np.linalg.lstsq(A,derivativevals,rcond=None)[0]
a,b,c = ml/2,bl,0
vals = []
yref = [a,b,c]
# gets the parabola pts based on the derivative function
for input in inputvals:
    out = a*input**2+b*input+c
    vals.append(out)
xvals = np.zeros(inputvals.shape)
#plots the backboard visualization
ax.plot3D(xvals.flatten(),np.array(vals).flatten(),inputvals.flatten(),'red')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim3d(-10,10)
ax.set_ylim3d(-10,10)
ax.set_zlim3d(-10,10)
zvals = {}
allx = []
ally = []
allz = []
for backY in np.arange(backYMin,backYMax+backLengthStep,backLengthStep):
    inputs = []
    derivatives = []
    for backX in np.arange(0,backXMax+backLengthStep,backLengthStep):
        inputs.append(backX)
        derivatives.append(np.tan(output[(backX,backY)][0]))
    inputvals = np.array([inputs]).T
    derivativevals = np.array([derivatives]).T
    m = np.linalg.lstsq(inputvals,derivativevals,rcond=None)[0]
    a = m/2
    vals = []
    for input in inputvals:
        zvalue = a*input**2+(yref[0]*backY**2+yref[1]*backY)
        zvals[(input[0],backY)] = zvalue[0][0]
        vals.append(zvalue)
        ally.append(zvalue[0][0])
    yvals = np.array([backY]*len(vals))
    ax.plot3D(inputvals.flatten(),np.array(vals).flatten(),yvals.flatten(),'blue')
    allx += inputs
    allz += [backY]*len(vals)
allx += [-1*val for val in allx]
ally += ally
allz += allz
file = open('zvals','wb')
pickle.dump(zvals,file)
file.close()
#generates point cloud for backboard
file = open('boardpoints.xyz','w')
file.truncate(0)
for i in range(len(allx)):
    file.write(str(allx[i])+' '+str(ally[i])+' '+str(allz[i])+'\n')
file.close()
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import pickle
#Backboard: 16" width, 12" height
#Usable backboard: 16" width, 8" height
#Rim: 9.06" OD probably, set target of 8.75" ID
#Ball diameter: 6.30", radius: 3.15"
rimOffset = 0
backXMax = 8 #width of 16, origin is at center of bottom of backboard, +x is to the right
backYMax = 9-rimOffset #measured from bottom of center of rim, +y is vertically up
backYMin = rimOffset
rimRad = 8.5/2
rimCenterY = 2.25+rimRad
ballRad = 2.5
rimHeight = 71
#Court bounding box for where the bal is shot from will be, origin is at point on the floor which the center of the backboad is directly above.
# +Y is the direction away from the backboard, +x is the direction to the right of the backboard when looking at it from the front
courtYMin = 48
courtYMax = 60
courtXMax = 36    #X boundary is +- from the y axis
launchZMin = 48
launchZmax = 72

g = -1*386.0886 # in ft/s^2
#reasonable shot limits
minAngle = np.pi/6
maxAngle = 1.3
maxEndVel = 12*12 #max reasonable shot velocity in/s
minXPlaneAngle = 0
maxXPlaneAngle = np.pi/4
minYPlaneAngle = -1*np.pi/4
maxYPlaneAngle = np.pi/4
#Increment vars:
backLengthStep = 1
courtLocationStep = 6
shotAngleStep = 5*np.pi/180
planeAngleStep = 0.03
#Backboard z vals
file = open('zvals','rb')
zvals = pickle.load(file)
file.close()
#Algorithm steps:
#Loop through all locations on Backboard
#For each location on the backboard, try all possible shots within proper velocity range within the court boundaries that hit the backboard and maybe meet some criteria(not line drive)
#For each shot(location+direction,angle,velocity), find all possible angles of the backboard segment that will produce a shot, should form an ellipse from x_angle,y_angle
#Collect all of the angle ellipses from all possible shots and find the angle the produces the most intersections

def checkAngle(bx,by,cx,cy,vel,theta,xAngle,yAngle):
    # print((xAngle,yAngle))
    #backboard point in court axes
    a = np.arctan2(cy-zvals[(bx,by)],bx-cx)  # x angle between the court point and the backboard point in court coordinates
    if(xAngle<=-1*a):   #physically doesn't work since ball would have to go through 3D backboard curve to reach point
        # print("incompatible x angle")
        return False
    dist = np.sqrt((cy-zvals[(bx,by)])**2+(bx-cx)**2)
    vl = vel*np.cos(theta) # velocity component in direction shot
    vzi = vel*np.sin(theta) # z velocity component
    time = dist/vl
    vzf = vzi + g*time
    b = np.arctan(vzf/vl) # vertical angle(y angle for backboard) of the ball velocity when it hits the backboard
    if((np.pi/2-yAngle)<=-1*b):   #physically doesn't work since ball would have to go through 3D backboard curve to reach point
        # print("incompatible y angle")
        return False
    b1 = 2*yAngle-b
    a1 = 2*xAngle-a
    vl = vel*np.cos(b1)
    vzi = vel*np.sin(b1)
    calc = vzi**2+2*g*(-1*by)
    time = (-1*vzi+np.sqrt(calc))/g
    # timevals = np.linspace(0,time,100)
    finalX = vl*np.cos(a1)*time+bx
    finalY = vl*np.sin(a1)*time+ballRad+zvals[(bx,by)] #need center of ball and not the end of the ball that bounces off wall, also accounts for backboard 3d shape
    # print("Final x: "+str(finalX))
    # print("Final y: "+str(finalY))
    centerDist = np.sqrt(finalX**2+(finalY-rimCenterY)**2) #distance from center of the ball to the center of the rim when the center of ball is on the rim plane
    if(centerDist<=(rimRad-ballRad)):
        # for i in range(100):
        #     if(np.sqrt(xvals[i]**2+(yvals[i]-rimCenterY)**2)<rimRad):
        #         tintersect = np.sqrt((xvals[i]-bx)**2+yvals[ixxxxx]**2)/vl
        #         if(by+vzi*tintersect+.5*g*tintersect**2>ballRad):
        #             return True
        #         else:
        #             return False
        return True
    else:
        return False
def findPlaneAngles(bx,by,cx,cy,cz,vel,theta):
    validAngles = set()
    #loops through angle range by planeAngleStep increments and adds all valid angles that result in the shot going into the hoop to a set
    for xAngleCur in np.arange(minXPlaneAngle,maxXPlaneAngle,planeAngleStep):
        for yAngleCur in np.arange(minYPlaneAngle,maxYPlaneAngle,planeAngleStep):
            if(checkAngle(bx,by,cx,cy,vel,theta,xAngleCur,yAngleCur)):
                validAngles.add((xAngleCur,yAngleCur))
    # xvals = [angles[0] for angles in validAngles]
    # yvals = [angles[1] for angles in validAngles]
    # plt.scatter(xvals,yvals)
    # plt.ylim([np.pi*-1/3,np.pi/3])
    # plt.xlim([np.pi*-1/3,np.pi/3])
    # plt.xlabel("X angle")
    # plt.ylabel("Y angle")
    # plt.show()
    return validAngles
def findValidShots(bx,by,cx,cy,cz):
    validShots = []
    #loops through the reasonable shot angle range by shotAngleStep increments
    #adds the shot velocity that results in hitting the target for each angle
    dist = np.sqrt((cy-zvals[(bx,by)])**2+(bx-cx)**2)
    deltaz = by+rimHeight-cz
    for theta in np.arange(minAngle,maxAngle,shotAngleStep):
        val = deltaz-dist*np.tan(theta)
        if(val<0):
            vi = np.sqrt(g*dist**2/(2*(val)*(np.cos(theta))**2))
            vil = vi*np.cos(theta)
            vzf = vi*np.sin(theta)+g*dist/vil
            # print(vi,theta,vzf)
            if(vzf/vil <= -1*.4 and np.sqrt(vzf**2+vil**2)<maxEndVel):
                validShots.append((bx,by,cx,cy,cz,vi,theta))
    return validShots
def findBestAngle(bx,by):
    validShots = []
    #Gets a list of all valid shots from all over the court bounding box that can hit the target spot
    for xloc in np.arange(-1*courtXMax,courtXMax,courtLocationStep):
        for yloc in np.arange(courtYMin,courtYMax,courtLocationStep):
            for zloc in np.arange(launchZMin,launchZmax,courtLocationStep):
                validShots += findValidShots(bx,by,xloc,yloc,zloc)
    # print("all valid shots found")
    print("Number of valid shots found: "+str(len(validShots)))
    count = 1
    angleSetList = []
    #generates a list of sets of angles that work for each shot
    for shot in validShots:
        angleSetList.append(findPlaneAngles(*shot))
        print("Shot "+str(count)+" calculated")
        count+=1
    frequencyDict = {}  #dictionary that has frequency to list of angle tuples that have that frequency
    #loops through all angle pairs in the defined range by the planeAngleStep increment
    #counts the number of sets from above that the pair fits under and sorts them into buckets
    for xAngleCur in np.arange(minXPlaneAngle,maxXPlaneAngle,planeAngleStep):
        for yAngleCur in np.arange(minYPlaneAngle,maxYPlaneAngle,planeAngleStep):
            count = 0
            anglePair = (xAngleCur,yAngleCur)
            for angleSet in angleSetList:
                if(anglePair in angleSet):
                    count +=1
            if(count in frequencyDict):
                frequencyDict[count].append(anglePair)
            else:
                frequencyDict[count] = []
                frequencyDict[count].append(anglePair)
    # print("angle frequencies found")
    sortedFrequencies = sorted(frequencyDict.keys())
    highestFrequencyAngles = frequencyDict[sortedFrequencies[-1]]   #gets the bucket of angle pairs with the highest frequency
    # print(highestFrequencyAngles)
    xvals = [angles[0] for angles in highestFrequencyAngles]
    yvals = [angles[1] for angles in highestFrequencyAngles]
    # print(len(xvals))
    # print(len(yvals))
    # plt.scatter(xvals,yvals)
    # plt.ylim([np.pi*-1/3,np.pi/3])
    # plt.xlim([np.pi*-1/3,np.pi/3])
    # plt.xlabel("X angle")
    # plt.ylabel("Y angle")
    # plt.show()
    return((sum(xvals)/len(xvals),sum(yvals)/len(yvals)))   #assumes optimal angle as average values of all angle pairs in the highest frequency bucket
def findAllBestAngles():
    positionToBestAngle = {}
    count = 1
    total = int((backXMax/backLengthStep+1)*((backYMax-backYMin)/backLengthStep+1))
    print("Total number of backboard points: "+str(total))
    for backX in np.arange(0,backXMax+backLengthStep,backLengthStep):
        for backY in np.arange(backYMin,backYMax+backLengthStep,backLengthStep):
            positionToBestAngle[(backX,backY)] = findBestAngle(backX,backY)
            print("Angle "+str(count)+" of "+str(total)+" found.")
            print((backX,backY))
            print(positionToBestAngle[(backX,backY)])
            count+=1
    return positionToBestAngle

#Code for visualization/debugging
def drawHoop():
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim3d(-50,50)
    ax.set_ylim3d(0,100)
    ax.set_zlim3d(0,100)
    rimtheta = np.linspace(0,2*np.pi,100)
    rimx = rimRad*np.cos(rimtheta)
    rimy = rimRad*np.sin(rimtheta)+rimCenterY
    rimz = rimHeight
    correctx = (rimRad-ballRad)*np.cos(rimtheta)
    correcty = (rimRad-ballRad)*np.sin(rimtheta)+rimCenterY
    ax.plot3D(rimx,rimy,rimz,'red')
    ax.plot3D(correctx,correcty,rimz,'green')
    ax.plot3D(np.linspace(backXMax,backXMax,100),np.zeros(100),np.linspace(backYMin,backYMax,100)+rimHeight,'red')
    ax.plot3D(np.linspace(-1*backXMax,-1*backXMax,100),np.zeros(100),np.linspace(backYMin,backYMax,100)+rimHeight,'red')
    ax.plot3D(np.linspace(-1*backXMax,backXMax,100),np.zeros(100),np.linspace(backYMin,backYMin,100)+rimHeight,'red')
    ax.plot3D(np.linspace(-1*backXMax,backXMax,100),np.zeros(100),np.linspace(backYMax,backYMax,100)+rimHeight,'red')
if(len(sys.argv)<2 or sys.argv[1]=='1'):
    start = datetime.now()
    output = findAllBestAngles()
    file = open('angles','wb')
    pickle.dump(output,file)
    file.close()
    print("Runtime: "+str(datetime.now()-start))
elif(sys.argv[1]=='2'):
    shotsToSee = []
    #Gets a list of all valid shots from all over the court bounding box that can hit the target spot
    probeX = 0
    probeY = int((backYMax+backYMin)/2)
    if(len(sys.argv)>2):
        if(sys.argv[2] == '1'):
            probeX = backXMax
            probeY = backYMax
        else:
            probeX = backXMax
            probeY = backYMin
    for xloc in np.arange(-1*courtXMax,courtXMax,courtLocationStep):
        for yloc in np.arange(courtYMin,courtYMax,courtLocationStep):
            for zloc in np.arange(launchZMin,launchZmax,courtLocationStep):
                shotsToSee += findValidShots(probeX,probeY,xloc,yloc,zloc)
    print(len(shotsToSee))
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    drawHoop()
    file = open('anglesbackup','rb')
    anglesref = pickle.load(file)
    file.close()
    pointAngle = anglesref[(probeX,probeY)]
    # pointAngle = findBestAngle(probeX,probeY)
    print(pointAngle)
    print(len(shotsToSee))
    for bx,by,cx,cy,cz,vel,theta in shotsToSee:
        a = np.arctan2(cy-zvals[(bx,by)],bx-cx)
        dist = np.sqrt((cy-zvals[(bx,by)])**2+(bx-cx)**2)
        vl = vel*np.cos(theta) # velocity component in direction shot
        vzi = vel*np.sin(theta) # z velocity component
        time = dist/vl
        vzf = vzi + g*time
        b = np.arctan(vzf/vl)
        timevals = np.linspace(0,time,100)
        zcoords = cz + vzi*timevals+.5*g*np.power(timevals,2)
        xcoords = cx+vl*np.cos(a)*timevals
        ycoords = cy-vl*np.sin(a)*timevals
        ax.plot3D(xcoords,ycoords,zcoords,'blue')
        b1 = 2*pointAngle[1]-b
        a1 = 2*pointAngle[0]-a
        vl = vel*np.cos(b1)
        vzi = vel*np.sin(b1)
        calc = vzi**2+2*g*(-1*by)
        time = (-1*vzi+np.sqrt(calc))/g
        timevals = np.linspace(0,time,100)
        zcoords = by + rimHeight + vzi*timevals+.5*g*np.power(timevals,2)
        xcoords = vl*np.cos(a1)*timevals+bx
        ycoords = vl*np.sin(a1)*timevals+ballRad+zvals[(bx,by)]
        ax.plot3D(xcoords,ycoords,zcoords,'pink')
    plt.show()

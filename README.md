# 3DBackboard

Scripts to generate a point cloud representing a curved, three-dimensional mini basketball hoop backboard that is designed to direct the ball into the rim for as many reasonable shots as possible. 

Inspired by a project featured on the StuffMadeHere youtube channel on 04/17/2020.

Scripts:
* boardfinder.py - Finds the x,y angles at each point on the backboard that maximizes the number of realistic shots made. Also had debugging feature to visualize shots and rebounds for probed locations on the backboard.
* generator.py - Uses x,y angles and least squares fit to create parabola cross sections of the backboard surface. Extrapolates points from the fit and exports point cloud(.xyz file) to later convert into a mesh with MeshLab. Also saves 3D representation of backboard points for reference in future iterations of angle finding.
* basegenerator.py - Resets the 3D reference backboard used in angle finding to a flat surface in order to start the first iteration.

Multiple iterations of boardfinder.py + generator.py need to be run since when the angles are converted into a 3D shape the rebound trajectory of the ball is affected.

Notes:
* The code was separated into multiple scripts to make debugging easier and can be combined if needed
* The ball pivot algorithm was used in MeshLab for making the mesh from the point cloud
* The mesh was exported as an STL and imported into Fusion360 to create the final backboard design based on the mesh
* I decided to 3D print the backboard so it was split into six pieces to fit my printer's bed and assembled with alignment pins and superglue
* Issues with shots on the sides and top corners bouncing off the rim sometimes. Might be due to the shots I chose to optimize for being different from the shots that actually occur in real life.

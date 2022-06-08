
from src.MovementScheme import Movements 

def appendDanceMovement():

    '''
    #demo 1 
    dance_scheme = Movements('stand','SpeedDisable','AttitudeDisable','LegsEnable','ActuatorDisable')
    dance_scheme.setExitstate('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.065]])   # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.065]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.065]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.065]])   # leg4

    dance_scheme.setInterpolationNumber(50)
    dance_scheme.setLegsSequence(dance_all_legs,'Forever',5)

    MovementLib.append(dance_scheme)      # append dance
    '''

    #demo 2 
    dance_scheme = Movements('push-up','SpeedEnable','AttitudeDisable','LegsEnable','ActuatorDisable')
    dance_scheme.setExitstate('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.04],[ 0.06,-0.05,-0.07],[ 0.06,-0.05,-0.04],[ 0.06,-0.05,-0.04],[ 0.06,-0.05,-0.04]])   # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.04],[ 0.06, 0.05,-0.07],[ 0.06, 0.05,-0.04],[ 0.06, 0.05,-0.04],[ 0.06, 0.05,-0.04]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.04],[-0.06,-0.05,-0.07],[-0.06,-0.05,-0.04],[-0.06,-0.05,-0.04],[-0.06,-0.05,-0.04]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.04],[-0.06, 0.05,-0.07],[-0.06, 0.05,-0.04],[-0.06, 0.05,-0.04],[-0.06, 0.05,-0.04]])   # leg4

    dance_speed = [[0,0,0],[0,0,0],[0,0,0],[0.25,0,0,0],[0.25,0,0,0]]    # speed_, speed_y, no_use

    dance_attitude = [[0,0,0],[10,0,0],[0,0,0]]         # roll, pitch, yaw rate
    
    dance_scheme.setInterpolationNumber(70)
    dance_scheme.setLegsSequence(dance_all_legs,'Forever',1)
    dance_scheme.setSpeedSequence(dance_speed,'Forever',1)
    dance_scheme.setAttitudeSequence(dance_attitude,'Forever',1)
        
    MovementLib.append(dance_scheme)      # append dance
    


MovementLib = []
appendDanceMovement()                           


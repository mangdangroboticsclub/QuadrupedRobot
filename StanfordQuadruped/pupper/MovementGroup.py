
from src.MovementScheme import Movements 

def appendDanceMovement():

    #demo 1 
    dance_scheme = Movements('stand','AttitudeDisable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.065]])   # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.065]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.065]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.065]])   # leg4

    dance_scheme.setLegsSubphase(50)
    dance_scheme.setLegsPhase(dance_all_legs,'Single',1)
    
    MovementLib.append(dance_scheme)      # append dance

    #demo 2 
    dance_scheme = Movements('push-up','AttitudeDisable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.04],[ 0.06,-0.05,-0.07]])   # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.04],[ 0.06, 0.05,-0.07]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.04],[-0.06,-0.05,-0.07]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.04],[-0.06, 0.05,-0.07]])   # leg4

    dance_scheme.setLegsSubphase(50)
    dance_scheme.setLegsPhase(dance_all_legs,'Multiple',2)
    
    MovementLib.append(dance_scheme)      # append dance
    
    #demo 3 
    dance_scheme = Movements('push-up 2','AttitudeDisable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.015]])   # leg1
    dance_all_legs.append([[ 0.06, 0.03,-0.04],[ 0.06, 0.03,-0.07]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.04],[-0.06,-0.05,-0.07]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.04],[-0.06, 0.05,-0.05]])   # leg4

    dance_scheme.setLegsSubphase(50)
    dance_scheme.setLegsPhase(dance_all_legs,'Multiple',3)
    
    MovementLib.append(dance_scheme)      # append dance

    #demo 4 
    dance_scheme = Movements('leg dance','AttitudeDisable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[0.06,-0.03,-0.065],[0.06,-0.04,-0.06],[0.06,-0.05,-0.04],[0.06,-0.06,-0.06],[0.06,-0.07,-0.065],[0.06,-0.06,-0.06],[0.06,-0.05,-0.04],[0.06,-0.04,-0.06]])   # leg1
    dance_all_legs.append([[ 0.06, 0.03,-0.07]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.07]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.07]])   # leg4

    dance_scheme.setLegsSubphase(20)
    dance_scheme.setLegsPhase(dance_all_legs,'Forever',1)
    
    MovementLib.append(dance_scheme)      # append dance

    #demo 5
    dance_scheme = Movements('swing body','AttitudeEnable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.055]])   # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.055]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.055]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.055]])   # leg4

    dance_scheme.setLegsSubphase(50)
    dance_scheme.setLegsPhase(dance_all_legs,'Single',1)


    dance_attitude = []
    dance_attitude.append([0])              # roll
    dance_attitude.append([0,10,10])   # pitch
    dance_attitude.append([0])              # yaw rate

    dance_scheme.setAttitudesSubphase(50)
    dance_scheme.setAttitudesPhase(dance_attitude,'Multiple',3)
    
    MovementLib.append(dance_scheme)      # append dance

    #demo 6
    dance_scheme = Movements('dig soil','AttitudeDisable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.05]])     # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.04]])     # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.05],[-0.09,-0.05,-0.05],[-0.06,-0.05,-0.03],[-0.06,-0.05,-0.03]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.05]])     # leg4

    dance_scheme.setLegsSubphase(10)

    dance_scheme.setLegsPhase(dance_all_legs,'Multiple',5)
    
    MovementLib.append(dance_scheme)      # append dance  

    #demo 7
    dance_scheme = Movements('piss','AttitudeDisable','ActuatorEnable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.08]])    # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.04]])    # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.015]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.06]])    # leg4

    dance_scheme.setLegsSubphase(80)
    dance_scheme.setLegsPhase(dance_all_legs,'Forever',1)

    all_actuators = []
    all_actuators.append([0])                         # actuator1
    all_actuators.append([0])                         # actuator2
    all_actuators.append([0,90])     # actuator3

    dance_scheme.setActuatorsSubphase(40)
    dance_scheme.setActuatorsPhase(all_actuators,'Single',1)
    
    MovementLib.append(dance_scheme)      # append dance
    
    #demo 8
    dance_scheme = Movements('stand','AttitudeDisable','ActuatorDisable')
    dance_scheme.setMovementExitState('Stand')

    dance_all_legs = []
    dance_all_legs.append([[ 0.06,-0.05,-0.055]])   # leg1
    dance_all_legs.append([[ 0.06, 0.05,-0.055]])   # leg2
    dance_all_legs.append([[-0.06,-0.05,-0.055]])   # leg3
    dance_all_legs.append([[-0.06, 0.05,-0.055]])   # leg4

    dance_scheme.setLegsSubphase(50)
    dance_scheme.setLegsPhase(dance_all_legs,'Single',1)
    
    MovementLib.append(dance_scheme)      # append dance


MovementLib = []
appendDanceMovement()                           


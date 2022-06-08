from ActuatorControl import ActuatorControl

LocationStanding = [[ 0.06,0.06,-0.06,-0.06],[-0.05, 0.05,-0.05,0.05],[ -0.07,-0.07,-0.07,-0.07]]
DeltLocationMax = 0.001

AttitudeMinMax = [[-20,20],[-20,20],[-100,100]]



class SequenceInterpolation:

    def __init__(self,name,dimension):

        self.Name = name
        self.Dimension = dimension
        self.InterpolationNumber = 1

        self.ExecuteTick = 0
        self.SequenceExecuteCounter = 0
        self.PhaseNumberMax = 1
        self.SequencePoint = [[0,0,0]]

        # interpolation point data 
        self.PointPhaseStart = 0
        self.PointPhaseStop = 1
        self.TnterpolationDelt = [0,0,0]
        self.PointNow = [0,0,0]                 
        self.PointPrevious = [0,0,0]

    def setCycleType(self,cycle_type,cycle_index):

        if cycle_type == 'Forever':
            self.SequenceExecuteCounter = 9999
        elif cycle_type == 'Multiple':
            self.SequenceExecuteCounter = cycle_index
        else:
            self.SequenceExecuteCounter = 1  

        return True
        
    def setInterpolationNumber(self,interpolation_number):


        self.InterpolationNumber = interpolation_number
        return True
        
    def setSequencePoint(self,sequence):

        self.SequencePoint = sequence
        self.PhaseNumberMax = len(sequence)
        

        # init now and pre point phase
        for xyz in range(self.Dimension):
        
            self.PointNow[xyz] = sequence[0][xyz] 
            self.PointPrevious[xyz] = sequence[0][xyz] 
            
        # init start point phase
        self.PointPhaseStart  = 0
        # init stop point phase
        self.PointPhaseStop  = self.PointPhaseStart + 1
        if self.PointPhaseStop >= len(sequence):
            self.PointPhaseStop = self.PointPhaseStart
            

        return True

    def updatePointPhase(self):
    

        # update start point phase
        self.PointPhaseStart  = self.PointPhaseStart + 1
        if self.PointPhaseStart >= self.PhaseNumberMax:
            if self.SequenceExecuteCounter >0:
                self.PointPhaseStart = 0
            else:
                self.SequenceExecuteCounter = 0
                self.PointPhaseStart = self.PointPhaseStart - 1

        # update stop point phase
        self.PointPhaseStop  = self.PointPhaseStart + 1
        if self.PointPhaseStop >= self.PhaseNumberMax:
            self.SequenceExecuteCounter = self.SequenceExecuteCounter - 1
            if self.SequenceExecuteCounter >0:
                self.PointPhaseStop = 0
            else:
                self.SequenceExecuteCounter = 0
                self.PointPhaseStop = self.PointPhaseStop - 1
            self.PointPhaseStop = 0
            
        return True

    def updateInterpolationDelt(self):

        #get start and stop point
        point_start  = self.SequencePoint[self.PointPhaseStart]
        point_stop  = self.SequencePoint[self.PointPhaseStop]
        
                
        for xyz in range(self.Dimension):
                
            diff =   point_stop[xyz] - point_start[xyz]  
            self.TnterpolationDelt[xyz] = - diff/self.InterpolationNumber       
                
        return True

    def getNewPoint(self):

        #update movement tick
        self.ExecuteTick = self.ExecuteTick + 1
        if self.ExecuteTick >= self.InterpolationNumber:
             self.ExecuteTick = 0
             self.updatePointPhase()
             self.updateInterpolationDelt()
        self.PointNow[0] = self.PointPrevious[0] + self.TnterpolationDelt[0]
        self.PointNow[1] = self.PointPrevious[1] + self.TnterpolationDelt[1]
        self.PointNow[2] = self.PointPrevious[2] + self.TnterpolationDelt[2]
        self.PointPrevious = self.PointNow

        return self.PointNow


class Movements:
    
    def __init__(self,name,speed_enable,attitude_enable,legs_enable,actuator_enable):

        self.MovementName =  name

        self.SpeedEnable = speed_enable
        self.AttitudeEnable = attitude_enable
        self.LegsEnable = legs_enable
        self.ActuatorEnable = actuator_enable
        self.ExitToStand = True

        self.SpeedMovements = SequenceInterpolation('speed',2)
        self.AttitudeMovements = SequenceInterpolation('attitude',3)
        self.LegsMovements = []
        self.LegsMovements.append(SequenceInterpolation('leg1',3))
        self.LegsMovements.append(SequenceInterpolation('leg2',3))
        self.LegsMovements.append(SequenceInterpolation('leg3',3))
        self.LegsMovements.append(SequenceInterpolation('leg4',3))
        self.ActuatorsMovements = SequenceInterpolation('actuators',1)

        # init state value
        self.SpeedInit = [0,0,0]          # x, y speed
        self.AttitudeInit = [0,0,0]     # roll pitch yaw rate
        self.LegsLocationInit = [[0,0,0,0],[0,0,0,0],[0,0,0,0]] # x,y,z for 4 legs
        self.ActuatorsAngleInit = [0,0,0]    # angle for 3 actuators
        # output
        self.SpeedOutput = [0,0,0]          # x, y speed
        self.AttitudeOutput = [0,0,0]     # roll pitch yaw rate
        self.LegsLocationOutput = [[0,0,0,0],[0,0,0,0],[0,0,0,0]] # x,y,z for 4 legs
        self.ActuatorsAngleOutput = [0,0,0]    # angle for 3 actuators

    def setInterpolationNumber(self,number):
    
        self.ActuatorsMovements.setInterpolationNumber(number) 
        for leg in range(4):
            self.LegsMovements[leg].setInterpolationNumber(number)  
        self.AttitudeMovements.setInterpolationNumber(number)  
        self.SpeedMovements.setInterpolationNumber(number)  
        return True
        
    def setExitstate(self,state):
    
        if state != 'Stand':
            self.ExitToStand = False
        return True
        
    def setSpeedSequence(self,sequence,cycle_type,cycle_index):

        self.SpeedMovements.setSequencePoint(sequence)
        self.SpeedMovements.setCycleType(cycle_type,cycle_index)
        self.SpeedInit = sequence[0]


    def setAttitudeSequence(self,sequence,cycle_type,cycle_index):

        self.AttitudeMovements.setSequencePoint(sequence)
        self.AttitudeMovements.setCycleType(cycle_type,cycle_index)
        self.AttitudeInit = sequence[0]

    def setLegsSequence(self,sequence,cycle_type,cycle_index):

        for leg in range(4):
            self.LegsMovements[leg].setSequencePoint(sequence[leg])
            self.LegsMovements[leg].setCycleType(cycle_type,cycle_index)
            
            # init location
            self.LegsLocationInit[0][leg] = sequence[leg][0][0]
            self.LegsLocationInit[1][leg] = sequence[leg][0][1]
            self.LegsLocationInit[2][leg] = sequence[leg][0][2]
            

    def setActuatorsSequence(self,sequence,cycle_type,cycle_index):

        self.ActuatorsMovements.setSequencePoint(sequence)
        self.ActuatorsMovements.setCycleType(cycle_type,cycle_index)
        self.ActuatorsAngleInit = sequence[0]

    def runMovementSequence(self):

        if self.SpeedEnable == 'SpeedEnable':
            self.SpeedOutput = self.SpeedMovements.getNewPoint()

        if self.AttitudeEnable == 'AttitudeEnable':
            self.AttitudeOutput = self.AttitudeMovements.getNewPoint()

        if self.LegsEnable == 'LegsEnable':
            for leg in range(4):
                leg_loaction = self.LegsMovements[leg].getNewPoint()
                for xyz in range(3):
                    self.LegsLocationOutput[xyz][leg] = leg_loaction[xyz]

        if self.ActuatorEnable == 'ActuatorEnable':
            self.ActuatorsAngleOutput = self.ActuatorsMovements.getNewPoint()


    def getSpeedOutput(self, state = 'Normal'):

        if state == 'Init':
            return self.SpeedInit
        else:
            return self.SpeedOutput

    def getAttitudeOutput(self, state = 'Normal'):

        if state == 'Init':
            return self.AttitudeInit
        else:
            return self.AttitudeOutput

    def getLegsLocationOutput(self, state = 'Normal'):

        if state == 'Init':
            return self.LegsLocationInit
        else:
            return self.LegsLocationOutput

    def getActuatorsAngleOutput(self, state = 'Normal'):

        if state == 'Init':
            return self.ActuatorsAngleInit
        else:
            return self.ActuatorsAngleOutput

    def getMovementName(self):

        return self.MovementName   
    

class MovementScheme:
    
    def __init__(self,movements_lib):

        self.movements_lib = movements_lib
        
        self.movements_now = movements_lib[0]
        self.movements_pre = movements_lib[0]
        self.movement_now_name =  movements_lib[0].getMovementName()
        self.movement_now_number = 0
        
        self.ststus = 'Movement'    # 'Entry' 'Movement' 'Exit'
        self.entry_down = False
        self.exit_down = False
        self.tick = 0

        self.legs_location_pre = LocationStanding
        self.legs_location_now = LocationStanding

        self.attitude_pre = [0,0,0]
        self.attitude_now = [0,0,0]

        self.speed_pre = [0,0,0]
        self.speed_now = [0,0,0]

        self.actuators_pre = [0,0,0]
        self.actuators_now = [0,0,0]

        self.actuator = []
        self.actuator.append(ActuatorControl(1)) 
        self.actuator.append(ActuatorControl(2)) 
        self.actuator.append(ActuatorControl(3)) 

    def updateMovementType(self):

        self.movements_pre = self.movements_lib[self.movement_now_number]
        self.movement_now_number = self.movement_now_number + 1
        if self.movement_now_number>= len(self.movements_lib):
            self.movement_now_number = 0
        self.entry_down = False
        self.exit_down = False
        self.movements_now = self.movements_lib[self.movement_now_number]

        return self.movements_now.getMovementName()

    def resetMovementNumber(self):

        self.movements_pre = self.movements_lib[self.movement_now_number]
        self.movement_now_number = 0
        self.entry_down = False
        self.exit_down = False
        self.movements_now = self.movements_lib[0]

        return True
    
    def updateMovement(self,movement_type):

        # movement state transition
        if movement_type != self.movement_now_name:
             self.ststus = 'Exit'
        elif(self.entry_down):
             self.ststus = 'Movement'
        elif(self.exit_down):
             self.ststus = 'Entry'
        self.movement_now_name = movement_type

        # update system tick
        self.tick = self.tick+ 1
        # movement execute
        if self.ststus == 'Entry':
             location_ready = self.movements_now.getLegsLocationOutput('Init')
             self.legs_location_now,self.entry_down = self.updateMovementGradient(self.legs_location_pre,location_ready) 
             self.legs_location_pre = self.legs_location_now

        if self.ststus == 'Exit':
             if self.movements_pre.ExitToStand == False:
                  self.legs_location_now,self.exit_down = self.updateMovementGradient(self.location_pre,LocationStanding)
                  self.legs_location_pre = self.legs_location_now
             else:
                  self.legs_location_now = self.legs_location_pre
                  self.exit_down = True

        elif self.ststus == 'Movement':
             self.updateMovemenScheme(self.tick)

             self.legs_location_pre = self.legs_location_now 
             self.attitude_pre = self.attitude_now 

        return self.legs_location_now

    def updateMovementGradient(self,location_now,location_target):

        loaction_gradient = location_now
        gradient_done = False
        gradient_done_counter = 0

        #legs gradient
        for xyz_index in range(3):
            for leg_index in range(4):

                diff = location_now[xyz_index][leg_index] - location_target[xyz_index][leg_index]
                if diff > DeltLocationMax:
                    loaction_gradient[xyz_index][leg_index] = location_now[xyz_index][leg_index] - DeltLocationMax
                elif diff < -DeltLocationMax:
                    loaction_gradient[xyz_index][leg_index] = location_now[xyz_index][leg_index] + DeltLocationMax                
                else :
                    loaction_gradient[xyz_index][leg_index] = location_target[xyz_index][leg_index] 
                    gradient_done_counter = gradient_done_counter + 1

        # movement gradient is down 
        if gradient_done_counter == 12:
            gradient_done = True

        return loaction_gradient, gradient_done  

    def updateMovemenScheme(self,tick):

        # run movement
        self.movements_now.runMovementSequence()

        # legs movement
        self.legs_location_now = self.movements_now.getLegsLocationOutput('normal')
        # speed movement
        self.speed_now = self.movements_now.getSpeedOutput('normal')
        # attitude movement
        self.attitude_now = self.movements_now.getAttitudeOutput('normal')
        # attitude movement
        self.actuators_now = self.movements_now.getActuatorsAngleOutput('normal')

        # attitude process
        '''
        for rpy in range(3):

            #limite attitude angle
            if attitude_now[rpy] < AttitudeMinMax[rpy][0]:
                attitude_now[rpy] = AttitudeMinMax[rpy][0]
            elif attitude_now[rpy] > AttitudeMinMax[rpy][1]:
                attitude_now[rpy] = AttitudeMinMax[rpy][1]
        '''
        # speed process

        return  True

    def runMovementScheme(self,transition):

        # update movement
        movement_name = ''
        if transition == True:
            movement_name = self.updateMovementType()

        self.updateMovement(movement_name) 
 
        return True

    def getMovemenSpeed(self):

        speed_now = [0,0,0]
        for xyz in range(3):

            speed_now[xyz] = -self.speed_now[xyz]
        return speed_now

    def getMovemenLegsLocation(self):
        
        return self.legs_location_now 

    def getMovemenAttitude(self):

        attitude_now_rad = [0,0,0] 

        for rpy in range(3):

            #angle to radin
            attitude_now_rad[rpy] = -self.attitude_now[rpy] / 57.3

        return   attitude_now_rad

    def getMovemenActuators(self):

        return self.actuators_now


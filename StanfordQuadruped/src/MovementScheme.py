from ActuatorControl import ActuatorControl

LocationStanding = [[ 0.06,0.06,-0.06,-0.06],[-0.05, 0.05,-0.05,0.05],[ -0.07,-0.07,-0.07,-0.07]]
DeltLocationMax = 0.001

AttitudeMinMax = [[-20,20],[-20,20],[-100,100]]

class Movements:
    
    def __init__(self,name,attitude_enable,actuator_enable):


        self.movement_name =  name
        self.attitude_enable = attitude_enable
        self.actuator_enable = actuator_enable

        # init location
        self.location_init = []
        
        # location at now and pre
        self.legs_now = []
        self.legs_pre = []

        self.actuator_now = []
        self.actuator_pre = []

        self.attitude_now = []
        self.attitude_pre = []


        self.tick = 0
        self.actuator_tick = 0
        self.attitude_tick = 0

        #number of subphase
        self.leg_subphase_length = 1   
        self.actuator_subphase_length = 1
        self.attitude_subphase_length = 1

        #execute type  :Single , Multiple ,Forever
        self.legs_execute_type = 'Forever'   
        self.legs_execute_time = 0        
        self.legs_exit_to_stand = True 
    
        self.actuators_execute_type = 'Single'   
        self.actuatosr_execute_time = 1 

        self.attitude_execute_type = 'Single'   
        self.attitude_execute_time = 1        


        #start and stop phase point
        self.leg_phase_start = [0,0,0,0]     #start of subphase number for 4 legs
        self.leg_phase_stop  = [0,0,0,0]     #stop of subphase number for 4 legs

        self.actuator_phase_start = [0,0,0]     #start of subphase number for 3 actuators
        self.actuator_phase_stop  = [0,0,0]     #stop of subphase number for 3 actuators

        self.attitude_phase_start = [0,0,0]     #start of subphase number for attitude
        self.attitude_phase_stop  = [0,0,0]     #stop of subphase number for attitude

        #movement delt
        self.legs_delt = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]] 
        self.actuators_delt = [0,0,0]
        self.attitudes_delt = [0,0,0]

        #movement phase
        self.attitudes_phase_all = [[0],[0],[0]]
        self.legs_phase_all = []
        self.actuators_phase_all = [[0],[0],[0]]

    def setLegsSubphase(self,delt_t):

        self.leg_subphase_length = delt_t

    def setAttitudesSubphase(self,delt_t):

        self.attitude_subphase_length = delt_t

    def setActuatorsSubphase(self,delt_t):

        self.actuator_subphase_length = delt_t
        
    def setMovementExitState(self,state):

        if state == 'Stand':
            self.exit_to_stand = True
        else:
            self.exit_to_stand = False
    
        return True
    
    def setLegsPhase(self,all_legs,exe_type,time):

        #init all legs movement phase
        self.legs_phase_all = all_legs
        
        self.location_init.append(all_legs[0][0])
        self.location_init.append(all_legs[1][0])
        self.location_init.append(all_legs[2][0])
        self.location_init.append(all_legs[3][0])

        # init execute type and execute time
        if exe_type == 'Single':
            self.legs_execute_type = 'Single' 
            self.legs_execute_time = 1

        if exe_type == 'Multiple':
            self.legs_execute_type = 'Multiple'
            self.legs_execute_time = time

        elif exe_type == 'Forever':
            self.legs_execute_type = 'Forever'

        #init start and stop phase for legs
        for leg_num in range(4):
            # update start point phase
            self.leg_phase_start[leg_num]  = 0
            if self.leg_phase_start[leg_num] >= len(self.legs_phase_all[leg_num]):
                self.leg_phase_start[leg_num] = 0
            # update stop point phase
            self.leg_phase_stop[leg_num]  = self.leg_phase_start[leg_num] + 1
            if self.leg_phase_stop[leg_num] >= len(self.legs_phase_all[leg_num]):
                self.leg_phase_stop[leg_num] = 0
   
        #init movement legs delt
        for leg_num in range(4):
            
            phase_num_start = self.leg_phase_start[leg_num]
            phase_num_stop =  self.leg_phase_stop[leg_num]

            location_start  = self.legs_phase_all[leg_num][phase_num_start]
            location_stop  = self.legs_phase_all[leg_num][phase_num_stop]
            
            for xyz in range(3):
                
                self.legs_delt[leg_num][xyz] = location_stop[xyz] - location_start[xyz]
               
        #init movement location 
        for leg in range(4):
            self.legs_now.append(self.legs_phase_all[leg][0])
            self.legs_pre.append(self.legs_phase_all[leg][0])

        return True

    def setAttitudesPhase(self,all_attitude,exe_type,time):

        #init all attitude movement phase
        self.attitudes_phase_all = all_attitude

        # init execute type and execute time
        if exe_type == 'Single':
            self.attitude_execute_type = 'Single'
            self.attitude_execute_time = 1

        if exe_type == 'Multiple':
            self.attitude_execute_type = 'Multiple'
            self.attitude_execute_time = time

        elif exe_type == 'Forever':
            self.attitude_execute_type = 'Forever'

        #init start and stop phase for attitude
        for attitude_num in range(3):
            # update start point phase
            self.attitude_phase_start[attitude_num]  = 0
            if self.attitude_phase_start[attitude_num] >= len(self.attitudes_phase_all[attitude_num]):
                self.attitude_phase_start[attitude_num] = 0
            # update stop point phase
            self.attitude_phase_stop[attitude_num]  = self.attitude_phase_start[attitude_num] + 1
            if self.attitude_phase_stop[attitude_num] >= len(self.attitudes_phase_all[attitude_num]):
                self.attitude_phase_stop[attitude_num] = 0

        #init movement location 
        self.attitude_now = [all_attitude[0][0],all_attitude[1][0],all_attitude[2][0]]
        self.attitude_pre = self.attitude_now

        return True

    def setActuatorsPhase(self,all_actuators,exe_type,time):

        #init all actuators movement phase
        self.actuators_phase_all = all_actuators

        # init execute type and execute time
        if exe_type == 'Single':
            self.actuators_execute_type = 'Single'
            self.actuators_execute_time = 1
        if exe_type == 'Multiple':
            self.actuators_execute_type = 'Multiple'
            self.actuators_execute_time = time
        elif exe_type == 'Forever':
            self.actuators_execute_type = 'Forever'

        #init start and stop phase for actuators
        for actuator_num in range(3):
            # update start point phase
            self.actuator_phase_start[actuator_num]  = 0
            if self.actuator_phase_start[actuator_num] >= len(self.actuators_phase_all[actuator_num]):
                self.actuator_phase_start[actuator_num] = 0
            # update stop point phase
            self.actuator_phase_stop[actuator_num]  = self.actuator_phase_start[actuator_num] + 1
            if self.actuator_phase_stop[actuator_num] >= len(self.actuators_phase_all[actuator_num]):
                self.actuator_phase_stop[actuator_num] = 0

        self.actuator_now = [all_actuators[0][0],all_actuators[1][0],all_actuators[2][0]]
        self.actuator_pre = self.actuator_now

        return True

    def updateLegPhaseNumber(self):

        for leg_num in range(4):
            # update start point phase
            self.leg_phase_start[leg_num]  = self.leg_phase_start[leg_num] + 1
            if self.leg_phase_start[leg_num] >= len(self.legs_phase_all[leg_num]):
                self.leg_phase_start[leg_num] = 0

            # update stop point phase
            self.leg_phase_stop[leg_num]  = self.leg_phase_start[leg_num] + 1
            if self.leg_phase_stop[leg_num] >= len(self.legs_phase_all[leg_num]):
                self.leg_phase_stop[leg_num] = 0
            
        return True

    def updateActuatorPhaseNumber(self):

        for actuator_num in range(3):
            # update start point phase
            self.actuator_phase_start[actuator_num]  = self.actuator_phase_start[actuator_num] + 1
            if self.actuator_phase_start[actuator_num] >= len(self.actuators_phase_all[actuator_num]):
                self.actuator_phase_start[actuator_num] = 0
            # update stop point phase
            self.actuator_phase_stop[actuator_num]  = self.actuator_phase_start[actuator_num] + 1
            if self.actuator_phase_stop[actuator_num] >= len(self.actuators_phase_all[actuator_num]):

                self.actuator_phase_stop[actuator_num] = 0
        return True

    def updateAttitudePhaseNumber(self):

        for attitude_num in range(3):
            # update start point phase
            self.attitude_phase_start[attitude_num]  = self.attitude_phase_start[attitude_num] + 1
            if self.attitude_phase_start[attitude_num] >= len(self.attitudes_phase_all[attitude_num]):
                self.attitude_phase_start[attitude_num] = 0
            # update stop point phase
            self.attitude_phase_stop[attitude_num]  = self.attitude_phase_start[attitude_num] + 1
            if self.attitude_phase_stop[attitude_num] >= len(self.attitudes_phase_all[attitude_num]):

                self.attitude_phase_stop[attitude_num] = 0
        return True

    def updateLegDelt(self):

        for leg_num in range(4):
            
            phase_num_start = self.leg_phase_start[leg_num]
            phase_num_stop =  self.leg_phase_stop[leg_num]

            location_start  = self.legs_phase_all[leg_num][phase_num_start]
            location_stop  = self.legs_phase_all[leg_num][phase_num_stop]
                
            for xyz in range(3):
                
                self.legs_delt[leg_num][xyz] = location_stop[xyz] - location_start[xyz]            
                
        return True

    def updateActuatorDelt(self):

        for actuator_num in range(3):
            
            phase_num_start = self.actuator_phase_start[actuator_num]
            phase_num_stop =  self.actuator_phase_stop[actuator_num]

            location_start  = self.actuators_phase_all[actuator_num][phase_num_start]
            location_stop  = self.actuators_phase_all[actuator_num][phase_num_stop]

            self.actuators_delt[actuator_num] = location_stop - location_start
                
        return True

    def updateAttitudeDelt(self):

        for attitude_num in range(3):
            
            phase_num_start = self.attitude_phase_start[attitude_num]
            phase_num_stop =  self.attitude_phase_stop[attitude_num]

            location_start  = self.attitudes_phase_all[attitude_num][phase_num_start]
            location_stop  = self.attitudes_phase_all[attitude_num][phase_num_stop]

            self.attitudes_delt[attitude_num] = location_stop - location_start
              
        return True

    def updateSignalLeg(self,tick,leg_num):

        #get start and stop movement phase number
        phase_num_start = self.leg_phase_start[leg_num]
        phase_num_stop =  self.leg_phase_stop[leg_num]

        #insert movement subphase between start phase and stop phase
        location_start = self.legs_pre[leg_num] 
        loaction_execute = []

        for xyz in range(3):
             diff = self.legs_delt[leg_num][xyz]
             delt_insert = diff/self.leg_subphase_length
             loaction_execute.append(location_start[xyz] + delt_insert)

        return loaction_execute

    def updateActuatorSignal(self,tick,actuator_num):

        #get start and stop actuator phase number
        phase_num_start = self.actuator_phase_start[actuator_num]
        phase_num_stop =  self.actuator_phase_stop[actuator_num]

        #insert actuator subphase between start phase and stop phase
        location_start = self.actuator_pre[actuator_num] 
        loaction_execute = []

        diff = - self.actuators_delt[actuator_num]
        delt_insert = diff/self.actuator_subphase_length
        loaction_execute = location_start + delt_insert

        return loaction_execute

    def updateAttitudeSignal(self,tick,attitude_num):

        #get start and stop attitude phase number
        phase_num_start = self.attitude_phase_start[attitude_num]
        phase_num_stop =  self.attitude_phase_stop[attitude_num]

        #insert actuator subphase between start phase and stop phase
        location_start = self.attitude_pre[attitude_num] 
        loaction_execute = []

        diff = - self.attitudes_delt[attitude_num]
        delt_insert = diff/self.attitude_subphase_length
        loaction_execute = location_start + delt_insert

        return loaction_execute

    def updateAllLegs(self,tick):

        leg_location = [0,0,0]
        All_legs_location =[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        
        #update movement tick
        self.tick = self.tick + 1
        if self.tick >= self.leg_subphase_length:
             self.tick = 0
             self.updateLegPhaseNumber()
             self.updateLegDelt()

        #update all legs loaction for movement
        for leg in range(4):
             leg_location = self.updateSignalLeg(self.tick,leg)
             All_legs_location[leg] = leg_location

        self.legs_now = All_legs_location
        self.legs_pre = All_legs_location

    def updateAllActuators(self,tick):

        all_actuator_location = [0,0,0]

        #update movement tick
        self.actuator_tick = self.actuator_tick + 1
        if self.actuator_tick >= self.actuator_subphase_length:
             self.actuator_tick = 0
             self.updateActuatorPhaseNumber()
             self.updateActuatorDelt()

        #update all legs loaction for movement
        for actuator in range(3):
             actuator_location = self.updateActuatorSignal(self.actuator_tick,actuator)
             all_actuator_location[actuator] = actuator_location

        self.actuator_now = all_actuator_location
        self.actuator_pre = all_actuator_location

    def updateAllAttitudes(self,tick):

        all_attitude_location = [0,0,0]

        #update movement tick
        self.attitude_tick = self.attitude_tick + 1
        if self.attitude_tick >= self.attitude_subphase_length:
             self.attitude_tick = 0
             self.updateAttitudePhaseNumber()
             self.updateAttitudeDelt()

        #update all legs loaction for movement
        for attitude in range(3):
             attitude_location = self.updateAttitudeSignal(self.attitude_tick,attitude)
             all_attitude_location[attitude] = attitude_location

        self.attitude_now = all_attitude_location
        self.attitude_pre = all_attitude_location

    def updateLocationTransition(self,location):

        result = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for leg_num in range(4):
            
            phase_num_start = self.leg_phase_start[leg_num]
            phase_num_stop =  self.leg_phase_stop[leg_num]
            for xyz in range(3):
                
                result[xyz][leg_num] = location[leg_num][xyz]
                
        return result
    
    def getLegMovementName(self):

        return self.movement_name   
 
    def getLegLocationNow(self):

        return self.updateLocationTransition(self.legs_now)

    def getActuatorLocationNow(self):

        return self.actuator_now

    def getAttitudeNow(self):

        return self.attitude_now

    def getLegLocationInit(self):

        return self.updateLocationTransition(self.location_init)
    

class MovementScheme:
    
    def __init__(self,movements_lib):

        self.movements_lib = movements_lib
        
        self.movements_now = movements_lib[0]
        self.movements_pre = movements_lib[0]
        self.movement_now_name =  movements_lib[0].getLegMovementName()
        self.movement_now_number = 0
        
        self.ststus = 'Movement'    # 'Entry' 'Movement' 'Exit'
        self.entry_down = False
        self.exit_down = False
        self.tick = 0
        self.location_pre = LocationStanding
        self.location_now = LocationStanding

        self.attitude_pre = [0,0,0]
        self.attitude_now = [0,0,0]

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

        return self.movements_now.getLegMovementName()

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
             location_ready = self.movements_now.getLegLocationInit()
             self.location_now,self.entry_down = self.updateMovementGradient(self.location_pre,location_ready) 
             self.location_pre = self.location_now

        if self.ststus == 'Exit':
             if self.movements_pre.exit_to_stand == False:
                  self.location_now,self.exit_down = self.updateMovementGradient(self.location_pre,LocationStanding)
                  self.location_pre = self.location_now
             else:
                  self.location_now = self.location_pre
                  self.exit_down = True

        elif self.ststus == 'Movement':
             self.location_now,self.attitude_now = self.updateMovemenScheme(self.tick)
             self.updateActuatorScheme(self.tick)

             self.location_pre = self.location_now 
             self.attitude_pre = self.attitude_now 

        return self.location_now

    def updateMovementGradient(self,location_now,location_target):

        loaction_gradient = location_now
        gradient_done = False
        gradient_done_counter = 0

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
        
        self.movements_now.updateAllLegs(tick)  
        location_now = self.movements_now.getLegLocationNow()

        if self.movements_now.attitude_enable == 'AttitudeEnable':
            self.movements_now.updateAllAttitudes(tick)
            attitude_now = self.movements_now.getAttitudeNow()
        else:
            attitude_now = [0,0,0]

        # attitude process
        for rpy in range(3):

            #limite attitude angle
            if attitude_now[rpy] < AttitudeMinMax[rpy][0]:
                attitude_now[rpy] = AttitudeMinMax[rpy][0]
            elif attitude_now[rpy] > AttitudeMinMax[rpy][1]:
                attitude_now[rpy] = AttitudeMinMax[rpy][1]

        return location_now , attitude_now

    def updateActuatorScheme(self,tick):
        
        if self.movements_now.actuator_enable == 'ActuatorEnable':
            self.movements_now.updateAllActuators(tick)
            location_now = self.movements_now.getActuatorLocationNow()

            for actuator_num in range(3):
                self.actuator[actuator_num].updateActuatorAngle(location_now[actuator_num])
      
        return True 

    def runMovementScheme(self,transition):

        # update movement
        movement_name = ''
        if transition == True:
            movement_name = self.updateMovementType()

        self.updateMovement(movement_name) 
 
        return True

    def getMovemenLegsLocation(self):
        
        return self.location_now 

    def getMovemenAttitudeLocation(self):

        attitude_now_rad = [0,0,0] 

        for rpy in range(3):

            #angle to radin
            attitude_now_rad[rpy] = self.attitude_now[rpy] / 57.3

        return   attitude_now_rad



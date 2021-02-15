//
// Define macro
//

//MAX17205 register map
#define DEVICE_NAME_REGISTER  0x21
#define REPSOC_REGISTER       0x06
#define REPCAP_REGISTER       0x05
#define VCELL_REGISTER        0x09
#define CURRNET_REGISTER      0x0A

//soc info resolution value
#define CURRENT_RESOLUTION    0.15625
#define SOC_RESOLUTION        256.0
#define VOLTAGE_RESOLUTION    6553.6

//bus config
#define I2C_BUS_NO             4
#define SLAVE_ADDRESS          0x36

#define DEV_NAME_VALUE         0x5
#define ODV_THRESHOLD          6.5
#define HALT_THRESHOLD         6.0

//IO file node
#define RED_LED_NODE            "/sys/class/gpio/gpio13/value"
#define GREEN_LED_NODE          "/sys/class/gpio/gpio12/value"
#define BUZZER_NODE             "/sys/class/gpio/gpio16/value"
#define Vbat_Servo_1_EN         "/sys/class/gpio/gpio19/value"
#define Vbat_Servo_2_EN         "/sys/class/gpio/gpio26/value"
#define VBAT_ARM_EN             "/sys/class/gpio/gpio20/value"

#define TIMER_PERIOD            35 //s
#define BUFFER_SIZE             100

#define BATTERY_FG_LOG          "/var/log/battery_info_log.txt"
#define DEBUG                   1
#define SIZE_200M               (200*1024*1024)

//UDP port info
#define SERV_PORT               8000

#define USE_CONTROLLER          0  // default 0
#define CONTROLLER_DONE_MSG     "Done"

// struct for current battery info
#include<time.h>
typedef struct {
	time_t  tm ;        // time in s
	float   soc ;       // soc percentage value  [ % ]
	float   currnet ;   // present current       [ mA ]
	float   voltage;    // present voltage       [ V ]
} batt_infor;


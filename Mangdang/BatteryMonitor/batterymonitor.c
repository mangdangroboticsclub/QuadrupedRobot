/*
 * Power monitor daemon to read battery soc / current / voltage
 * when measurement voltage exceed the over discharged threshold (default:6.0v),
 * alarm by red LED and buzzer on
 *
 * fae@mangdang.net
 *
 * Copyright (c) 2020, Mangdang Technology Co., Limited
*/

#include <sys/ioctl.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include "smbus.h"
#include "i2cbusses.h"
#include "batterymonitor.h"

int32_t g_file = -1;   // fd to save i2c bus file node

#if DEBUG
void debug_log(const char* msg)
{
	FILE *fp = NULL;
	fp = fopen(BATTERY_FG_LOG ,"a+");
	if(NULL == fp) {
		fprintf(stderr, "open %s failed.\n",BATTERY_FG_LOG);
	}else{
		fprintf(fp, "%s", msg);
	}
	fclose(fp);
}
#endif

void io_write(const char* path , char val)
{
   int fd = -1;
   fd = open(path, O_WRONLY);
   if(fd < 0){
       fprintf(stderr , "batterymonitor: open %s failed.\n",path);
   }else{
       write(fd, (const void *)(&val), sizeof(val));
   }
}

void get_battery_info(batt_infor* bat_inf)
{
	int reg_val = 0;
	struct tm *local_time;
	FILE *fp = NULL;

	//get soc value
	reg_val = i2c_smbus_read_word_data(g_file, REPSOC_REGISTER);
	bat_inf->soc = reg_val / SOC_RESOLUTION;
	usleep(10*1000);
	//get currnet value
	reg_val = i2c_smbus_read_word_data(g_file, CURRNET_REGISTER);
	bat_inf->currnet = (0xffff - reg_val + 1) * CURRENT_RESOLUTION;
        usleep(10*1000);
	//get valtage value
	reg_val = i2c_smbus_read_word_data(g_file, VCELL_REGISTER);
	bat_inf->voltage = reg_val / VOLTAGE_RESOLUTION ;
        usleep(10*1000);
	//get current time
	bat_inf->tm = time(NULL);

	//print present battery info
	local_time = localtime(&(bat_inf->tm));
	/*
        fprintf(stderr, "battery info: [%d-%02d-%02d %02d:%02d:%02d] " ,                       \
	        (1900+local_time->tm_year), (1+local_time->tm_mon),   local_time->tm_mday,     \
                local_time->tm_hour,        local_time->tm_min ,      local_time->tm_sec);
	fprintf(stderr , " %4.2f%c(soc)  %7.2f(mA)  %3.2f(v)\n" , bat_inf->soc, '%', bat_inf->currnet, bat_inf->voltage);
	*/

#if DEBUG
	//save battery info in log file
	fp = fopen(BATTERY_FG_LOG ,"a+");
	if(NULL == fp) {
		fprintf(stderr, "open %s failed.\n",BATTERY_FG_LOG);
	}
	fprintf(fp, "battery info: [%d-%02d-%02d %02d:%02d:%02d] " ,                                              \
        (1900+local_time->tm_year), (1+local_time->tm_mon),   local_time->tm_mday,     \
            local_time->tm_hour,        local_time->tm_min ,      local_time->tm_sec);
	fprintf(fp , " %4.2f%c(soc)  %7.2f(mA)  %3.2f(v)\n" , bat_inf->soc, '%', bat_inf->currnet, bat_inf->voltage);
	fclose(fp);
#endif
}


int send_message_to_contrller() // disable this function before co-work with controller module
{
	int32_t sock_fd;
	int32_t ret;
	int32_t len ;
	struct timeval timeout;

	sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if(sock_fd < 0){
		fprintf(stderr , "batterymonitor: creat socket failed\n");
		return -1;
	}

	timeout.tv_sec = 6;
	timeout.tv_usec = 0;
	setsockopt(sock_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

	struct sockaddr_in addr_serv;
	memset(&addr_serv, 0, sizeof(struct sockaddr_in));
	addr_serv.sin_family = AF_INET;
	addr_serv.sin_port = htons(SERV_PORT);
	addr_serv.sin_addr.s_addr = htonl(INADDR_ANY);
	len = sizeof(addr_serv);
	if(bind(sock_fd, (struct sockaddr *)&addr_serv, sizeof(addr_serv)) < 0){
		fprintf(stderr , "batterymonitor: bind socket failed.\n");
#if DEBUG
		debug_log("batterymonitor: bind socket failed.\n");
#endif
		return -1;
	}

	char buf[1024] = "FG : Low power state";
	ret = sendto(sock_fd, buf, strlen(buf), 0, (struct sockaddr *)&addr_serv, sizeof(addr_serv));
	if (ret < 0){
		fprintf(stderr , "batterymonitor: send message %s failed.\n", buf);
#if DEBUG
		debug_log("batterymonitor: send message failed.\n");
#endif
		return -1;
	}

	memset(buf, 0, 1024*sizeof(char));
	ret = recvfrom(sock_fd, buf, sizeof(buf), 0, (struct sockaddr *)&addr_serv, (socklen_t *)&len);
	if(ret < 0){
		fprintf(stderr , "batterymonitor: recv message failed , ret = %d\n", ret);
#if DEBUG
                debug_log("batterymonitor: recv message failed\n");
#endif
		return -1;
	}

	if(strcmp(buf, CONTROLLER_DONE_MSG)){
		fprintf(stderr , "batterymonitor: check recv message  failed.\n");
#if DEBUG
		debug_log("batterymonitor: check recv message  failed.\n");
#endif
		return -1;
	}
	return 0;
}

void battery_check(int signal)
{
	batt_infor bat_inf[BUFFER_SIZE];
	float sum = 0  , avg_vol = 8.4;
	int ret = 0 ;

        if(SIGALRM == signal){
		for (int i = 0; i < BUFFER_SIZE; i++)
		{
			get_battery_info(&(bat_inf[i]));
			usleep(150*1000);
			sum +=bat_inf[i].voltage;
		}
		fprintf(stderr, "\n");
		avg_vol = sum / BUFFER_SIZE;

		if(avg_vol < ODV_THRESHOLD) {     /*over dischager, alarm !*/
#if USE_CONTROLLER     // send low power state message to controller module to suspend pupper
		        ret = send_message_to_contrller();
		        if(0 !=  ret){ // switch off servo power anyway
				fprintf(stderr , "batterymonitor: co-work with controller module failed.\n");
#if DEBUG
				debug_log("batterymonitor: co-work with controller module failed.\n");
#endif
			}
#endif
			io_write(RED_LED_NODE, '1');
			io_write(GREEN_LED_NODE, '0');
			io_write(BUZZER_NODE, '1');
			io_write(Vbat_Servo_1_EN, '0');
			io_write(Vbat_Servo_2_EN, '0');
			io_write(VBAT_ARM_EN, '0');
		}else{
			io_write(RED_LED_NODE, '0');
			io_write(GREEN_LED_NODE,'1');
			io_write(BUZZER_NODE, '0');
		}
		if(avg_vol < HALT_THRESHOLD){  /*low Power , Power off pi4*/
			system("halt");
		}
		alarm(TIMER_PERIOD);
#if DEBUG
		debug_log("\n");
#endif
	}
}


int main(int argc, char *argv[])
{
	int reg_value =0, ret;
	char filename[20] = {0};
	unsigned long funcs;
	struct stat sstat;
#if DEBUG
	debug_log("batterymonitor start.\n");
#endif
	//open i2c , get i2c functionality matrix , set slave address
        g_file = open_i2c_dev(I2C_BUS_NO, filename, sizeof(filename), 0);
	if (g_file < 0)
	{
		fprintf(stderr,"batterymonitor: open i2cbus(%d) [%s] failed.\n", I2C_BUS_NO,filename);
		exit(1);
	}else{
		ret = ioctl(g_file, I2C_FUNCS, &funcs);
		fprintf(stdout,"batterymonitor: I2C_FUNCS = 0x%lx\n",funcs);
		ret = set_slave_addr(g_file, SLAVE_ADDRESS,1);
		if(0 != ret){
			fprintf(stdout,"batterymonitor: I2C set slave address (0x%x) failed, ret = %d \n",SLAVE_ADDRESS, ret);
			exit(1);
		}
	}

	// check max17205 chip
	reg_value = i2c_smbus_read_word_data(g_file , DEVICE_NAME_REGISTER);
        if(DEV_NAME_VALUE != (0x00ff & reg_value)){
		fprintf(stderr,"batterymonitor: max17205 not found.\n");
		// alarm for no fual gauge IC
		io_write(RED_LED_NODE, '1');
		io_write(GREEN_LED_NODE,'0');
		io_write(BUZZER_NODE, '0');
		exit(1);
	}else{
		fprintf(stdout,"batterymonitor: max17205 probe successfully.\n");
#if DEBUG
		debug_log(" max17205 probe successfully.\n");
#endif
	}

	// delete log file when almost full charged and log file larged than 200M
	ret = stat(BATTERY_FG_LOG, &sstat);
	if(0 == ret){
		if(sstat.st_size > SIZE_200M){
			reg_value = i2c_smbus_read_word_data(g_file, VCELL_REGISTER);
			if((reg_value / VOLTAGE_RESOLUTION) > 8.0)
				remove(BATTERY_FG_LOG);
		}
	}else{
		fprintf(stderr,"batterymonitor: get %s size failed.\n", BATTERY_FG_LOG);
	}

	// periodic task ,timer 40s
	signal(SIGALRM, battery_check);
	alarm(3);

	// hold on service
	while(1)
	{
		ret++;
		sleep(60);
	}
	exit(0);
}

// #include "RedisClient.h"
#include <simplecat/Master.h>
#include <simplecat/Beckhoff/Beckhoff.h>
#include "utils/Logger.h"
#include <thread>

typedef Eigen::Matrix<double, 1, 1> Vector1d;

Vector1d speed_sensor_counts;
// Vector1d screw_encoder_counts;
Vector1d pressure_sensor_counts;
Vector1d force_sensor_counts;
Vector1d torque_sensor_counts;

// 100 Hz logger
Logging::Logger logger(10000, "datalog.csv");

simplecat::Master master;
simplecat::Beckhoff_EK1100 bh_ek1100;
simplecat::Beckhoff_EL5152 bh_el5152;
simplecat::Beckhoff_EL9510 bh_el9510;
simplecat::Beckhoff_EL3356 bh_el3356_force;
simplecat::Beckhoff_EL3356 bh_el3356_torque;
simplecat::Beckhoff_EL3062 bh_el3062;

#include <signal.h>
bool rundaq = true;
unsigned long long controller_counter = 0;
void sighandler(int sig) {
	master.stop();
}

void control_callback() {
	speed_sensor_counts << bh_el5152.read_value[0];
	pressure_sensor_counts << bh_el3062.read_data_[0];
	force_sensor_counts << bh_el3356_force.read_value;
	torque_sensor_counts << bh_el3356_torque.read_value;
}

int main (int argc, char** argv) {
	master.setCtrlCHandler(sighandler);
	master.addSlave(0, 0, &bh_ek1100);
	master.addSlave(0, 1, &bh_el3062);
	master.addSlave(0, 2, &bh_el5152);
	master.addSlave(0, 3, &bh_el9510);
	master.addSlave(0, 4, &bh_el3356_force);
	master.addSlave(0, 5, &bh_el3356_torque);

	master.setThreadHighPriority();
	master.activate();
	uint control_freq = 1000; // Hz
	
	logger.addVectorToLog(&speed_sensor_counts, "speed");
	logger.addVectorToLog(&pressure_sensor_counts, "pressure");
	logger.addVectorToLog(&force_sensor_counts, "force");
	logger.addVectorToLog(&torque_sensor_counts, "torque");
	logger.start();

	master.run(control_callback, control_freq);

	logger.stop();

	return 0;
}

// #include "RedisClient.h"
#include <simplecat/Master.h>
#include <simplecat/Beckhoff/Beckhoff.h>
#include "utils/Logger.h"
#include "utils/RedisClient.h"
#include <thread>
#include <string>

typedef Eigen::Matrix<double, 1, 1> Vector1d;

Vector1d speed_sensor_counts;
// Vector1d screw_encoder_counts;
Vector1d pressure_sensor_counts;
Vector1d force_sensor_counts;
Vector1d torque_sensor_counts;
Vector1d front_temp_sensor_counts;

// 100 Hz logger
Logging::Logger logger(10000, "datalog.csv");

simplecat::Master master;
simplecat::Beckhoff_EK1100 bh_ek1100;
simplecat::Beckhoff_EL5152 bh_el5152;
simplecat::Beckhoff_EL9510 bh_el9510;
simplecat::Beckhoff_EL3356 bh_el3356_force;
simplecat::Beckhoff_EL3356 bh_el3356_torque;
simplecat::Beckhoff_EL3062 bh_el3062;
simplecat::Beckhoff_EL3202 bh_el3202;

#include <signal.h>
bool rundaq = true;
unsigned long long controller_counter = 0;
void sighandler(int sig) {
	master.stop();
}

/* Redis keys */
const std::string hpu_pressure_key = "utec::read::pressure::hpu";
const std::string drill_pressure_key = "utec::read::pressure::drill";
const std::string screwjack_pressure_key = "utec::read::pressure::screwjack";
const std::string fluid_pressure_key = "utec::read::pressure::fluid";
const std::string screwjack_speed_key = "utec::read::linear_speed::screwjack";
const std::string screwjack_position_key = "utec::read::position::screwjack";
const std::string screwjack_force_key = "utec::read::force::drill";
const std::string drill_speed_key = "utec::read::rotary_speed::drill";
const std::string drill_torque_key = "utec::read::torque::drill";
const std::string front_bearing_temp_key = "utec::read::temperature::front_bearing";
const std::string rear_bearing_temp_key = "utec::read::temperature::rear_bearing";


void control_callback() {
	speed_sensor_counts << bh_el5152.read_value[0];
	pressure_sensor_counts << bh_el3062.read_data_[0];
	force_sensor_counts << bh_el3356_force.read_value;
	torque_sensor_counts << bh_el3356_torque.read_value;
	front_temp_sensor_counts << bh_el3202.read_data_[0];
}

int main (int argc, char** argv) {
	master.setCtrlCHandler(sighandler);
	master.addSlave(0, 0, &bh_ek1100);
	master.addSlave(0, 1, &bh_el3062);
	master.addSlave(0, 2, &bh_el5152);
	master.addSlave(0, 3, &bh_el3202);
	master.addSlave(0, 4, &bh_el9510);
	master.addSlave(0, 5, &bh_el3356_force);
	master.addSlave(0, 6, &bh_el3356_torque);

	master.setThreadHighPriority();
	master.activate();
	uint control_freq = 1000; // Hz

	logger.addVectorToLog(&speed_sensor_counts, "speed");
	logger.addVectorToLog(&pressure_sensor_counts, "pressure");
	logger.addVectorToLog(&force_sensor_counts, "force");
	logger.addVectorToLog(&torque_sensor_counts, "torque");
	logger.addVectorToLog(&front_temp_sensor_counts, "front_temp");
	logger.start();

	master.run(control_callback, control_freq);

	logger.stop();

	return 0;
}

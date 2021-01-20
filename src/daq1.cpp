// #include "RedisClient.h"
#include <simplecat/Master.h>
#include <simplecat/Beckhoff/Beckhoff.h>
#include "utils/Logger.h"
#include "utils/RedisClient.h"
#include <chrono>
#include <thread>
#include <string>
#include <sstream>
#include <iomanip>

typedef Eigen::Matrix<double, 1, 1> Vector1d;

using namespace std::chrono_literals;

const int NO_DATA_VALUE = -9999;

Vector1d drill_speed_sensor_counts(NO_DATA_VALUE);
Vector1d screwjack_position_sensor_counts(NO_DATA_VALUE);
Vector1d screwjack_speed_counts(NO_DATA_VALUE);
Vector1d hpu_pressure_sensor_counts(NO_DATA_VALUE);
Vector1d screwjack_pressure_sensor_counts(NO_DATA_VALUE);
Vector1d drill_pressure_sensor_counts(NO_DATA_VALUE);
Vector1d force_sensor_counts(NO_DATA_VALUE);
Vector1d torque_sensor_counts(NO_DATA_VALUE);
Vector1d front_temp_sensor_counts(NO_DATA_VALUE);
Vector1d rear_temp_sensor_counts(NO_DATA_VALUE);

// 100 Hz logger
Logging::Logger logger(10000);

simplecat::Master master;
simplecat::Beckhoff_EK1100 bh_ek1100;
simplecat::Beckhoff_EL5152 bh_el5152;
simplecat::Beckhoff_EL9510 bh_el9510;
simplecat::Beckhoff_EL3356 bh_el3356_force;
simplecat::Beckhoff_EL3356 bh_el3356_torque;
simplecat::Beckhoff_EL3062 bh_el3062_1;
simplecat::Beckhoff_EL3062 bh_el3062_2;
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

const std::string logger_key = "utec::logging::start";

double getCalibratedRotarySpeed(double raw_counts) {
	//TODO
	return raw_counts;
}

double getCalibratedLinearSpeed(double raw_counts) {
	//TODO
	return raw_counts;
}

double getCalibratedScrewjackPosition(double raw_counts) {
	// TODO
	return raw_counts;
}

double getCalibratedPressure(double raw_counts) {
	//TODO
	return raw_counts;
}

double getCalibratedTemperature(double raw_counts) {
	//TODO
	return raw_counts;
}

double getCalibratedTorque(double raw_counts) {
	return raw_counts*0.1129848; //returns Nm
}

double getCalibratedForce(double raw_counts) {
	return raw_counts*8.89644; //return N
}

void control_callback() {
	drill_speed_sensor_counts << getCalibratedRotarySpeed(bh_el5152.read_value[0]); // channel 1 is drill speed sensor
	screwjack_position_sensor_counts << getCalibratedScrewjackPosition(bh_el5152.read_value[1]); // channel 2 is screwjack encoder
	hpu_pressure_sensor_counts << getCalibratedPressure(bh_el3062_1.read_data_[0]); // 3062_1 channel 1 is hpu pressure
	drill_pressure_sensor_counts << getCalibratedPressure(bh_el3062_1.read_data_[1]); // 3062_1 channel 2 is drill pressure
	screwjack_pressure_sensor_counts << getCalibratedPressure(bh_el3062_2.read_data_[0]); // 3062_2 channel 1 is screwjack pressure
	force_sensor_counts << getCalibratedForce(bh_el3356_force.read_value);
	torque_sensor_counts << getCalibratedTorque(bh_el3356_torque.read_value);
	front_temp_sensor_counts << getCalibratedTemperature(bh_el3202.read_data_[0]); // channel 1 is front bearing temperature sensor
	rear_temp_sensor_counts << getCalibratedTemperature(bh_el3202.read_data_[1]); // channel 2 is rear bearing temperature sensor
}

bool f_should_write_to_redis = false;

std::string return_current_time_and_date()
{
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);

    std::stringstream ss;
    ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d_%X");
    return ss.str();
}

void redis_read_write(RedisClient* client) {
	while(f_should_write_to_redis) {
		// sleep for 10 ms
		std::this_thread::sleep_for(10ms); //NOTE: ms suffix operator is a C++14 feature
		client->pipeset({
			{hpu_pressure_key, std::to_string(hpu_pressure_sensor_counts[0])},
			{drill_pressure_key, std::to_string(drill_pressure_sensor_counts[0])},
			{screwjack_pressure_key, std::to_string(screwjack_pressure_sensor_counts[0])},
			{drill_speed_key, std::to_string(drill_speed_sensor_counts[0])},
			{screwjack_position_key, std::to_string(screwjack_position_sensor_counts[0])},
			{screwjack_speed_key, std::to_string(screwjack_speed_counts[0])},
			{front_bearing_temp_key, std::to_string(front_temp_sensor_counts[0])},
			{rear_bearing_temp_key, std::to_string(rear_temp_sensor_counts[0])},
			{drill_torque_key, std::to_string(torque_sensor_counts[0])},
			{screwjack_force_key, std::to_string(force_sensor_counts[0])}
		},
		2 /*seconds*/);
		try {
			std::string log_val_str = client->get(logger_key);
			if(std::stoi(log_val_str) && !logger._f_is_logging) {
				std::string filename = "log_"+return_current_time_and_date()+".csv";
				logger.newFileStart(filename);
			}
			if(!std::stoi(log_val_str) && logger._f_is_logging) {
				logger.stop();
			}
		} catch (...) {
			// do nothing
		}
	}
}

int main (int argc, char** argv) {
	master.setCtrlCHandler(sighandler);
	master.addSlave(0, 0, &bh_ek1100);
	master.addSlave(0, 1, &bh_el5152);
	master.addSlave(0, 2, &bh_el3202);
	master.addSlave(0, 3, &bh_el3062_1);
	master.addSlave(0, 4, &bh_el3062_2);
	master.addSlave(0, 5, &bh_el9510);
	master.addSlave(0, 6, &bh_el3356_force);
	master.addSlave(0, 7, &bh_el3356_torque);

	master.setThreadHighPriority();
	master.activate();
	uint control_freq = 1000; // Hz

	logger.addVectorToLog(&hpu_pressure_sensor_counts, "hpu_pressure");
	logger.addVectorToLog(&drill_pressure_sensor_counts, "drill_pressure");
	logger.addVectorToLog(&screwjack_pressure_sensor_counts, "screwjack_pressure");
	logger.addVectorToLog(&drill_speed_sensor_counts, "drill_speed");
	logger.addVectorToLog(&screwjack_position_sensor_counts, "screwjack_position");
	logger.addVectorToLog(&screwjack_speed_counts, "screwjack_speed");
	logger.addVectorToLog(&front_temp_sensor_counts, "front_temp");
	logger.addVectorToLog(&rear_temp_sensor_counts, "rear_temp");
	logger.addVectorToLog(&torque_sensor_counts, "torque");
	logger.addVectorToLog(&force_sensor_counts, "force");
	// logger.start(); //Started from UI now

	auto rclient = RedisClient();
	rclient.connect();

	f_should_write_to_redis = true;
	std::thread redis_thread(redis_read_write, &rclient);

	// std::this_thread::sleep_for(60s); //For testing only
	master.run(control_callback, control_freq);

	f_should_write_to_redis = false;
	redis_thread.join();

	if(logger._f_is_logging) {
		logger.stop();
	}

	return 0;
}

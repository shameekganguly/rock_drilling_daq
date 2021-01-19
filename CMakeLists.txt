################Initialize the Cmake Defaults#################

cmake_minimum_required(VERSION 2.8.12)

#Name the project
project(rock_drill_daq)

#Set the build mode to release by default
set(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_FLAGS "-std=c++11 -I/usr/include -I/usr/local/include")

################Project source#################
include_directories(${PROJECT_SOURCE_DIR} ${PROJECT_SOURCE_DIR}/src)
set(COMMON_SOURCE
	#${PROJECT_SOURCE_DIR}/utils/ButterworthFilter.cpp
    ${PROJECT_SOURCE_DIR}/utils/RedisClient.cpp
)

################Initialize the 3rdParty lib#################
### Eigen
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

### Simplecat
set(SIMPLECAT_BASE_DIR ${PROJECT_SOURCE_DIR}/../simplecat)
include(${SIMPLECAT_BASE_DIR}/SimplECAT.cmake)
include_directories(${SIMPLECAT_INCLUDE_DIRS})
# find_library( SIMPLECAT_LIBRARY NAMES simplecat PATHS ${SIMPLECAT_BASE_DIR}/lib/)

### Etherlab
# link_directories(/opt/etherlab/)
# include_directories(/opt/etherlab/include)
# find_library( ETHERCAT_LIBRARY NAMES ethercat PATHS /opt/etherlab/lib/)

### HiRedis
find_library(HIREDIS_LIBRARY hiredis)

### JsonCpp
# if (CMAKE_SYSTEM_NAME MATCHES Darwin)
#   find_library(JSONCPP_LIBRARY jsoncpp)
# elseif (CMAKE_SYSTEM_NAME MATCHES Linux)
#   find_package(PkgConfig REQUIRED)
#   pkg_check_modules(JSONCPP jsoncpp)
#   link_directories(${JSONCPP_LIBRARY_DIRS})
#   set(JSONCPP_LIBRARY ${JSONCPP_LIBRARIES})
# endif ()

set(COMMON_LIBRARIES pthread
    ${SIMPLECAT_LIBRARIES}
    ${HIREDIS_LIBRARY}
)

###############BUILD ALL EXECUTABLES AND LINK LIBRARIES ######################
add_executable(daq1 src/daq1.cpp ${COMMON_SOURCE})
target_link_libraries(daq1 ${COMMON_LIBRARIES})


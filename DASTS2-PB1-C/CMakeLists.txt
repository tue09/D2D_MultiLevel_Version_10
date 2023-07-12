cmake_minimum_required(VERSION 3.20)
project(DASTS2_PB1_C)
include(FetchContent)

if(POLICY CMP0135)
	cmake_policy(SET CMP0135 NEW)
	set(CMAKE_POLICY_DEFAULT_CMP0135 NEW)
endif()

FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz)
message( STATUS "Fetching Thor..." )
FetchContent_MakeAvailable(json)

set(CMAKE_CXX_STANDARD 17)


add_executable(DASTS2_PB1_C test.cpp src/Config.cpp src/solution.cpp src/parameter.cpp)
target_link_libraries(DASTS2_PB1_C PRIVATE nlohmann_json::nlohmann_json)


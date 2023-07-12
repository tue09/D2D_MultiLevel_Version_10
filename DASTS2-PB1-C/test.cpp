#include "nlohmann/json.hpp"
#include <iostream>
#include <fstream>
#include <filesystem>
#include "src/Config.h"
#include "src/parameter.h"
#include "src/solution.h"
#include <vector>
#include <string>

using json = nlohmann::json;


int main(int argc, char **argv)
{    
    Config config;
    std::string configFilePath = "D:\\Users\\ADMIN\\Documents\\0.Study\\Multi_Level\\DASTS2-PB1-C\\Config.json";
    std::ifstream configFile(configFilePath);
    json jsConfig = json::parse(configFile);

    config.droneVelocity = jsConfig["parameter"]["droneVelocity"].get<double>();
    config.staffVelocity = jsConfig["parameter"]["staffVelocity"].get<double>();
    config.numDrone = jsConfig["parameter"]["numDrone"].get<int>();
    config.numStaff = jsConfig["parameter"]["numStaff"].get<int>();
    config.droneLimitFlightTime = jsConfig["parameter"]["droneLimitFlightTime"].get<double>();
    config.sampleLimitWaitingTime = jsConfig["parameter"]["sampleLimitWaitingTime"].get<double>();
    config.use_ejection = jsConfig["parameter"]["use_ejection"].get<bool>();
    config.use_inter = jsConfig["parameter"]["use_inter"].get<bool>();
    config.use_intra = jsConfig["parameter"]["use_intra"].get<bool>();
   
    config.num_level = jsConfig["multiLevel_para"]["num_level"].get<int>();
    config.percent_match = jsConfig["multiLevel_para"]["percent_match"].get<double>();
    config.tabu_max_ite = jsConfig["multiLevel_para"]["tabu_max_ite"].get<int>();

    config.tabu_size = jsConfig["tabu_para"]["tabu_size"].get<int>();
    config.max_ite = jsConfig["tabu_para"]["max_ite"].get<int>();
    config.num_runs = jsConfig["tabu_para"]["num_runs"].get<int>();
    config.terminate_iter = jsConfig["tabu_para"]["terminate_iter"].get<int>();
    config.tabuAlpha1 = jsConfig["tabu_para"]["tabuAlpha1"].get<double>();
    config.tabuAlpha2 = jsConfig["tabu_para"]["tabuAlpha2"].get<double>();
    config.tabuBeta = jsConfig["tabu_para"]["tabuBeta"].get<double>();
    config.epsilon = jsConfig["tabu_para"]["epsilon"].get<double>();

    config.ws = jsConfig["ws"].get<std::string>();;
    config.dataName = jsConfig["dataName"].get<std::string>();
    config.dataPath = jsConfig["dataPath"].get<std::string>();

    std::string path = config.ws + config.dataPath + config.dataName;
    std::cout<<path;
    
    parameter param(config.droneVelocity, config.staffVelocity, config.droneLimitFlightTime, path);

    solution tue;
    tue.droneTripList = {{{3}}, {{1, 2}}};
    tue.staffTripList = {{4, 6}, {5}};
    tue.param = param;
    tue.config = config;
    tue.alpha1 = 1;
    tue.alpha2 = 1;
    std::cout<<std::endl<<"Fitness of tue is: "<<tue.fitness()<<std::endl;
    std::cout<<"is Tue Feasible??: "<<tue.checkFeasible();




    return 0;
}


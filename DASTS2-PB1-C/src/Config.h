#ifndef DASTS2_PB1_C_CONFIG_H
#define DASTS2_PB1_C_CONFIG_H

#include <string>
class Config
{
public:
    std::string ws;
    std::string resultfolder;
    std::string dataPath;
    std::string dataName;


    double droneVelocity;
    double staffVelocity;
    int numDrone;
    int numStaff;
    double droneLimitFlightTime;
    double sampleLimitWaitingTime;


    bool use_ejection;
    bool use_inter;
    bool use_intra;
    int num_level;
    double percent_match;
    int tabu_max_ite;
    int tabu_size;
    int max_ite;
    int num_runs;
    int terminate_iter;
    double tabuAlpha1;
    double tabuAlpha2;
    double tabuBeta;
    double epsilon;

    Config();
};
#endif
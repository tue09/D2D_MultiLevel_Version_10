#ifndef DASTS2_VERSION8_C_CONFIG_H
#define DASTS2_VERSION8_C_CONFIG_H

#include <string>
class Config
{
public:
    std::string ws;
    std::string TaburesultFolder;
    std::string MultiLevelresultFolder;
    std::string dataPath;
    std::string dataName;
    std::string dataType;
    int NumRunPerDataSet;
    bool multiData;

    double droneVelocity;
    double techVelocity;
    int numDrone;
    int numTech;
    double droneLimitationFlightTime;
    double sampleLimitationWaitingTime;


    bool use_ejection;
    bool use_inter;
    bool use_intra;
    int num_level;
    double percent_match;
    int tabu_max_ite;
    int tabu_size;


    int tabuMaxIter;
    int tabuNumRunPerDataSet;
    int tabuNotImproveIter;
    int minTabuDuration;
    int maxTabuDuration;
    double tabuAlpha1;
    double tabuAlpha2;
    double tabuBeta;
    double tabuEpsilon;
    int maxEjectionLevel;

    Config();
};
#endif


#ifndef DASTS2_VERSION8_C_INPUT_H
#define DASTS2_VERSION8_C_INPUT_H

#include <vector>
#include "string"
#include "Config.h"

class Input
{
public:
    std::vector<std::vector<double>> coordinates;
    std::vector<std::vector<double>> distances;
    std::vector<std::vector<double>> droneTimes;
    std::vector<std::vector<double>> techTimes;
    int numCus{};
    std::string dataSet;
    std::vector<bool> cusOnlyServedByTech;

    Input(double droneVelocity, double techVelocity, int limitationFightTime, const std::string &path);

    Input();
};

#endif 

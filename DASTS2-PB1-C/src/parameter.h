
#ifndef DASTS2_PB1_C_PARAMETER_H
#define DASTS2_PB1_C_PARAMETER_H

#include <vector>
#include "string"
#include "Config.h"

class parameter
{
public:
    std::vector<std::vector<double>> coordinates;
    std::vector<std::vector<double>> distance_matrix;
    std::vector<std::vector<double>> droneTime_matrix;
    std::vector<std::vector<double>> staffTime_matrix;
    std::vector<bool> cusServedByStaff;
    std::string data;
    int numCus{};

    parameter(double droneVelocity, double staffVelocity, int limitationFlighTime, const std::string &path);

    parameter();
};

#endif
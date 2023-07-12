#ifndef DASTS2_PB1_C_SOLUTION_H
#define DASTS2_PB1_C_SOLUTION_H

#include "vector"
#include "iostream"

#include "Config.h"
#include "parameter.h"

class solution
{
public:
    Config config;
    parameter param;
    std::vector<std::vector<std::vector<int>>> droneTripList;
    std::vector<std::vector<int>> staffTripList;

    double cz{}, dz{}, alpha1{}, alpha2{};

    solution(Config &config, parameter &param, double alpha1, double alpha2);

    solution();

    double fitness();

    bool checkFeasible();

};

#endif
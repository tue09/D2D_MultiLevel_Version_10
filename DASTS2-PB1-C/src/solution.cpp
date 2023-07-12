#include "solution.h"
#include "nlohmann/json.hpp"

using json = nlohmann::json;

double solution::fitness()
{
    std::vector<double> staffCompleTime(config.numStaff, 0);
    std::vector<double> droneCompleTime(config.numDrone, 0);
    std::vector<double> cusCompleTime(param.numCus + 1, 0);
    std::vector<std::vector<double>> droneTripCompleTime;
    int maxSize = 0;
    for (int  i = 0; i < (int)droneTripList.size(); i++){
        if (maxSize < droneTripList[i].size()){
            maxSize = (int)droneTripList[i].size();
        }
    }
    for (int i = 0; i < config.numDrone; i++)
    {
        std::vector<double> tripTime(maxSize, 0);
        droneTripCompleTime.push_back(tripTime);
    }
    double maxStaffTime = 0, maxDroneTime = 0;

    double temp, temp1;
    cz = 0, dz = 0;
    for (int i = 0; i < (int)staffTripList.size(); i++)
    {
        if (i == (int)staffTripList.size() - 1) {break;}
        if (staffTripList[i].empty()) {continue;}

        temp = param.staffTime_matrix[0][staffTripList[i][0]];
        cusCompleTime[staffTripList[i][0]] = temp;

        for (int j = 0; j < (int)staffTripList[i].size() - 1; j++)
        {
            temp = temp + param.staffTime_matrix[staffTripList[i][j]][staffTripList[i][j+1]];
            cusCompleTime[staffTripList[i][j + 1]] = temp;
            
        }
        staffCompleTime[i] = temp + param.staffTime_matrix[staffTripList[i].back()][0];
        if (staffCompleTime[i] > maxStaffTime) {maxStaffTime = staffCompleTime[i];}
    }
    for (int i = 0; i < (int)droneTripList.size(); i++)
    {
        temp = 0;
        for (int j = 0; j < (int)droneTripList[i].size(); j++)
        {
            if (droneTripList.empty()) {continue;}
            temp1 = param.droneTime_matrix[0][droneTripList[i][j][0]];
            cusCompleTime[droneTripList[i][j][0]] = temp1;
            for (int k = 0; k < (int)droneTripList[i][j].size() - 1; k++)
            {
                temp1 = temp1 + param.droneTime_matrix[droneTripList[i][j][k]][droneTripList[i][j][k+1]];
                cusCompleTime[droneTripList[i][j][k+1]] = temp1;
            }
            droneTripCompleTime[i][j] = temp1 + param.droneTime_matrix[droneTripList[i][j].back()][0];
            temp = temp + droneTripCompleTime[i][j];
        }
        droneCompleTime[i] = temp;
        if (temp > maxDroneTime) {maxDroneTime = temp;}
    }
    
    double maxTime = std::max(maxDroneTime, maxStaffTime);
    
    for (int i = 0; i < (int)staffTripList.size(); i++){
        if (staffTripList.empty()) {continue;}
        
        for (int j = 0; j < (int)staffTripList[i].size(); j++)
        {
            cz = cz + std::max(0., staffCompleTime[i] - cusCompleTime[staffTripList[i][j]] - config.sampleLimitWaitingTime);
        }
    }

    for (int i = 0; i < (int)droneTripList.size(); i++)
    {
        for (int j = 0; j < (int)droneTripList[i].size(); j++)
        {
            if (droneTripList[i][j].empty()) {continue;}

            for (int k = 0; k < (int)droneTripList[i][j].size(); k++)
            {
                cz = cz + std::max(0.,droneTripCompleTime[i][j] - cusCompleTime[droneTripList[i][j][k]] - config.sampleLimitWaitingTime);
            }
            dz = dz + std::max(0., droneTripCompleTime[i][j] - config.sampleLimitWaitingTime);
        }
    }

    return maxTime + alpha1 * cz + alpha2 * dz;
}

bool solution::checkFeasible()
{
    std::vector<double> staffCompleTime(config.numStaff, 0);
    std::vector<double> droneCompleTime(config.numDrone, 0);
    std::vector<double> cusCompleTime(param.numCus + 1, 0);
    std::vector<std::vector<double>> droneTripCompleTime;
    
    int maxSize = 0;
    for (int  i = 0; i < (int)droneTripList.size(); i++){
        if (maxSize < (int)droneTripList[i].size()){
            maxSize = (int)droneTripList[i].size();
        }
    } 

    for (int i = 0; i < config.numDrone; i++)
    {
        std::vector<double> tripTime(maxSize, 0);
        droneTripCompleTime.push_back(tripTime);
    }
    
    double maxStaffTime = 0, maxDroneTime = 0;

    double temp, temp1;
    cz = 0, dz = 0;

    for (int i = 0; i < staffTripList.size(); i++){
        if (staffTripList[i].empty()) {continue;}

        temp = param.staffTime_matrix[0][staffTripList[i][0]];
        cusCompleTime[staffTripList[i][0]] = temp;

        for (int j = 0; j < (int)staffTripList[i].size() - 1; j++){
            temp = temp + param.staffTime_matrix[staffTripList[i][j]][staffTripList[i][j+1]];
            cusCompleTime[staffTripList[i][j + 1]] = temp;
        }
        staffCompleTime[i] = temp + param.staffTime_matrix[staffTripList[i].back()][0];

        if (staffCompleTime[i] > maxStaffTime) {maxStaffTime = staffCompleTime[i];}
    }

    for (int i = 0; i <droneTripList.size(); i++)
    {
        temp = 0;
        for (int j = 0; j < droneTripList[i].size(); j++)
        {
            if (droneTripList.empty()) {continue;}
            temp1 = param.droneTime_matrix[0][droneTripList[i][j][0]];
            cusCompleTime[droneTripList[i][j][0]] = temp1;

            for (int k = 0; k < (int)droneTripList[i][j].size() - 1; k++)
            {
                temp1 = temp1 + param.droneTime_matrix[droneTripList[i][j][k]][droneTripList[i][j][k+1]];
                cusCompleTime[droneTripList[i][j][k+1]] = temp1;
            }
            droneTripCompleTime[i][j] = temp1 + param.droneTime_matrix[droneTripList[i][j].back()][0];
            temp = temp + droneTripCompleTime[i][j];
        }
        droneCompleTime[i] = temp;
        if (temp > maxDroneTime) {maxDroneTime = temp;}
    }
    
    for (int i = 0; i < staffTripList.size(); i++){
        if (staffTripList.empty()) {continue;}
        
        for (int j = 0; j < (int)staffTripList[i].size(); j++)
        {
            cz = cz + std::max(0., staffCompleTime[i] - cusCompleTime[staffTripList[i][j]] - config.sampleLimitWaitingTime);
        }
    }

    if (cz != 0) {return false;}

    for (int i = 0; i < droneTripList.size(); i++)
    {
        for (int j = 0; j < droneTripList[i].size(); j++)
        {
            if (droneTripList[i][j].empty()) {continue;}

            for (int k = 0; k < (int)droneTripList[i][j].size(); k++)
            {
                cz = cz + std::max(0.,droneTripCompleTime[i][j] - cusCompleTime[droneTripList[i][j][k]] - config.sampleLimitWaitingTime);
            }
            dz = dz + std::max(0., droneTripCompleTime[i][j] - config.sampleLimitWaitingTime);
        }
    }
    
    if ((cz != 0) or (dz != 0)) {return false;}

    return true;
}

solution::solution() = default;
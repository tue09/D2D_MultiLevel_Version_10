#include <fstream>
#include <iostream>
#include "parameter.h"
#include <cmath>

parameter::parameter(double droneVelocity, double staffVelocity, int limitationFlighTime, const std::string &path)
{
    std::ifstream file(path);
    std::string line;
    std::string tmp;
    if (file.is_open())
    {
        std::getline(file, line);
        line.replace(line.begin(), line.begin() + 10, "");
        line.erase(line.find_last_of(' '));
        numCus = std::stoi(line);
        std::getline(file, line);
        double x, y, z;

        coordinates.push_back({0, 0});
        while (file >> x >> y >> z)
        {
            coordinates.push_back({x, y});
        }coordinates.push_back({0, 0});
    
        for (int i = 0; i < numCus + 2; i++){
            std::vector<double> Distances;
            std::vector<double> DroneTimes;
            std::vector<double> StaffTimes;
            for (int j = 0; j < numCus + 2; j++){
                double distance = sqrt(pow(coordinates[i][0] - coordinates[j][0], 2)
                                    + pow(coordinates[i][1] - coordinates[j][1], 2));
                Distances.push_back(distance);
                DroneTimes.push_back(distance / droneVelocity);
                StaffTimes.push_back(distance / staffVelocity);
            }
            distance_matrix.push_back(Distances);
            droneTime_matrix.push_back(DroneTimes);
            staffTime_matrix.push_back(StaffTimes);
        }
        cusServedByStaff.resize(numCus + 1, false);
        cusServedByStaff[0] = false;

        for (int i =1; i < numCus + 1; i++)
        {
            if (droneTime_matrix[0][i] > limitationFlighTime) cusServedByStaff[i] = true;
        }

        size_t beg = path.find_last_of("//");
        size_t end = path.find_last_of('.');

        data = path.substr(0, end).substr(beg + 1);
    }
}

parameter::parameter() = default;
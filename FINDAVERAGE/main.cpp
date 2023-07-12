#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <chrono>

#include "nlohmann/json.hpp"


using namespace std::chrono;
using json = nlohmann::json;



int main(int argc, char **argv)
{    
    std::ifstream file("D:/Users/ADMIN/Documents/0.Study/Multi_Level/FINDAVERAGE/result_50_.json");
    json tue;
    if (file.is_open())
    {
        json jsonAvg;
        file >> jsonAvg;
        std::vector<std::string> fileList = {"50.10.1.txt", "50.10.2.txt", "50.10.3.txt", "50.10.4.txt", "50.20.1.txt", "50.20.2.txt", "50.20.3.txt", "50.20.4.txt", "50.30.1.txt", "50.30.2.txt", "50.30.3.txt", "50.30.4.txt", "50.40.1.txt", "50.40.2.txt", "50.40.3.txt", "50.40.4.txt"};
        std::string type = "100";
        for (int i = 0; i < fileList.size(); i++)
        {
            std::cout<<fileList[i];
            std::string file = fileList[i];
            std::string temp;
            double average = 0;
            double tue = 0;
            for (int j = 1; j <= 10; j++)
            {

                temp = file + "." + std::to_string(j);
                std::cout<<std::endl<<temp;
                tue = std::stod(jsonAvg[temp]["best feasible score"].get<std::string>());
                average = average + tue;
            }
            jsonAvg[file] = average / 10;
        }
        std::ofstream o ("D:/Users/ADMIN/Documents/0.Study/Multi_Level/FINDAVERAGE/" + type + "_" + ".json");
        o << std::setw(4) << jsonAvg << std::endl;
        o.close();
    } else
    {
        std::cout<<"Cannot open this file";
    }
    return 0;
}

#ifndef DASTS2_VERSION8_C_TABUSEARCH_H
#define DASTS2_VERSION8_C_TABUSEARCH_H

#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Config.h"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Input.h"
#include "iostream"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Solution.h"
#include "nlohmann/json.hpp"

using json = nlohmann::json;

class TabuSearch
{
public:
    Config config;
    Input input;

    Solution initSolution;
    Solution currentSolution;
    Solution bestSolution;

    int tabuDuration{};
    double alpha1{};
    double alpha2{};

    TabuSearch();

    TabuSearch(Config &conf, Input &inp);

    std::tuple<double, Solution> run(json &log, std::string &path_e, Input &input, Solution solution, std::map<int, std::vector<int>> Map, int level);

    void runPostOptimization(json &log);

    static void runEjection(Solution &solution);

    static void runInterRoute(Solution &solution);

    static void runIntraRoute(Solution &solution);

    void updatePenalty(double dz, double cz);
};

#endif 

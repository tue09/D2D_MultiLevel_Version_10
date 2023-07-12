
#ifndef DASTS2_VERSION8_C_MULTILEVEL_H
#define DASTS2_VERSION8_C_MULTILEVEL_H

#include "nlohmann/json.hpp"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Config.h"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Solution.h"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Input.h"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/tabuSearch/TabuSearch.h"
#include <map>
#include <tuple>

class MultiLevel
{
public:
    Config config;
    Input input;
    TabuSearch tabuSearch;

    Solution initSolution;
    Solution currentSolution;
    Solution bestSolution;

    MultiLevel();

    MultiLevel(Config &config, Input &input);

    int numCustomer{};
    int tabuDuration{};

    void setConfigandInput(Config &config, Input &input);

    std::vector<std::vector<double>> droneTimeMatrix{};
    std::vector<std::vector<double>> techTimeMatrix{};

    std::vector<std::vector<double>> convertMatrix (std::vector<std::vector<double>> currentMatrix, std::map<int, std::vector<int>> Map);

    std::tuple<double, Solution, std::vector<std::vector<int>>> tabuInMultiLevel (Solution solution, int numRun);

    std::vector<std::map<int, std::vector<int>>> mapLevel;

    std::vector<std::vector<std::vector<double>>> DistanceMatrixLevel;

    std::vector<std::vector<bool>> C1Level;

    std::tuple<Solution, std::vector<std::tuple<int, int>>> beUpdate(Solution solution, int NumCus, std::vector<std::vector<double>> distanceMatrix, int Level);

    std::tuple<int, Solution, std::map<int, std::vector<int>>> mergeSol(Solution solution, Config &config, Input &input, int NumCus, std::vector<std::vector<double>> DistanceMatrix, int Level);
    
    std::tuple<Solution, std::map<int, std::vector<int>>> mergeProcess(Config &config, Input &input, std::vector<std::map<int, std::vector<int>>> &mapLevel, std::vector<std::vector<std::vector<double>>> &DistanceMatrixLevel, std::vector<std::vector<bool>> &C1Level); 

    Solution splitSol(Solution solution, std::map<int, std::vector<int>> Map);

    Solution splitProcess(Solution solution, Config &config, Input &input, std::vector<std::map<int, std::vector<int>>> &mapLevel, std::vector<std::vector<std::vector<double>>> &DistanceMatrixLevel, std::vector<std::vector<bool>> &C1Level);

    std::tuple<double, Solution> run(Config &config, Input &input);
    //merge_sol
    //merge_process
    //split_sol
    //split_process
// merge point one by one
//main process: Init Sol -> Tabu(40) -> merge_process:((Best(level_i) -> merge_sol -> Tabu(40) -> Best_new(level_i+1)) * num_level) 
//                                  -> Best(level_3) -> split_process:((Best(level_i) -> split_sol -> Tabu(40) -> Best(level_i-1)) * num_level) -> Best_Solution
//
//{1, 2, 4, 10, 5, 8, 6, 3, 7, 9} <(2, 4) and (6, 3)> -> {1, 2, 10, 5, 8, 3, 7, 9} -> {1, 2, 8, 4, 6, 3, 5 ,7}
// => remember_map_level_1: 1: {1}; 2: {2, 4}; 3: {6, 3}, 4: {5}, 5: {7}, 6: {8}, 7: {9}, 8: {10}
// {1, 2, 8, 4, 6, 3, 5, 7} <(2, 8) and (3, 5)> -> {1, 2, 4, 6, 3, 7} -> {1, 2, 4, 5, 3, 6}
// => remember_map_level_2: 1: {1}, 2: {2, 8}, 3: {3, 5}, 4: {4}, 5: {6}, 6: {7}
// => main_remember_map : 1: {1}, 2: {2, 4, 10}, 3: {6, 3, 7}, 4: {5}, 5: {8}, 6: {9}
//
//{1, 2, 3, 6, 4, 5} <(1, 2) and (3, 6)> -> {1, 3, 4, 5} -> {1, 2, 3, 4}
//
//{1, 2, 4, 10, 5, 8, 7, 6, 3, 9} <(2, 4) and (7, 6)> -> {1, 2, 10, 5, 8, 7, 3, 9} -> {1, 2, 8, 4, 6, 5, 3, 7}
//
//
//
//{1, 10, 4, 3, 5, 8, 6, 7, 11, 9, 2, 12} <(3, 5) and (4, 3) and (10, 4)> -> {1, 3, 4, 5, 8, 6, 7, 11, 9, 2, 12} 
//                                               -> {1, 3, 4, 5, 8, 9, 7, 10, 9, 2, 11}
//{10, 4, 3, 5}
//
//
//{1, 10, 4, 3, 5, 8, 6, 7, 11, 9, 2, 12} <(3, 5) and (4, 3) and (10, 4) and (6, 7)> 
//
//{10, 4, 3, 5} | {6, 7}
//
//4, 5, 7, 10
//
//{1, 3, 8, 6, 11, 9, 2, 12} -> {1, 3, 5, 4, 7, 6, 2, 8}
//
//
//
//
//{1, 3, 4, 5, 10, 8, 6, 7, 11, 9, 2, 12} <(4, 5)> -> {1, 3, 4, 10, 8, 6, 7, 11, 9, 2, 12} -> {1, 3, 4, 9, 7, 5, 6, 10, 8, 2, 11}
//1: {1}, 2: {2}, 3: {3}, 4: {4, 5}, 5: {6}, 6: {7}, 7: {8}, 8: {9}, 9: {10}, 10: {11}, 11: {12}
//{1, 3, 4, 9, 7, 5, 6, 10, 8, 2, 11} <(3, 4)> -> {1, 3, 8, 6, 4, 5, 9, 7, 2, 10}
//1: {1}, 2: {2}, 3: {3, 4}, 4: {5}, 5: {6}, 6: {7}, 7: {8}, 8: {9}, 9: {10}, 10: {11}
//{1, 3, 8, 6, 4, 5, 9, 7, 2, 10} <3, 8> -> {1, 3, 6, 4, 5, 8, 7, 2, 9}
//1: {1}, 2: {2}, 3: {3, 8}, 4: {4}, 5: {5}, 6: {6}, 7: {7}, 8: {9}, 9: {10}
//
// => Map is: 1: {1}, 2: {2}, 3: {3, 8}, 4: {4}, 5: {5}, 6: {6}, 7: {7}, 8: {9}, 9: {10} -> 1: {1}, 2: {2}, 3: {}
//
//0, 1, 2, 6, 7, 4, 8, 9
//



};

#endif
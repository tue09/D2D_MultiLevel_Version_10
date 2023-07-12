#include "MultiLevel.h"
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <filesystem>
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Utils.h"
#include "D:/Users/ADMIN/Documents/0.Study/Multi_Level/DASTS2_VERSION8_C/src/Random.h"

using Random = effolkronium::random_static;

MultiLevel::MultiLevel(Config &config, Input &input)
{
    this->config = config;
    this->config.tabuMaxIter = config.tabu_max_ite;
    this->input = input;
    this->tabuDuration = Random::get(config.minTabuDuration, config.maxTabuDuration);
}

void MultiLevel::setConfigandInput(Config &config, Input &input)
{
    this->input = input;
    this->config = config;
}

std::vector<std::vector<double>> MultiLevel::convertMatrix(std::vector<std::vector<double>> currentMatrix, std::map<int, std::vector<int>> Map)
{

    std::vector<std::vector<double>> newMatrix;
    int sizee = Map.size();
    std::vector<double> temp;
    for (int i = 0; i <= sizee; i++)
    {
        temp.resize(sizee + 1, 0);
        newMatrix.push_back(temp);
    }
    std::vector<int> plus;
    for (int i = 0; i < newMatrix.size() - 1; i++)
    {
        for (int j = 0; j < newMatrix.size() - 1; j++)
        {
            plus = Map[i];
            plus.insert(plus.end(), Map[j].begin(), Map[j].end());
            if (Map[j].size() > 1)
            {
                int sizee = Map[j].size();
                for (int k = 0; k < sizee - 1; k++)
                {
                    plus.pop_back();
                }
            }
            for (int k = 0; k < plus.size() - 1; k++)
            {
                newMatrix[i][j] = newMatrix[i][j] + currentMatrix[plus[k]][plus[k+1]];
            }
        }
    }
    for (int i = 0; i < newMatrix.size(); i++)
    {
        newMatrix[i][newMatrix.size() - 1] = newMatrix[i][0];
        newMatrix[newMatrix.size() - 1][i] = newMatrix[0][i];
    }  
    return newMatrix;
}

std::tuple<Solution, std::vector<std::tuple<int, int>>> MultiLevel::beUpdate(Solution solution, int NumCus, std::vector<std::vector<double>> distanceMatrix, int Level)
{
    std::vector<std::tuple<int , int>> update_Real;
    
    std::vector<std::tuple<int , int>> update;
    std::vector<std::tuple<int , int>> edgeSol;
    
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        if (solution.droneTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            if (solution.droneTripList[i][j].size() <= 1) {continue;}
            for (int k = 0; k < solution.droneTripList[i][j].size() - 1; k++)
            {
                edgeSol.push_back(std::make_tuple(solution.droneTripList[i][j][k], solution.droneTripList[i][j][k+1]));
            }
        }
    }   

    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        if (solution.techTripList[i].size() <= 1) {continue;}
        for (int j = 0; j < solution.techTripList[i].size() - 1; j++)
        {
            edgeSol.push_back(std::make_tuple(solution.techTripList[i][j], solution.techTripList[i][j+1]));
        }
    }
    std::cout<<std::endl<<"BUG AT 1";

    // Select 5% shortest edge from Solution
    int numUpdate = NumCus*0.05;
    while (update.size() < numUpdate)
    {
        double count = 9999999;
        int row = 1;
        int col = 1;

        for (int i = 1; i <= NumCus; i++)
        {
            for (int j = 1; j <= NumCus; j++)
            {
                auto find1 = std::find(update.begin(), update.end(), std::make_tuple(i, j));
                auto find2 = std::find(edgeSol.begin(), edgeSol.end(), std::make_tuple(i, j));
                if ((distanceMatrix[i][j] <= count) and (find1 == update.end()) and (find2 == edgeSol.end()) and (i != j))
                {
                    count = distanceMatrix[i][j];
                    row = i;
                    col = j;
                }
            }
        }
        update.push_back(std::make_tuple(row, col));
    }
    /*
    std::cout<<std::endl<<"solution BEFORE is: ";
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        std::cout<<std::endl<<"DRONE "<<i<<" : ";
        if (solution.droneTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            if (solution.droneTripList[i][j].size() <= 0) {continue;}
            for (int k = 0; k < solution.droneTripList[i][j].size(); k++)
            {
                std::cout<<solution.droneTripList[i][j][k]<<" ";
            }
            std::cout<<" | ";
        }
    }
    std::cout<<std::endl;
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        std::cout<<std::endl<<"TECH "<<i<<" : ";
        if (solution.techTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.techTripList[i].size(); j++)
        {
            std::cout<<solution.techTripList[i][j]<<" ";
        }
    }
    std::cout<<std::endl<<"Update BEFORE is: "<<std::endl;
    for (int i = 0; i < update.size(); i++)
    {
        std::cout<<std::get<0> (update[i])<<" | "<<std::get<1> (update[i])<<std::endl;
    }
    std::cout<<std::endl<<"BUG AT 2";
    */
    for (int l = 0; l < update.size(); l++)
    {
        int row = std::get<0> (update[l]);
        int col = std::get<1> (update[l]);
        int x1, x2, x3;
        int y1, y2, y3;
        for (int i = 0; i < solution.droneTripList.size(); i++)
        {
            if (solution.droneTripList[i].size() == 0) {continue;}
            for (int j = 0; j < solution.droneTripList[i].size(); j++)
            {
                if (solution.droneTripList[i][j].size() <= 1) {continue;}
                for (int k = 0; k < solution.droneTripList[i][j].size() - 1; k++)
                {
                    if (solution.droneTripList[i][j][k] == row)
                    {
                        x1 = i;
                        x2 = j;
                        x3 = k;
                    }
                    if (solution.droneTripList[i][j][k] == col)
                    {
                        y1 = i;
                        y2 = j;
                        y3 = k;
                    }
                }
            }
        }   

        for (int i = 0; i < solution.techTripList.size(); i++)
        {
            if (solution.techTripList[i].size() <= 1) {continue;}
            for (int j = 0; j < solution.techTripList[i].size() - 1; j++)
            {
                if (solution.techTripList[i][j] == row)
                {
                    x1 = i;
                    x2 = j;
                    x3 = -1;
                }
                if (solution.techTripList[i][j] == col)
                {
                    y1 = i;
                    y2 = j;
                    y3 = -1;
                }
            }
        }

        if ((x3 != -1) and (y3 != -1))
        {
            if ((x1 == y1) and (x2 == y2))
            {             
                if (x3 == (solution.droneTripList[x1][x2].size() - 1))
                {
                    int temp = solution.droneTripList[y1][y2][y3];
                    solution.droneTripList[y1][y2].erase(solution.droneTripList[y1][y2].begin() + y3);
                    solution.droneTripList[y1][y2].insert(solution.droneTripList[y1][y2].begin() + x3, temp);
                }
                else
                {
                    int temp = solution.droneTripList[x1][x2][x3 + 1];
                    solution.droneTripList[x1][x2][x3+1] = solution.droneTripList[y1][y2][y3];
                    solution.droneTripList[y1][y2][y3] = temp;
                }                
            }
            else
            {
                std::vector<int> temp1;
                std::vector<int> temp2;
                for (int i = x3 + 1; i < solution.droneTripList[x1][x2].size() - 1; i++)
                {
                    temp1.push_back(solution.droneTripList[x1][x2][i]);
                }
                solution.droneTripList[x1][x2].erase(solution.droneTripList[x1][x2].begin() + x3 + 1, solution.droneTripList[x1][x2].end());
                for (int i = y3; i < solution.droneTripList[y1][y2].size() - 1; i++)
                {
                    temp2.push_back(solution.droneTripList[y1][y2][i]);
                }
                solution.droneTripList[y1][y2].erase(solution.droneTripList[y1][y2].begin() + y3, solution.droneTripList[y1][y2].end());

                solution.droneTripList[x1][x2].insert(solution.droneTripList[x1][x2].end(), temp2.begin(), temp2.end());
                solution.droneTripList[y1][y2].insert(solution.droneTripList[y1][y2].end(), temp1.begin(), temp1.end());
            }
        }
        else if ((x3 != -1) and (y3 == -1))
        {
            bool flag = false;
            for (int i = y2 + 1; i < solution.techTripList[y1].size() - 1; i++)
            {
                if (C1Level[Level - 1][solution.techTripList[y1][i]] == true) 
                {
                    flag = true;
                    break;
                }
            }
            if (flag == true) {continue;}
            std::vector<int> temp1;
            std::vector<int> temp2;
            for (int i = x3 + 1; i < solution.droneTripList[x1][x2].size() - 1; i++)
            {
                temp1.push_back(solution.droneTripList[x1][x2][i]);
            }
            solution.droneTripList[x1][x2].erase(solution.droneTripList[x1][x2].begin() + x3 + 1, solution.droneTripList[x1][x2].end());

            for (int i = y2; i < solution.techTripList[y1].size() - 1; i++)
            {
                temp2.push_back(solution.techTripList[y1][i]);
            }
            solution.techTripList[y1].erase(solution.techTripList[y1].begin() + y2, solution.techTripList[y1].end());

            solution.droneTripList[x1][x2].insert(solution.droneTripList[x1][x2].end(), temp2.begin(), temp2.end());
            solution.techTripList[y1].insert(solution.techTripList[y1].end(), temp1.begin(), temp1.end());
        }
        else if ((x3 == -1) and (y3 != -1))
        {
            bool flag = false;
            for (int i = x2 + 1; i < solution.techTripList[x1].size() - 1; i++)
            {
                if (C1Level[Level - 1][solution.techTripList[x1][i]] == true) 
                {
                    flag = true;
                    break;
                }
            }
            if (flag == true) {continue;}
            std::vector<int> temp1;
            std::vector<int> temp2;
            for (int i = y3; i < solution.droneTripList[y1][y2].size() - 1; i++)
            {
                temp1.push_back(solution.droneTripList[y1][y2][i]);
            }
            solution.droneTripList[y1][y2].erase(solution.droneTripList[y1][y2].begin() + y3, solution.droneTripList[y1][y2].end());

            for (int i = x2 + 1; i < solution.techTripList[x1].size() - 1; i++)
            {
                temp2.push_back(solution.techTripList[x1][i]);
            }
            solution.techTripList[x1].erase(solution.techTripList[x1].begin() + x2 + 1, solution.techTripList[x1].end());

            solution.droneTripList[y1][y2].insert(solution.droneTripList[y1][y2].end(), temp2.begin(), temp2.end());
            solution.techTripList[x1].insert(solution.techTripList[x1].end(), temp1.begin(), temp1.end());
        }
        else
        {
            if (x1 == y1)
            {
                if (x2 == (solution.techTripList[x1].size() - 1))
                {
                    int temp = solution.techTripList[y1][y2];
                    solution.techTripList[y1].erase(solution.techTripList[y1].begin() + y2);
                    solution.techTripList[y1].insert(solution.techTripList[y1].begin() + x2, temp);
                }
                else
                {
                    int temp = solution.techTripList[x1][x2 + 1];
                    solution.techTripList[x1][x2 + 1] = solution.techTripList[y1][y2];
                    solution.techTripList[y1][y2] = temp;
                }          
            }
            else
            {
                std::vector<int> temp1;
                std::vector<int> temp2;   
                for (int i = x2 + 1; i < solution.techTripList[x1].size() - 1; i++)
                {
                    temp1.push_back(solution.techTripList[x1][i]);
                }      
                solution.techTripList[x1].erase(solution.techTripList[x1].begin() + x2 + 1, solution.techTripList[x1].end());

                for (int i = y2; i < solution.techTripList[y1].size() - 1; i++)
                {
                    temp2.push_back(solution.techTripList[y1][i]);
                }
                solution.techTripList[y1].erase(solution.techTripList[y1].begin() + y2, solution.techTripList[y1].end());

                solution.techTripList[x1].insert(solution.techTripList[x1].end(), temp1.begin(), temp1.end());
                solution.techTripList[y1].insert(solution.techTripList[y1].end(), temp2.begin(), temp2.end());
            }
        }

    } 
    std::cout<<std::endl<<"BUG AT 3";
    int length = 0;
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            length = length + std::max((int)solution.droneTripList[i][j].size() - 1, 0);
        }
    }
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        length = length + std::max((int)solution.techTripList[i].size() - 1, 0);
    }
    int number = NumCus * config.percent_match + 1;
    int numUpdateReal = std::min(number, length);

    while (update_Real.size() < numUpdateReal)
    {
        double count = 9999999;
        int row = 1;
        int col = 1;
        for (int i = 0; i < solution.droneTripList.size(); i++)
        {
            if (solution.droneTripList[i].size() == 0) {continue;}
            for (int j = 0; j < solution.droneTripList[i].size(); j++)
            {
                if (solution.droneTripList[i][j].size() <= 1) {continue;}
                for (int k = 0; k < solution.droneTripList[i][j].size() - 1; k++)
                {
                    auto find = std::find(update_Real.begin(), update_Real.end(), std::make_tuple(solution.droneTripList[i][j][k], solution.droneTripList[i][j][k+1]));
                    if ((distanceMatrix[solution.droneTripList[i][j][k]][solution.droneTripList[i][j][k+1]] <= count) && (find == update_Real.end()))
                    {
                        count = distanceMatrix[solution.droneTripList[i][j][k]][solution.droneTripList[i][j][k+1]];
                        row = solution.droneTripList[i][j][k];
                        col = solution.droneTripList[i][j][k+1];
                    }
                }
            }
        }        
        for (int i = 0; i < solution.techTripList.size(); i++)
        {
            if (solution.techTripList[i].size() <= 1) {continue;}
            for (int j = 0; j < solution.techTripList[i].size() - 1; j++)
            {
                auto find = std::find(update_Real.begin(), update_Real.end(), std::make_tuple(solution.techTripList[i][j], solution.techTripList[i][j+1]));
                if ((distanceMatrix[solution.techTripList[i][j]][solution.techTripList[i][j+1]] <= count) && (find == update_Real.end()))
                {
                    count = distanceMatrix[solution.techTripList[i][j]][solution.techTripList[i][j+1]];
                    row = solution.techTripList[i][j];
                    col = solution.techTripList[i][j+1];
                }
            }
        }
        update_Real.push_back(std::make_tuple(row, col));
    }
    
    std::cout<<std::endl<<"solution is: ";
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        std::cout<<std::endl<<"DRONE "<<i<<" : ";
        if (solution.droneTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            if (solution.droneTripList[i][j].size() <= 0) {continue;}
            for (int k = 0; k < solution.droneTripList[i][j].size(); k++)
            {
                std::cout<<solution.droneTripList[i][j][k]<<" ";
            }
            std::cout<<" | ";
        }
    }
    std::cout<<std::endl;
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        std::cout<<std::endl<<"TECH "<<i<<" : ";
        if (solution.techTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.techTripList[i].size(); j++)
        {
            std::cout<<solution.techTripList[i][j]<<" ";
        }
    }
    
    std::cout<<std::endl<<"Update REAL is: "<<std::endl;
    for (int i = 0; i < update_Real.size(); i++)
    {
        std::cout<<std::get<0> (update_Real[i])<<" | "<<std::get<1> (update_Real[i])<<std::endl;
    }
    
    std::cout<<std::endl<<"SCORE OF SOLUTION BEFORE MAKE TUPLE IS: "<<solution.getScore();
    return std::make_tuple(solution, update_Real);

}

std::tuple<int, Solution, std::map<int, std::vector<int>>> MultiLevel::mergeSol(Solution solution, Config &config, Input &input, int NumCus, std::vector<std::vector<double>> DistanceMatrix, int Level)
{

    //make update for matrix
    std::tuple<Solution, std::vector<std::tuple<int, int>>> update1;
    std::vector<std::tuple<int, int>> update;
    update1 = beUpdate(solution, NumCus, DistanceMatrix, Level);
    update = std::get<1> (update1);
    solution = std::get<0> (update1);
    std::cout<<std::endl<<"SCORE BE REAL IS: "<<solution.getScore();
    //merge of DroneTripList and TechTripList: First Part
    int numUpdate = update.size();
    std::vector<std::tuple<int , int>> updateFake = update;
    std::map<int, std::vector<int>> map;
    map[0] = {0};
    std::vector<std::vector<int>> beMerge;
    std::vector<int> temp;
    std::tuple<int, int> fi;
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        if (solution.droneTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            if (solution.droneTripList[i][j].size() <= 1) {continue;}
            for (int k = 0; k < solution.droneTripList[i][j].size() - 1; k++)
            {
                fi = std::make_tuple(solution.droneTripList[i][j][k], solution.droneTripList[i][j][k+1]);
                for (int u = 0; u < updateFake.size(); u++)
                {
                    if (fi == updateFake[u])
                    {
                        if (temp.size() == 0)
                        {
                            temp.push_back(solution.droneTripList[i][j][k]);
                            temp.push_back(solution.droneTripList[i][j][k+1]);
                        }
                        else
                        {
                            if (temp[temp.size() - 1] != solution.droneTripList[i][j][k])
                            {
                                beMerge.push_back(temp);
                                temp.resize(0);
                                temp.push_back(solution.droneTripList[i][j][k]);
                                temp.push_back(solution.droneTripList[i][j][k+1]);
                            }
                            else
                            {
                                temp.push_back(solution.droneTripList[i][j][k+1]);
                            }
                        }
                        updateFake.erase(updateFake.begin() + u);
                        break;
                    }
                }
            }
            if (temp.size() != 0) {beMerge.push_back(temp);}
            temp = {};
        }
    }
    temp = {};

    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        if (solution.techTripList[i].size() <= 1) {continue;}
        for (int j = 0; j < solution.techTripList[i].size() - 1; j++)
        {
            fi = std::make_tuple(solution.techTripList[i][j], solution.techTripList[i][j+1]);
            for (int u = 0; u < updateFake.size(); u++)
            {
                if (fi == updateFake[u])
                {
                    if (temp.size() == 0)
                    {
                        temp.push_back(solution.techTripList[i][j]);
                        temp.push_back(solution.techTripList[i][j+1]);
                    }
                    else
                    {
                        if (temp[temp.size() - 1] != solution.techTripList[i][j])
                        {
                            beMerge.push_back(temp);
                            temp.resize(0);
                            temp.push_back(solution.techTripList[i][j]);
                            temp.push_back(solution.techTripList[i][j+1]);
                        }
                        else
                        {
                            temp.push_back(solution.techTripList[i][j+1]);
                        }
                    }
                    updateFake.erase(updateFake.begin() + u);
                    break;
                }
            }
        }
        if (temp.size() != 0) {beMerge.push_back(temp);}
        temp = {};
    }


    std::vector<int> del;
    for (int u = 0; u < beMerge.size(); u++)
    {
        for (int i = 0; i < solution.droneTripList.size(); i++)
        {
            if (solution.droneTripList[i].size() == 0) {continue;}
            for (int j = 0; j < solution.droneTripList[i].size(); j++)
            {
                if (solution.droneTripList[i][j].size() <= 1) {continue;}
                for (int k = 0; k < solution.droneTripList[i][j].size() - 1; k++)
                {

                    if (beMerge[u][0] == solution.droneTripList[i][j][k])
                    {
                        auto minElement = std::min_element(beMerge[u].begin(), beMerge[u].end());
                        int insertt = *minElement;
                        for (int l = 0; l < beMerge[u].size(); l++)
                        {
                            del.push_back(solution.droneTripList[i][j][k]);
                            solution.droneTripList[i][j].erase(solution.droneTripList[i][j].begin() + k);
                        }
                        solution.droneTripList[i][j].insert(solution.droneTripList[i][j].begin() + k, insertt);
                        break;
                    }
                    
                }
            }
        }
    }
    for (int u = 0; u < beMerge.size(); u++)
    {
        for (int i = 0; i < solution.techTripList.size(); i++)
        {
            if (solution.techTripList[i].size() <= 1) {continue;}
            for (int j = 0; j < solution.techTripList[i].size() - 1; j++)
            {

                if (beMerge[u][0] == solution.techTripList[i][j])
                {
                    auto minElement = std::min_element(beMerge[u].begin(), beMerge[u].end());
                    int insertt = *minElement;
                    map[insertt] = {std::get<0>(update[u]), std::get<1>(update[u])};
                    for (int l = 0; l < beMerge[u].size(); l++)
                    {
                        del.push_back(solution.techTripList[i][j]);
                        solution.techTripList[i].erase(solution.techTripList[i].begin() + j);
                    }
                    solution.techTripList[i].insert(solution.techTripList[i].begin() + j, insertt);
                    break;
                }
                
                
            }
        }
    }
    //merge of DroneListTrip and TechTripList: Second Part
    for (int i = 0; i < beMerge.size(); i++)
    {
        auto minElement = std::min_element(beMerge[i].begin(), beMerge[i].end());
        map[*minElement] = beMerge[i];
    }
    int max = 0;
    std::vector<int> fill;
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            for (int k = 0; k < solution.droneTripList[i][j].size(); k++)
            {
                if (solution.droneTripList[i][j][k] > max) max = solution.droneTripList[i][j][k];
            }
        }
    }
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        for (int j = 0; j < solution.techTripList[i].size(); j++)
        {
            if (solution.techTripList[i][j] > max) max = solution.techTripList[i][j];
        }
    }
    for (int i = 1; i <= max; i++)
    {
        int keytofind = i;
        auto ite1 = map.find(keytofind);
        auto ite2 = std::find(del.begin(), del.end(), i);
        if ((ite1 == map.end()) and (ite2 == del.end()))
        {
            map[i] = {i};
        }
    }
    for (int i = 1; i <= max; i++)
    {
        fill.push_back(i);
    }
    for (int u = 1; u <= max; u++)
    {
        for (int i = 0; i < solution.droneTripList.size(); i++)
        {
            for (int j = 0; j < solution.droneTripList[i].size(); j++)
            {
                auto find = std::find(solution.droneTripList[i][j].begin(), solution.droneTripList[i][j].end(), u);
                if (find != solution.droneTripList[i][j].end()) 
                {
                    fill.erase(std::remove(fill.begin(), fill.end(), u), fill.end());
                }
            }
        }

        for (int i = 0; i < solution.techTripList.size(); i++)
        {
            auto find = std::find(solution.techTripList[i].begin(), solution.techTripList[i].end(), u);
            if (find != solution.techTripList[i].end())
            {
                fill.erase(std::remove(fill.begin(), fill.end(), u), fill.end());
            }
        }
    }
    
    std::sort(fill.begin(), fill.end());
    for (int i = 1; i <= max; i++)
    {
        int keytofind = i;
        auto ite = map.find(keytofind);
        if (ite != map.end())
        {
            if (i > fill[(int)fill.size() - 1])
            {
                map[i - (int)fill.size()] = map[i];
            }
            else
            {
                for (int j = 0; j < (int)fill.size() - 1; j++)
                {
                    if ((fill[j] < i) and (fill[j+1] > i))
                    {
                        map[i - (j+1)] = map[i];
                    }
                }
            }
        }
    }
    
    for (int i = NumCus - numUpdate + 1; i <= max; i++)
    {
        map.erase(i);
    }
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            for (int k = 0; k < solution.droneTripList[i][j].size(); k++)
            {
                if (solution.droneTripList[i][j][k] > fill[(int)fill.size() - 1])
                {
                    
                    solution.droneTripList[i][j][k] = solution.droneTripList[i][j][k] - (int)fill.size();
                }
                else
                {
                    for (int u = 0; u < (int)fill.size() - 1; u++)
                    {
                        if ((fill[u] < solution.droneTripList[i][j][k]) and (solution.droneTripList[i][j][k] < fill[u+1]))
                        {
                            solution.droneTripList[i][j][k] = solution.droneTripList[i][j][k] - (u+1);
                        }
                    }
                } 
            }
        }
    }
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        for (int j = 0; j < solution.techTripList[i].size(); j++)
        {
            if (solution.techTripList[i][j] > fill[(int)fill.size() - 1])
            {
                solution.techTripList[i][j] = solution.techTripList[i][j] - (int)fill.size();
            }
            else
            {
                for (int u = 0; u < (int)fill.size(); u++)
                {
                    if ((fill[u] < solution.techTripList[i][j]) and (solution.techTripList[i][j] < fill[u+1]))
                    {                        
                        solution.techTripList[i][j] = solution.techTripList[i][j] - (u+1);
                    }
                }
            }
        }
    }
    /*
    std::cout<<std::endl<<"solution after MERGE SOL is: ";
    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        std::cout<<std::endl<<"DRONE "<<i<<" : ";
        if (solution.droneTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            if (solution.droneTripList[i][j].size() <= 0) {continue;}
            for (int k = 0; k < solution.droneTripList[i][j].size(); k++)
            {
                std::cout<<solution.droneTripList[i][j][k]<<" ";
            }
            std::cout<<" | ";
        }
    }
    std::cout<<std::endl;
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        std::cout<<std::endl<<"TECH "<<i<<" : ";
        if (solution.techTripList[i].size() == 0) {continue;}
        for (int j = 0; j < solution.techTripList[i].size(); j++)
        {
            std::cout<<solution.techTripList[i][j]<<" ";
        }
    }
    std::cout<<std::endl<<"NUM UPDATE IS: "<<numUpdate;
    std::cout<<std::endl<<"MAP IS: "<<std::endl;
    for (const auto& pair : map) {
        std::cout << "Key: " << pair.first << ", Values: ";
        for (const auto& value : pair.second) {
            std::cout << value << " ";
        }
        std::cout << std::endl;
    }
    */

    return std::make_tuple(numUpdate, solution, map);
}

//main process: Init Sol -> Tabu(40) -> merge_process:((Best(level_i) -> merge_sol -> Tabu(40) -> Best_new(level_i+1)) * num_level) 
//                                  -> Best(level_3) -> split_process:((Best(level_i) -> split_sol -> Tabu(40) -> Best(level_i-1)) * num_level) -> Best_Solution

std::tuple<Solution, std::map<int, std::vector<int>>> MultiLevel::mergeProcess(Config &config, Input &input, std::vector<std::map<int, std::vector<int>>> &mapLevel, std::vector<std::vector<std::vector<double>>> &DistanceMatrixLevel, std::vector<std::vector<bool>> &C1Level)
{
    TabuSearch tabuSearch(config, input);
    Solution currentSol;
    currentSol.setInput(input);
    currentSol = tabuSearch.initSolution;
    std::tuple<int, Solution, std::map<int, std::vector<int>>> merge;
    std::map<int, std::vector<int>> Map;
    std::vector<std::vector<double>> distanceMatrix = input.distances;
    DistanceMatrixLevel.push_back(distanceMatrix);
    config.tabuMaxIter = config.tabu_max_ite;
    double bestScore = currentSol.getScore();
    int numcus = input.numCus;
    C1Level.push_back(input.cusOnlyServedByTech);
    for (int i = 0; i < config.num_level; i++)
    {
        json log;
        std::string path_e;  
        TabuSearch tabuSearch(config, input);
        MultiLevel multilev(config, input);
        std::tuple<double, Solution> result;
        currentSol.setInput(input);
        std::cout<<std::endl<<"Level "<<(i+1)<<": Score of Merge Before Tabu is: "<<currentSol.getScore()<<std::endl;
        result = tabuSearch.run(log, path_e, input, currentSol, Map, i);
        std::cout<<"AFTER TABU";
        Solution sol;
        sol.setInput(input);
        currentSol.setInput(input);
        double temp = currentSol.getScore();
        sol = std::get<1> (result);
        merge = multilev.mergeSol(sol, config, input, numcus, distanceMatrix, i+1);
        numcus = numcus - std::get<0> (merge);
        currentSol = std::get<1> (merge);
        std::cout<<std::endl<<"HAHHHHHHHHDsolution is: ";
        for (int i = 0; i < currentSol.droneTripList.size(); i++)
        {
            std::cout<<std::endl<<"DRONE "<<i<<" : ";
            if (currentSol.droneTripList[i].size() == 0) {continue;}
            for (int j = 0; j < currentSol.droneTripList[i].size(); j++)
            {
                if (currentSol.droneTripList[i][j].size() <= 0) {continue;}
                for (int k = 0; k < currentSol.droneTripList[i][j].size(); k++)
                {
                    std::cout<<currentSol.droneTripList[i][j][k]<<" ";
                }
                std::cout<<" | ";
            }
        }
        std::cout<<std::endl;
        for (int i = 0; i < currentSol.techTripList.size(); i++)
        {
            std::cout<<std::endl<<"TECH "<<i<<" : ";
            if (currentSol.techTripList[i].size() == 0) {continue;}
            for (int j = 0; j < currentSol.techTripList[i].size(); j++)
            {
                std::cout<<currentSol.techTripList[i][j]<<" ";
            }
        }
        if (bestScore > temp)
        {
            bestScore = temp;
        }
        mapLevel.push_back(std::get<2> (merge));
        distanceMatrix = multilev.convertMatrix(distanceMatrix, std::get<2> (merge));
        int sizee = distanceMatrix.size();
        std::vector<std::vector<double>> droneFlightMatrix(sizee, std::vector<double>(sizee, 0));
        std::vector<std::vector<double>> techMoveMatrix(sizee, std::vector<double>(sizee, 0));
        for (int j = 0; j < sizee; j++)
        {
            for (int k = 0; k < sizee; k++)
            {
                droneFlightMatrix[j][k] = distanceMatrix[j][k] / config.droneVelocity;
                techMoveMatrix[j][k] = distanceMatrix[j][k] / config.techVelocity;
            }
        }
        std::vector<std::vector<double>> coor(sizee, std::vector<double>(sizee, 0));
        input.numCus = numcus;
        std::cout<<std::endl<<"NUM CUS OS: "<<numcus;
        input.coordinates = coor;
        input.distances = distanceMatrix;
        DistanceMatrixLevel.push_back(distanceMatrix);
        input.droneTimes = droneFlightMatrix;
        input.techTimes = techMoveMatrix;
        std::vector<bool> C1(numcus + 1, false);

        for (const auto& pair : std::get<2> (merge))
        {
            int key = pair.first;
            const std::vector<int>& values = pair.second;
            for (int value : values)
            {
                for (int j = 0; j < input.cusOnlyServedByTech.size(); j++)
                {
                    if (input.cusOnlyServedByTech[value] == true)
                    {
                        C1[key] = true;
                    }
                }

            }
        }
        C1Level.push_back(C1);
        input.cusOnlyServedByTech = C1;
        currentSol.setInput(input);
        std::cout<<std::endl<<"HAHHHHHHHHDsolution is: ";
        for (int i = 0; i < currentSol.droneTripList.size(); i++)
        {
            std::cout<<std::endl<<"DRONE "<<i<<" : ";
            if (currentSol.droneTripList[i].size() == 0) {continue;}
            for (int j = 0; j < currentSol.droneTripList[i].size(); j++)
            {
                if (currentSol.droneTripList[i][j].size() <= 0) {continue;}
                for (int k = 0; k < currentSol.droneTripList[i][j].size(); k++)
                {
                    std::cout<<currentSol.droneTripList[i][j][k]<<" ";
                }
                std::cout<<" | ";
            }
        }
        std::cout<<std::endl;
        for (int i = 0; i < currentSol.techTripList.size(); i++)
        {
            std::cout<<std::endl<<"TECH "<<i<<" : ";
            if (currentSol.techTripList[i].size() == 0) {continue;}
            for (int j = 0; j < currentSol.techTripList[i].size(); j++)
            {
                std::cout<<currentSol.techTripList[i][j]<<" ";
            }
        }

        std::cout<<std::endl<<"SCORE OF SOLLLLLLLLLLLl: "<<currentSol.getScore();
    }
    return std::make_tuple(currentSol, std::get<2> (merge));
}

Solution MultiLevel::splitSol(Solution solution, std::map<int, std::vector<int>> Map)
{

    for (int i = 0; i < solution.droneTripList.size(); i++)
    {
        for (int j = 0; j < solution.droneTripList[i].size(); j++)
        {
            for (int k = 0; k < solution.droneTripList[i][j].size(); k++)
            {
                int temp = solution.droneTripList[i][j][k];
                solution.droneTripList[i][j].erase(solution.droneTripList[i][j].begin() + k);
                for (int u = Map[temp].size() - 1; u >= 0; u--)
                {
                    solution.droneTripList[i][j].insert(solution.droneTripList[i][j].begin() + k, Map[temp][u]);
                }
                k = k + Map[temp].size() - 1;
                if (k >= solution.droneTripList[i][j].size() - 1) {break;}
            }
        }
    }
    for (int i = 0; i < solution.techTripList.size(); i++)
    {
        for (int j = 0; j < solution.techTripList[i].size(); j++)
        {
            int temp = solution.techTripList[i][j];
            solution.techTripList[i].erase(solution.techTripList[i].begin() + j);
            for (int u = Map[temp].size() - 1; u >= 0; u--)
            {
                solution.techTripList[i].insert(solution.techTripList[i].begin() + j, Map[temp][u]);
            }
            j = j + Map[temp].size() - 1;
            if (j >= solution.techTripList[i].size() - 1) {break;}
        }
    }
    return solution;
}

Solution MultiLevel::splitProcess(Solution solution, Config &config, Input &input, std::vector<std::map<int, std::vector<int>>> &mapLevel, std::vector<std::vector<std::vector<double>>> &DistanceMatrixLevel, std::vector<std::vector<bool>> &C1Level)
{
    solution.setInput(input);
    double best = solution.getScore();
    std::map<int, std::vector<int>> Map;
    for (int i = 0; i < config.num_level; i++)
    {
        json log;
        std::string path_e;
        MultiLevel multilev(config, input);
        multilev.setConfigandInput(config, input);
        solution.setInput(input);
        solution = multilev.splitSol(solution, mapLevel[config.num_level - i - 1]);
        int sizee = DistanceMatrixLevel[config.num_level - i - 1].size();
        std::vector<std::vector<double>> droneFlightMatrix(sizee, std::vector<double>(sizee, 0));
        std::vector<std::vector<double>> techMoveMatrix(sizee, std::vector<double>(sizee, 0));
        for (int j = 0; j < sizee; j++)
        {
            for (int k = 0; k < sizee; k++)
            {
                droneFlightMatrix[j][k] = DistanceMatrixLevel[config.num_level - i - 1][j][k] / config.droneVelocity;
                techMoveMatrix[j][k] = DistanceMatrixLevel[config.num_level - i - 1][j][k] / config.techVelocity;
            }
        }
        std::vector<std::vector<double>> coor(sizee, std::vector<double>(sizee, 0));
        input.numCus = sizee - 2;
        input.coordinates = coor;
        input.distances = DistanceMatrixLevel[config.num_level - i - 1];
        input.droneTimes = droneFlightMatrix;
        input.techTimes = techMoveMatrix;
        input.cusOnlyServedByTech = C1Level[config.num_level - i - 1];
        solution.setInput(input);
        TabuSearch tabuSearch(config, input);
        std::cout<<std::endl<<"Level "<<(i+1)<<": Score of Split Before Tabu is: "<<solution.getScore()<<std::endl;
        std::tuple<double, Solution> result = tabuSearch.run(log, path_e, input, solution, Map, 0);
        best = std::get<0> (result);
        solution = std::get<1> (result);
    }
    return solution;
}

std::tuple<double, Solution> MultiLevel::run(Config &config, Input &input)
{
    json log;
    std::string path_e;
    MultiLevel multilev(config, input);
    /*
    std::vector<std::vector<int>> mainMatrix;
    std::map<int, std::vector<int>> Map;        
    TabuSearch tabuSearch(config, input);
    std::tuple<double, Solution, std::vector<std::vector<int>>> tue = tabuSearch.run(log, path_e, input, tabuSearch.initSolution, mainMatrix, Map, 0);
    Solution solution = std::get<1> (tue);
    */
    std::tuple<Solution, std::map<int, std::vector<int>>> result = multilev.mergeProcess(config, input, mapLevel, DistanceMatrixLevel, C1Level);
    Solution res_sol = std::get<0> (result);

    Solution solution = multilev.splitProcess(res_sol, config, input, mapLevel, DistanceMatrixLevel, C1Level);
    solution.setInput(input);
    double bestScore = solution.getScore();
    std::cout<<std::endl<<"best score is: "<<bestScore<<std::endl;
    return std::make_tuple(bestScore, solution);
}


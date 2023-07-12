#include "Config.h"

Config::Config()
{
    tabu_size = 5;
    max_ite = 500;
    num_runs = 5;
    terminate_iter = 200;
    tabuAlpha1 = 1;
    tabuAlpha2 = 1;
    tabuBeta = 0.5;
    epsilon = 1e-3;
    num_level = 3;
    percent_match = 0.2;
    tabu_max_ite = 40;


    droneVelocity = 0.83;
    staffVelocity = 0.58;
    numDrone = 4;
    numStaff = 4;
    droneLimitFlightTime = 120;
    sampleLimitWaitingTime = 60;


    use_ejection = true;
    use_inter = true;
    use_intra = true;


    ws = "D:\\Users\\ADMIN\\Documents\\0.Study\\Multi_Level\\DASTS2-PB1-C";
    resultfolder = "D:\\Users\\ADMIN\\Documents\\0.Study\\Multi_Level\\DASTS2-PB1-C\\result";
    dataPath = "\\data";
    dataName = "6.5.1.txt";
}
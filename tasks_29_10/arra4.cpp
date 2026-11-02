#include <iostream>


int main()
{
    srand(time(NULL));
    int raws,cols;
    std::cin >> cols >> raws;
    std::cout << std::endl;
    const int ROWS = raws,COLS = cols;

    int arr[COLS][ROWS];

    for(int i = 0; i < COLS;i++)
    {
        for (auto& r : arr[i])
        {
            r = rand() % 100 - 20;
            std::cout << r << ' ';
        }
        std::cout << std::endl;
    }

    int max = -100;
    int colID,rowID;

    for(int i = 0; i < COLS;i++)
    {
        for (int j = 0; j < ROWS;j++)
        {
            if (arr[i][j] > max)
            {
                max = arr[i][j];
                colID = i;
                rowID = j;
            }
        }
    }

    std::cout << "max: " << max << " colID: " << colID << " rawID: " << rowID << std::endl;

    return 0;
}
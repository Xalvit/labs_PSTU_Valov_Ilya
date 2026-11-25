#include <iostream>


int main()
{
    int n;
    std::cin >> n;
    int arr[n][n];

    for(auto& r : arr)
    {
        for (auto&r : r)
        {
            r = rand() % 9 + 1;
        }
    }

    for(int i = 0;i < n/2;i++)
    {
        for(int j = 0;j < n;j++)
        {
            if (i < j)
            {
                if (i + j < n-1)
                {
                    arr[i][j] = 0;
                }
            }
        }
    }


    for (auto& r : arr)
    {
        for(auto& r : r)
        {
            std::cout << r << ' ';
        }
        std::cout << std::endl;
    }

    return 0;
}
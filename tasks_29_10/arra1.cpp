#include <iostream>
#include <cmath>

int main()
{
    int n;
    int min = 1000000,minID,counterMin = 0,max = -INFINITY,maxID,counterMax = 0;
    std::cin >> n;
    const int SIZE = n;
    int array[SIZE];
    for(int i = 0; i < n;i++)
    {
        int temp;
        std::cin >> temp;
        array[i] = temp;
    }

    for(int i = 0; i < SIZE; i++)
    {
        if ( array[i] > max)
        {
            max = array[i];
            maxID = i;
        }
        if (array[i] < min)
        {
            min = array[i];
            minID = i;
        }
    }

    for(auto& r : array)
    {
        if(r == max)
        {
            counterMax += 1;
        }
        if(r == min)
        {
            counterMin += 1;
        }
    }

    std::cout << "max: " << max  << " maxID: " << maxID << " maxCounter: " << counterMax << "\nmin: " << min << " minID: " << minID << " minCounter: " << counterMin;

    return 0;
}
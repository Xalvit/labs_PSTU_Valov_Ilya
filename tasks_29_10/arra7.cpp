#include <iostream>

int main()
{
    srand(time(NULL));
    int arr[7];

    for (auto& r : arr)
    {
        r = rand() % 100 - 20;
        std::cout << r << ' ';
    }
    std::cout << std::endl;

    for (int i = 0; i < 7 - 1; i++) 
    {
        for (int j = 0; j < 7 - 1 - i; j++) 
        {
            if (arr[j] > arr[j + 1]) 
            {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    for (int i = 0; i < 7; i++)
    {
        std::cout << arr[i] << ' ';
    }

    std::cout << '\n';

    return 0;
}
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

    for (int i = 1; i < 7; i++)
    {
        int current = arr[i];
        int j = i - 1;

        while (j >= 0 && arr[j] > current) 
        {
            arr[j + 1] = arr[j];
            j--;
        }

        arr[j + 1] = current;
    }

    for (int i = 0; i < 7; i++)
    {
        std::cout << arr[i] << ' ';
    }

    std::cout << '\n';

    return 0;
}
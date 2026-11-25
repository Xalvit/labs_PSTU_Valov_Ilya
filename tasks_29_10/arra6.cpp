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

    int n = 7;

    for (int i = 0;i < 7;i++)
    {
        for (int j = 0; j < i;j++)
        {
            if (arr[j] > arr[i])
            {
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
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
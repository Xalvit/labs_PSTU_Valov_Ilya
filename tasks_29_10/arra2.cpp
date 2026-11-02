#include <iostream>

int main()
{
    srand(time(NULL));
    int n;
    std::cin >> n;
    const int SIZE = n;
    int arr[SIZE];
    std::cout << "Array: ";
    for(auto&r : arr)
    {
        r = rand() % 100;
        std::cout << r << ' ';
    }

    std::cout << std::endl;

    int temp = arr[0];
    bool sorted = true;

    for (int i = 0;i < SIZE;i++)
    {
        if (temp > arr[i])
        {
            sorted = false;
            break;
        }


        temp = arr[i];
    }

    std::cout << "Sorted: " << sorted;

    return 0;
}
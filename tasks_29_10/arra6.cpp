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

    for (int i = 0; i < n - 1; i++) {
        int minIndex = i;

        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minIndex]) {
                minIndex = j;
            }
        }

        int temp = arr[i];
        arr[i] = arr[minIndex];
        arr[minIndex] = temp;
    }

    for (int i = 0; i < 7; i++)
    {
        std::cout << arr[i] << ' ';
    }

    std::cout << '\n';

    return 0;
}
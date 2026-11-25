#include <iostream>

void print(int** arr,const int rows, const int cols)
{
    std::cout << std::endl;
    for(int i = 0;i < rows;i++)
    {
        for(int j = 0;j < cols;j++)
        {
            std::cout << arr[i][j] << ' ';
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}

int main()
{
    srand(time(NULL));
    int n,m;
    std::cin >> n;
    m = n;
    int** arr = new int*[n];
    for(int i = 0;i < n;i++)
    {
        arr[i] = new int[m]{};
    }

    for(int i = 0;i< n;i++)
    {
        for (int j = 0; j < m;j++)
        {
            arr[i][j] = rand() % 9 +1;
        }
    }

    print(arr,n,m);

    for(int i = 0;i< n;i++)
    {
        for (int j = 0; j < m;j++)
        {
            if (i == j) {arr[i][j] = 0;} // Главная диагональ
            if (i + j == n - 1) {arr[i][j] = 0;} // Побочная диагональ
        }

    }

    print(arr,n,m);

    for (int i = 0; i < n; i++) 
    {
        delete[] arr[i];
    }
    delete[] arr;

    return 0;
}
#include <iostream>

/*Написать процедуру для суммирования матриц.
 С ее помощью сложить исходную матрицу и транспонированную 
 (т. е. полученную поворотом исходной на 90 ).*/

void matrix_sum(int** m1,int** m2,int** res,const size_t size)
{

    for(int i = 0;i < size;i++)
    {
        for (int j = 0; j < size;j++)
        {
            res[i][j] = m1[i][j] + m2[i][j];
        }
    }
    
}

void transpl(int** arr,int** res,const size_t size)
{
    for(int i = 0;i < size;i++)
    {
        for(int j = 0; j < size;j++)
        {
            res[j][i] = arr[i][j];
        }
    }
}

void fill(int**& array,size_t size)
{
    for(int i = 0;i < size;i++)
    {
        for(int j = 0;j < size;j++)
        {
            array[i][j] = rand() % 99 + 1;
            std::cout << array[i][j] << ' ';
        }
        std::cout << std::endl;
    }
}

void out(int** arr,const size_t size)
{
    std::cout << "\n----------\n";
    for(int i = 0;i < size;i++)
    {
        for(int j = 0;j < size;j++)
        {
            std::cout << arr[i][j] << ' ';
        }
        std::cout << std::endl;
    }
    std::cout << "\n----------\n";
}

int main()
{
    srand(time(NULL));
    int n;
    std::cin >> n;
    int** matrix = new int*[n];
    int** trans = new int*[n];
    int** res = new int*[n];

    for(int i = 0;i < n;i++)
    {
        matrix[i] = new int[n];
        trans[i] = new int[n];
        res[i] = new int[n];
    }

    fill(matrix,n);

    transpl(matrix,trans,n);

    out(trans,n);

    matrix_sum(matrix,trans,res,n);

    out(res,n);


    for (int i = 0;i < n;i++)
    {
        delete[] matrix[i];
        delete[] trans[i];
        delete[] res[i];
    }

    delete[] matrix;
    delete[] trans;
    delete[] res;

    return 0;
}
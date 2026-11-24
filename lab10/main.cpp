#include <iostream>


void add(int*& arr,int& size,const int id,const int value)
{
    if (size < 1 || size < 0) return;
    
    int* tempArr = new int[size+1];

    bool deleted = false;
    for(int i = 0; i < size;i++)
    {
        if (i == id) {deleted = true; tempArr[i] = value;}

        if (deleted)
        {
            tempArr[i+1] = arr[i];
        }
        else
        {
            tempArr[i] = arr[i];
        }
    }

    delete[] arr;
    arr = tempArr;
    size++;
    tempArr = nullptr;
}

void remove(int*& arr,int& size,const int id)
{
    if (size < 1 || size < 0) return;

    int* tempArr = new int[size-1];

    bool deleted = false;
    for(int i = 0; i < size;i++)
    {
        if (i == id) {deleted = true; continue;}

        if (deleted)
        {
            tempArr[i-1] = arr[i];
        }
        else
        {
            tempArr[i] = arr[i];
        }
    }

    delete[] arr;
    arr = tempArr;
    size--;
    tempArr = nullptr;
}

void remove(int*& arr,int& size,const int startID,const int endID)
{
    if (size < 1 || size < 0) return;
    int counter = 0;

    int* tempArr = new int[size-(endID-startID)];

    bool deleted = false;
    for(int i = 0; i < size;i++)
    {
        if (i >= startID && i <= endID) {deleted = true; counter++; continue;}

        if (deleted)
        {
            tempArr[i-counter] = arr[i];
        }
        else
        {
            tempArr[i] = arr[i];
        }
    }

    delete[] arr;
    arr = tempArr;
    size-=(counter);
    tempArr = nullptr;
}

void print(const int* arr,const int size)
{

    for(int i = 0;i < size;i++)
    {
        std::cout << arr[i] << ' ';
    }
    std::cout << std::endl;
}

int main()
{
    srand(time(NULL));
    int n;
    int idDel;
    int addVal,addId;

    std::cin >> n;
    int* arr = new int[n]{};


    for(int i = 0;i < n;i++)
    {
        arr[i] = rand() % 10;
    }



    print(arr,n);

    std::cout << "\nID to delete: ";
    std::cin >> idDel;
    
    remove(arr,n,idDel,5);

    print(arr,n);

    std::cout << "value to add: ";
    std::cin >> addVal;

    std::cout << "ID to add: ";
    std::cin >> addId;

    add(arr,n,addId,addVal);

    print(arr,n);


    delete[] arr;

    return 0;
}
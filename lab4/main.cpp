#include <iostream>

int main()
{
    srand(time(NULL));
// 1,2)
    int N;
    std::cout << "Array size: ";
    std::cin >> N;
    const int size = N;
    int array[N];
    std::cout << "Basic array: ";
    for(int i = 0;i < N;i++)
    {
        array[i] = rand() % 5; // ЗАПОЛНЕНИЕ МАССИВА СЛУЧАЙНЫМИ ЧИСЛАМИ
        std::cout << array[i] << ' '; 
    }

    std::cout << std::endl;

    int counter = 0;
    bool hasOdd = false;

    for(auto& r : array)
    {
        if (r == 0)
        {
            counter += 1;
        }
        if (r % 2 == 0)
        {
            hasOdd = true;
        }
    }
    if (counter != size)
    {
        const int midSize = size-counter; // РАЗМЕР НОВОГО = РАЗМЕР СТАРОГО - КОЛ-ВО НУЛЕЙ
        int midArray[midSize];

        int freeElem = 0;
        // 3)
        for(int i = 0; i < size;i++)
        {
            if (array[i] != 0)
            {
                midArray[freeElem] = array[i];
                freeElem += 1;
            }
        }
        // 4)
        if (hasOdd)
        {
            int temp = 0;
            bool first = true;
            const int endSize = (hasOdd ? midSize + 1 : midSize); // РАЗМЕР НОВОГО = РАЗМЕР СТАРОГО +1 ЕСЛИ ЕСТЬ ЧЁТНОЕ, ИНАЧЕ ТАКОЙ ЖЕ

            int endArray[endSize];

            for (int i = 0; i < midSize;i++)
            {
                endArray[i+temp] = midArray[i];
                if (midArray[i] % 2 == 0 && first && i != 0)
                {
                    endArray[i+1] = endArray[i-1]+2;
                    first = false;
                    temp = 1;
                }
            }
            // 5)
            std::cout << "Array with new element & without zero: ";
            for(auto& r : endArray)
            {
                std::cout << r << ' ';
            }
        
        }
        else
        {
            std::cout << "Array with new element & without zero: ";
            for(auto& r : midArray)
            {
                std::cout << r << ' ';
            }
        }
    }
    else
    {
        std::cout << "\nAll elements = 0.\n";
    }
    return 0;
}
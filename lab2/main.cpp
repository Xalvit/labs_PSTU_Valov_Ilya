#include <iostream>

int main()
{
    int res = 0;
    for (size_t i = 0; i < 200;i++)
    {
        if (i % 2 != 0)
        {
            res += i;
        }
    }
    
    std::cout << res;

    return 0;
}

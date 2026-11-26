#include <iostream>
#include <cstdarg>

int sum(int count, ...)
{

    va_list args;
    va_start(args, count);

    int total_sum = 0;
    int prev = va_arg(args, int); 

    for (int i = 1; i < count; ++i) 
    {
        int current = va_arg(args, int); 
        total_sum += prev * current;
        prev = current; 
    }

    va_end(args);
    return total_sum;
}

int main() {
    std::cout << sum(4, 1, 2, 3, 4) << std::endl; 

    return 0;
}


#include <iostream>
#include <vector>
#include "yard.h"

int main()
{
    
    parser parse("100*10+2*(5+5)+47-1000");
    std::cout << parse.getParsed();
    return 0;

}
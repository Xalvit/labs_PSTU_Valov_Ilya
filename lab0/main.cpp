
#include <iostream>
#include <vector>
#include "yard.h"

int main()
{
    
    parser parse("100*2-4+9");
    std::cout << parse.getParsed();
    return 0;

}
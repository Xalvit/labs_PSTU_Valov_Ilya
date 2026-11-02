#include <iostream>
#include <cmath>


int main()
{

    float a = 0.1f;
    int b = 1;
    int k = 10;
    float step = (b-a)/k;

    long double y;
    long double SN = a;
    long double SE = 0;


    for (float x = a; x <= b;x += step)
    {
        y = sin(x);
        SN = a;
        for (int n = 1; n <= 10;n++)
        {
            SN += pow(-1,n)*(pow(x,2*n+1))/(tgamma(2*n+1 +1));
        }
        std::cout << "X: " << x<< " SN: " << SN << " SE: " << SE << " Y: " << y << std::endl;
    }
    
    return 0;
}
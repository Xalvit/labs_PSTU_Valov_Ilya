#include <iostream>
#include <complex>

std::complex<double> mult(std::complex<double> a,std::complex<double> b)
{
    return a*b;
}

int mult(int a,int b)
{
    return a*b;
}

int main()
{
    std::complex<double> a;
    std::complex<double> b;
    int c,d;
    std::cin >> a >> b;
    std::cout << mult(a,b);
    std::cout << std::endl;
    std::cin >> c >> d;
    std::cout << mult(c,d);

    return 0;
}
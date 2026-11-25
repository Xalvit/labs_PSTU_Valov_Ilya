#include <iostream>
#include <string>

struct Apartment
{
    int price;
    int floor;
    std::string street;
};


int main()
{
    Apartment v[3];
    for(auto & r : v)
    {
        std::cout << "Price: ";
        std::cin >> r.price;
        std::cout << "Floor: ";
        std::cin >> r.floor;
        std::cout << "Street: ";
        std::cin >> r.street;
        std::cout << "\n-------\n";
    }

    int t_price;
    std::cout << "ur price: ";
    std::cin >> t_price;

    for(auto& r : v)
    {
        if (r.price <= t_price)
        {
            std::cout << "Good choice:\n price: " << r.price << " floor: " << r.floor << " street: " << r.street;
            std::cout << std::endl; 
        }
    }


    return 0;
}
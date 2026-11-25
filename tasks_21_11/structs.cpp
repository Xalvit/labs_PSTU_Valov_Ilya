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
        std::cin >> v->price;
        std::cout << "Floor: ";
        std::cin >> v->floor;
        std::cout << "Street: ";
        std::cin >> v->street;
        std::cout << "\n-------\n";
    }

    int t_price;
    std::cout << "ur price: ";
    std::cin >> t_price;

    for(auto& r : v)
    {
        if (v->price <= t_price)
        {
            std::cout << "Good choice: price: " << v->price << " floor: " << v->floor << " street: " << v->street; 
        }
    }


    return 0;
}
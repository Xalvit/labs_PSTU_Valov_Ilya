#include <iostream>

inline const void Gets(std::string& text,const std::string& value)
{
    text = value;
}


int main()
{
    setlocale(LC_ALL,"Ru");
    std::string text;

    std::string odd = "aAeEuUyYoO";

    Gets(text,"afr kk bebeb  ffff uuuu kkk rurur bbbb.");

    std::string word = "";

    for(auto& r : text)
    {
        if(r != ' ' && r != '.')
        {
            word += r;
        }
        
        if (r == ' ' || r == '.')
        {
            for (auto& w : word)
            {
                if (odd.find(w) != std::string::npos)
                {
                    word = "";
                    break;
                }
            }
            
            if (!word.empty())
            {
                std::cout << word << ' ';
            }

            word = "";
        }
    }

    
    return 0;
}
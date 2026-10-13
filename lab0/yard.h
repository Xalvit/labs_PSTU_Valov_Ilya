

#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <stack>

class parser
{
private:
    double answer;
    std::string math;
    std::vector<std::string> tokens;
    const std::string nums = "0123456789";
    const std::string symbs = "-+/*()";

    double parseMult(double a,double b)
    {
        return a*b;
    }
    double parseDiv(double a,double b)
    {
        return a/b;
    }
    double parseSum(double a,double b)
    {
        return a+b;
    }
    double parseDis(double a,double b)
    {
        return a-b;
    }

    unsigned short priority(const std::string& symbol)
    {
        if (symbol == "-" || symbol == "+")
        {
            return 1;
        }
        if (symbol == "*" || symbol == "/")
        {
            return 2;
        }
        if (symbol == "(" || symbol == ")")
        {
            return 3;
        }
        return 0;
    }
    void clearString(const std::string& math)
    {
        std::string temp;
        for (int i = 0; i < math.size();i++)
        {
            if (nums.find(math.at(i)) != std::string::npos)
            {
                temp += math.at(i);
            }
            if (symbs.find(math.at(i)) != std::string::npos)
            {
                if (!temp.empty())
                    tokens.push_back(temp);

                tokens.push_back(std::string(1,math.at(i)));
                temp.clear();
            }

        }
        if (!temp.empty())
        {
            tokens.push_back(temp);
        }
    }

    std::vector<std::string> yard()
    {   
        std::vector<std::string> output;
        std::stack<std::string> ops;

        for (int i = 0; i < this->tokens.size();i++)
        {
            if (nums.find(tokens.at(i).at(0)) != std::string::npos)
            {
                output.push_back(tokens.at(i)); // ЕСЛИ ЧИСЛО СРАЗУ НА ВЫХОД
            }

            if (symbs.find(tokens.at(i)) != std::string::npos)
            {
                if (ops.empty() || tokens.at(i) == "(")
                {
                    ops.push(tokens.at(i)); // ЕСЛИ СТЕК ПУСТ ИЛИ СКОБКА ТО ПРОСТО ТОЛКАЕМ
                }
                else
                {
                    if (ops.top() == "(")
                    {
                        ops.push(tokens.at(i)); // КЛАДЕМ Т.К. У СКОБКИ НЕТ ПРИОРИТЕТА
                    }
                    else if (priority(ops.top()) >= priority(tokens.at(i)))
                    {
                    

                        // !!! ЕСЛИ УБРАТЬ *, ТО + - ОСТАЁТСЯ, А + ДОЛЖЕН ВЫТАЛКИВАТЬСЯ, СДЕЛАТЬ ПРОВЕРКУ
                        output.push_back(ops.top());
                        ops.pop(); // ЕСЛИ ПРИОРИТЕТ >= ТО ВЫТАЛКИВАЕМ ТОП В ВЫХОД
                        if (!ops.empty() && priority(ops.top()) >= priority(tokens.at(i)) && ops.top() != "(")
                        {
                            output.push_back(ops.top());
                            ops.pop();
                        }
                        ops.push(tokens.at(i));

                    }
                    else if (tokens.at(i) == ")")
                    {
                        while (ops.top() != "(")
                        {
                            output.push_back(ops.top()); 
                            ops.pop(); // ЕСЛИ ПРАВАЯ СКОБКА ТО ВСЁ ВЫТАЛКИВАЕМ ДО (
                        }
                        if (ops.top() == "(")
                        {
                            ops.pop();
                        }
                    }
                    else
                    {
                        ops.push(tokens.at(i));
                    }
                }
            }
        }


        while (!ops.empty())
        {
            output.push_back(ops.top());
            ops.pop();
        }
        return output;
    }

    std::stack<char> vecToStack(std::vector<char> out)
    {
        std::stack<char> temp;
        for (auto& r : out)
        {
            temp.push(r);
        }
        return temp;
    }

    double parse()
    {
        std::vector<std::string> output = yard();
        std::stack<double> ans;

        for (int i = 0; i < output.size();i++)
        {
            if (nums.find(output.at(i).at(0)) != std::string::npos)
            {
                ans.push(std::stod(output.at(i)));
            }
            else
            {
                if (output.at(i) == "*")
                {
                    double tempTop1 = ans.top();
                    ans.pop();
                    double tempTop2 = ans.top();
                    ans.pop();
                    ans.push(parseMult(tempTop2,tempTop1));
                }
                if (output.at(i) == "/")
                {
                    double tempTop1 = ans.top();
                    ans.pop();
                    double tempTop2 = ans.top();
                    ans.pop();
                    ans.push(parseDiv(tempTop2,tempTop1));
                }
                if (output.at(i) == "+")
                {
                    double tempTop1 = ans.top();
                    ans.pop();
                    double tempTop2 = ans.top();
                    ans.pop();
                    ans.push(parseSum(tempTop2,tempTop1));
                }
                if (output.at(i) == "-")
                {
                    double tempTop1 = ans.top();
                    ans.pop();
                    double tempTop2 = ans.top();
                    ans.pop();
                    ans.push(parseDis(tempTop2,tempTop1));
                }
            }
        }

        return ans.top();
    }

public:

    parser(std::string math)
    {
        this->math = math;
        this->clearString(this->math);
        this->parse();
    }

    double getParsed()
    {
        return this->parse();
    }

};
#include <iostream>
#include <vector>
#include <string>

const int NUM_DISKS = 5;
std::vector<int> towers[3];
int step_count = 0;

void drawTowers() {
    std::cout << "=== Шаг " << step_count << " ===\n\n";

    for (int level = NUM_DISKS - 1; level >= 0; --level) {
        for (int t = 0; t < 3; ++t) {
            int disk_size = 0;
            if (level < static_cast<int>(towers[t].size())) {
                disk_size = towers[t][level];
            }

            int spaces = NUM_DISKS - disk_size;
            std::string pad(spaces, ' ');
            std::string body = (disk_size == 0) ? "|" : std::string(disk_size * 2 + 1, '=');

            std::cout << " " << pad << body << pad << " ";
        }
        std::cout << '\n';
    }

    std::string base(NUM_DISKS * 2 + 1, '-');
    std::cout << " " << base << "  " << base << "  " << base << "\n";

    std::string label_pad(NUM_DISKS, ' ');
    std::cout << " " << label_pad << "A" << label_pad << "  "
              << label_pad << "B" << label_pad << "  "
              << label_pad << "C" << label_pad << "\n\n";
}


void hanoi(int n, int from, int to, int aux) {
    if (n == 0) return;

    hanoi(n - 1, from, aux, to);

    int disk = towers[from].back();
    towers[from].pop_back();
    towers[to].push_back(disk);
    
    step_count++;
    char names[3] = {'A', 'B', 'C'};
    std::cout << "Перенос кольца " << disk << ": " << names[from] << " -> " << names[to] << '\n';
    drawTowers();

    hanoi(n - 1, aux, to, from);
}

int main() {
    for (int i = NUM_DISKS; i >= 1; --i) {
        towers[0].push_back(i);
    }

    std::cout << "Начальное состояние:\n";
    drawTowers();

    hanoi(NUM_DISKS, 0, 2, 1);

    std::cout << "Готово! Всего выполнено шагов: " << step_count << '\n';
    return 0;
}

#include <iostream>
#include <vector>
#include <string>

const int NUM_DISKS = 5;
std::vector<int> towers[3]; // Три стержня: 0 (A), 1 (B), 2 (C)
int step_count = 0;

// Функция отрисовки текущего состояния всех башен
void drawTowers() {
    std::cout << "=== Шаг " << step_count << " ===\n\n";

    // Проходим по уровням сверху вниз
    for (int level = NUM_DISKS - 1; level >= 0; --level) {
        for (int t = 0; t < 3; ++t) {
            int disk_size = 0;
            if (level < static_cast<int>(towers[t].size())) {
                disk_size = towers[t][level];
            }

            // Формируем визуальное представление диска или пустого стержня
            int spaces = NUM_DISKS - disk_size;
            std::string pad(spaces, ' ');
            std::string body = (disk_size == 0) ? "|" : std::string(disk_size * 2 + 1, '=');

            std::cout << " " << pad << body << pad << " ";
        }
        std::cout << '\n';
    }

    // Отрисовка основания и подписей стержней
    std::string base(NUM_DISKS * 2 + 1, '-');
    std::cout << " " << base << "  " << base << "  " << base << "\n";

    std::string label_pad(NUM_DISKS, ' ');
    std::cout << " " << label_pad << "A" << label_pad << "  "
              << label_pad << "B" << label_pad << "  "
              << label_pad << "C" << label_pad << "\n\n";
}

// Рекурсивный алгоритм Ханойских башен
void hanoi(int n, int from, int to, int aux) {
    if (n == 0) return;

    // 1. Перекладываем n-1 колец на вспомогательный стержень
    hanoi(n - 1, from, aux, to);

    // 2. Перемещаем самое большое из текущих колец на целевой стержень
    int disk = towers[from].back();
    towers[from].pop_back();
    towers[to].push_back(disk);
    
    step_count++;
    char names[3] = {'A', 'B', 'C'};
    std::cout << "Перенос кольца " << disk << ": " << names[from] << " -> " << names[to] << '\n';
    drawTowers();

    // 3. Перекладываем n-1 колец со вспомогательного стержня на целевой
    hanoi(n - 1, aux, to, from);
}

int main() {
    // Заполняем первый стержень (A) кольцами от 5 (внизу) до 1 (вверху)
    for (int i = NUM_DISKS; i >= 1; --i) {
        towers[0].push_back(i);
    }

    std::cout << "Начальное состояние:\n";
    drawTowers();

    // Запускаем перенос 5 колец со стержня 0 (A) на стержень 2 (C) через 1 (B)
    hanoi(NUM_DISKS, 0, 2, 1);

    std::cout << "Готово! Всего выполнено шагов: " << step_count << '\n';
    return 0;
}

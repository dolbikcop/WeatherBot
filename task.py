# Дан неотсортированный массив целых чисел
# Найти минимальное положительное число, которого нет в массиве.
# Примеры:
# 10 -3 5 0 1 5 3 2 - ответ 4
# 0 3 2 1 4 - ответ 5

arr = list(map(int, input().split()))

min_val = 0
flag = True
while flag:
    min_val += 1

    flag = False
                        # В худшем случае - O(n^2)
    for i in arr:
        if i == min_val:
            flag = True
            break

print(min_val)

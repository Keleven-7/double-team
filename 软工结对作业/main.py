from flask import Flask, render_template
import random
import threading

app = Flask(__name__)

def is_valid(sudo, x, y, val):
    # 检查行冲突
    if val in sudo[y]:
        return False

    # 检查列冲突
    for i in range(9):
        if sudo[i][x] == val:
            return False

    # 检查宫格冲突
    subgrid_x = (x // 3) * 3
    subgrid_y = (y // 3) * 3
    for i in range(subgrid_y, subgrid_y + 3):
        for j in range(subgrid_x, subgrid_x + 3):
            if sudo[i][j] == val:
                return False

    return True

def fill_sudoku(lock):
    sudo = [[0] * 9 for _ in range(9)]

    def fill_from(y, val):
        nonlocal sudo

        for x in random.sample(range(9), 9):
            if sudo[y][x] == 0 and is_valid(sudo, x, y, val):
                sudo[y][x] = val

                if y == 8:
                    if val == 9:
                        return True
                    else:
                        if fill_from(0, val + 1):
                            return True
                else:
                    if fill_from(y + 1, val):
                        return True

                sudo[y][x] = 0

        return False

    lock.acquire()  # 获取锁
    if fill_from(0, 1):
        result = [row[:] for row in sudo]
    else:
        result = None
    lock.release()  # 释放锁

    return result


def dig_holes(sudo, lock, hole_cnt):
    idx = list(range(81))
    random.shuffle(idx)

    for i in range(hole_cnt):
        x = idx[i] % 9
        y = idx[i] // 9
        lock.acquire()  # 获取锁
        sudo[y][x] = 0
        lock.release()  # 释放锁


@app.route('/')
def home():
    sudokus = []
    lock = threading.Lock()

    def generate_sudoku(lock, result_list):
        sudo = fill_sudoku(lock)
        if sudo is not None:
            dig_holes(sudo, lock, 50)
            result_list.append(sudo)

    threads = []
    results = []
    for _ in range(9):
        t = threading.Thread(target=generate_sudoku, args=(lock, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return render_template('index.html', sudokus=results)

if __name__ == '__main__':
    app.run()


import multiprocessing
import time


# Функція для запуску обчислень з певною кількістю процесів
def execute_tests(numbers_range, proc_counts):
    for proc_count in proc_counts:
        print(f"\nЗапуск із {proc_count} процесами...")
        start = time.time()
        avg_steps, top_steps, top_number = parallel_collatz(numbers_range, proc_count)
        elapsed = time.time() - start
        print(f"Середня кількість кроків: {avg_steps:.2f}")
        print(f"Найбільше число: {top_number} із {top_steps} кроками")
        print(f"Час виконання: {elapsed:.2f} секунд")


# Паралельне обчислення кроків Коллатца
def parallel_collatz(max_num, process_count):
    task_q = multiprocessing.Queue()
    result_q = multiprocessing.Queue()

    # Додавання завдань у чергу
    for num in range(1, max_num + 1):
        task_q.put(num)

    # Створення процесів
    procs = []
    for _ in range(process_count):
        p = multiprocessing.Process(target=collatz_worker, args=(task_q, result_q))
        p.start()
        procs.append(p)

    # Завершення роботи процесів
    for _ in range(process_count):
        task_q.put(None)

    for p in procs:
        p.join()

    # Обробка результатів
    total_steps, total_count = 0, 0
    max_found_steps, max_found_number = 0, 1
    while not result_q.empty():
        steps_sum, count, max_steps, number = result_q.get()
        total_steps += steps_sum
        total_count += count
        if max_steps > max_found_steps:
            max_found_steps = max_steps
            max_found_number = number

    avg_steps = total_steps / total_count
    return avg_steps, max_found_steps, max_found_number


# Воркер-функція для виконання завдань
def collatz_worker(input_queue, output_queue):
    total_steps_local, max_steps_local, max_number_local = 0, 0, 0
    processed_count = 0

    while True:
        current_number = input_queue.get()
        if current_number is None:
            break

        steps = calculate_collatz_steps(current_number)
        total_steps_local += steps
        processed_count += 1

        if steps > max_steps_local:
            max_steps_local = steps
            max_number_local = current_number

    output_queue.put((total_steps_local, processed_count, max_steps_local, max_number_local))


# Розрахунок кількості кроків для числа
def calculate_collatz_steps(number):
    """
    Calculate the number of steps to reach 1
    based on the Collatz conjecture.

    Parameters:
    - number (int): Starting value of the Collatz sequence. Must be a positive integer.

    Returns:
    - steps (int): Total steps to reach 1.

    Raises:
    - ValueError: If the input is not a positive integer.
    """
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Input must be a positive integer.")

    steps = 0
    while number != 1:
        number = number // 2 if number % 2 == 0 else 3 * number + 1
        steps += 1
    return steps


if __name__ == "__main__":
    RANGE = 100000  # Діапазон чисел для обчислення
    PROCESSES = [1, 2, 10, 12, 50]  # Кількість процесів для тестування
    execute_tests(RANGE, PROCESSES)

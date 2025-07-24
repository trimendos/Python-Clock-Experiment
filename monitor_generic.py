import sys
import time
import subprocess
import psutil
import matplotlib.pyplot as plt
import os

def monitor_processes(executable_paths, duration=25):
    """
    Запускає довільну кількість .exe файлів, моніторить їхні ресурси 
    і будує порівняльний графік продуктивності.
    """
    if not executable_paths:
        print("Не передано жодного файлу для моніторингу.")
        return

    print(f"Запуск моніторингу на {duration} секунд для:")
    for path in executable_paths:
        print(f"- {path}")

    # --- Виправлення попередження Matplotlib ---
    # Старий виклик: plt.cm.get_cmap(...)
    # Новий, рекомендований виклик:
    try:
        # Для Matplotlib 3.7+
        colors = plt.colormaps.get_cmap('tab10').colors
    except AttributeError:
        # Для старих версій Matplotlib
        colors = plt.cm.get_cmap('tab10').colors
        
    linestyles = ['-', '--', '-.', ':'] * (len(executable_paths) // 4 + 1)

    all_data = {}

    # Головний цикл, що ітерується по кожному файлу послідовно
    for i, path in enumerate(executable_paths):
        name = os.path.basename(path).split('.')[0]
        all_data[name] = {'cpu': [], 'ram': [], 'threads': [], 'time': []}
        
        print("-" * 50)
        print(f"ПОЧАТОК ТЕСТУ для: {name}")
        print("-" * 50)
        
        proc = None
        try:
            # Запускаємо ОДИН процес
            proc = subprocess.Popen([path])
            p_obj = psutil.Process(proc.pid)
            print(f"Процес '{name}' запущено з PID: {p_obj.pid}. Очікування запуску...")
            # time.sleep(2) # Даємо додатку час на повний запуск та ініціалізацію

            start_time = time.time()
            
            # Внутрішній цикл моніторингу для поточного процесу
            while time.time() - start_time < duration:
                current_timestamp = time.time() - start_time
                
                try:
                    # Перший виклик cpu_percent після паузи дає коректні дані
                    cpu = p_obj.cpu_percent(interval=1.0) 
                    mem_info = p_obj.memory_info()
                    ram = mem_info.rss / (1024 * 1024) # Resident Set Size в МБ
                    num_threads = p_obj.num_threads()
                    
                    all_data[name]['cpu'].append(cpu)
                    all_data[name]['ram'].append(ram)
                    all_data[name]['threads'].append(num_threads)
                    all_data[name]['time'].append(current_timestamp)
                    
                    print(f"Час: {int(current_timestamp):>2}с | "
                        f"Пам'ять: {ram:>5.1f} МБ | "
                        f"ЦП: {cpu:>4.1f}% | "
                        f"Потоки: {num_threads:>2}")

                except psutil.NoSuchProcess:
                    print("Процес завершився раніше.")
                    break
        
        finally:
            # Гарантовано завершуємо процес після його тестування
            if proc and proc.poll() is None:
                print(f"Завершення процесу '{name}' (PID: {proc.pid})")
                proc.kill()
                proc.wait() # Чекаємо повного завершення
            print(f"ТЕСТ для {name} завершено. Пауза 2 секунди...")
            time.sleep(4) # Пауза між тестами для стабілізації системи

    # --- Побудова графіків ---
    print("-" * 50)
    print("Побудова фінального графіка...")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    fig.suptitle(f'Послідовне порівняння продуктивності ({len(executable_paths)} додатки)')

    for i, name in enumerate(all_data.keys()):
        if all_data[name]['time']:
            style_args = {'color': colors[i % len(colors)], 'linestyle': linestyles[i], 'label': name}
            
            # Графік ЦП
            ax1.plot(all_data[name]['time'], all_data[name]['cpu'], **style_args)
            
            # Графік Пам'яті
            ax2.plot(all_data[name]['time'], all_data[name]['ram'], **style_args)

            # Графік кількості потоків
            ax3.plot(all_data[name]['time'], all_data[name]['threads'], **style_args)

    ax1.set_ylabel('Навантаження на ЦП (%)')
    ax1.legend()
    ax1.grid(True)

    ax2.set_ylabel('Використання пам\'яті (МБ)')
    ax2.legend()
    ax2.grid(True)

    ax3.set_ylabel('Кількість потоків')
    ax3.set_xlabel('Час (секунди)')
    # Встановлюємо цілочисельні значення для осі Y
    ax3.yaxis.set_major_locator(plt.MaxNLocator(integer=True)) 
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig("sequential_performance_comparison.png")
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Будь ласка, вкажіть шляхи до одного або більше .exe файлів як аргументи.")
        print("Приклад: python monitor_generic.py C:\\app1.exe C:\\app2.exe")
    else:
        # Передаємо всі аргументи, крім імені самого скрипта
        monitor_processes(sys.argv[1:])
# python monitor_generic.py "build_thread\clock_thread.exe" "build_Qtimer\clock_qtimer.exe" "build_Qthreadpool\clock_qthreadpool.exe" "build_QThreadPoolExecutor\clock_threadpoolexecutor.exe"
# python monitor_generic.py "download_thread\download_thread.exe" "download_qtimer\download_qtimer_bad.exe" "download_QThreadPool\download_qthreadpool.exe" "download_ThreadPoolExecutor\download_executor.exe"
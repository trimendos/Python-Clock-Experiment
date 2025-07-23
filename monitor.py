import sys
import time
import subprocess
import psutil
import matplotlib.pyplot as plt

def monitor_processes(path1, path2, path3, path4, duration=30):
    """
    Запускає чотири .exe файли, моніторить їхні ресурси 
    і будує порівняльний графік продуктивності.
    """
    paths = {'thread': path1, 'qtimer': path2, 'qpool': path3, 'executor': path4}
    print("Запуск моніторингу для:")
    for name, path in paths.items():
        print(f"- {name}: {path}")

    # Словник для зберігання даних
    data = {name: {'cpu': [], 'ram': [], 'time': []} for name in paths.keys()}
    
    procs = {}
    ps_procs = {}

    try:
        # Запускаємо всі чотири процеси
        for name, path in paths.items():
            proc = subprocess.Popen([path])
            procs[name] = proc
            ps_procs[name] = psutil.Process(proc.pid)
            print(f"Процес '{name}' запущено з PID: {proc.pid}")

        start_time = time.time()
        
        while time.time() - start_time < duration:
            current_timestamp = time.time() - start_time
            # Робимо замір раз на секунду
            # cpu_percent потрібно викликати з інтервалом, щоб отримати коректні дані
            time.sleep(1.0) 

            # Збираємо дані для всіх активних процесів
            for name, p_obj in ps_procs.items():
                if p_obj and p_obj.is_running():
                    try:
                        data[name]['cpu'].append(p_obj.cpu_percent(interval=None))
                        data[name]['ram'].append(p_obj.memory_info().rss / (1024 * 1024)) # в МБ
                        data[name]['time'].append(current_timestamp)
                    except psutil.NoSuchProcess:
                        ps_procs[name] = None # Позначаємо процес як завершений

            # Перевірка, чи всі процеси завершились
            if not any(p.is_running() for p in ps_procs.values() if p is not None):
                print("Всі процеси завершились.")
                break

            # Виводимо поточний статус
            status_line = f"Час: {int(current_timestamp)}с | Пам'ять (МБ): "
            status_parts = []
            for name in paths.keys():
                if data[name]['ram']:
                    status_parts.append(f"{name}={data[name]['ram'][-1]:.2f}")
            status_line += " | ".join(status_parts)
            print(status_line)

    finally:
        # Завершуємо всі процеси, що могли залишитись
        for name, proc in procs.items():
            if proc and proc.poll() is None:
                print(f"Зупинка процесу '{name}' (PID: {proc.pid})")
                proc.kill()

    # --- Побудова графіків ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.suptitle('Порівняння продуктивності: 4 підходи до багатозадачності в PyQt')

    # Визначення стилів для кожного графіка для кращої читабельності
    styles = {
        'thread':   {'color': 'red',    'linestyle': '-',  'label': 'threading.Thread'},
        'qtimer':   {'color': 'blue',   'linestyle': '--', 'label': 'QTimer'},
        'qpool':    {'color': 'green',  'linestyle': '-.', 'label': 'QThreadPool'},
        'executor': {'color': 'purple', 'linestyle': ':',  'label': 'ThreadPoolExecutor'}
    }
    
    # Графік навантаження на ЦП
    for name, style in styles.items():
        if data[name]['time']:
            ax1.plot(data[name]['time'], data[name]['cpu'], **style)
    ax1.set_ylabel('Навантаження на ЦП (%)')
    ax1.legend()
    ax1.grid(True)
    
    # Графік використання пам'яті
    for name, style in styles.items():
        if data[name]['time']:
            ax2.plot(data[name]['time'], data[name]['ram'], **style)
    ax2.set_ylabel('Використання пам\'яті (МБ)')
    ax2.set_xlabel('Час (секунди)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig("performance_comparison_4way.png")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Будь ласка, вкажіть шляхи до ЧОТИРЬОХ .exe файлів.")
        print("Порядок: thread, qtimer, qpool, executor")
        print("Приклад: python monitor_all.py C:\\app1.exe C:\\app2.exe C:\\app3.exe C:\\app4.exe")
    else:
        monitor_processes(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
# python monitor.py "build_thread\clock_thread.exe" "build_Qtimer\clock_qtimer.exe" "build_Qthreadpool\clock_qthreadpool.exe" "build_QThreadPoolExecutor\clock_threadpoolexecutor.exe"
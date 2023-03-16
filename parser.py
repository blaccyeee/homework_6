import datetime
import subprocess

KILOBYTES_IN_MEGABYTE = 1024


def list_command(cmd, args):
    temp = subprocess.Popen([cmd, args], stdout=subprocess.PIPE)

    output = str(temp.communicate())

    output = output.split("\n")

    output = output[0].split('\\n')

    res = []

    for line in output:
        res.append(line)

    return res


def parse_ps_aux():
    total = {
        'users': {},
        'total_mem': 0,
        'total_cpu': 0,
        'max_mem_process': {
            'pid': -1,
            'name': '',
            'mem': -1.0,
        },
        'max_cpu_process': {
            'pid': -1,
            'name': '',
            'cpu': -1.0,
        },
        'total_processes': 0,
    }
    lines = list_command('ps', 'aux')
    for idx in range(1, len(lines) - 1):
        user, pid, cpu_percent, mem_percent, vsz, rss, tt, stat, started, time, *command = lines[idx].split()
        rss = float(rss)
        cpu_percent = float(cpu_percent)
        pid = int(pid)

        total['users'].setdefault(user, 0)
        total['users'][user] += 1
        total['total_mem'] += rss
        total['total_cpu'] += cpu_percent

        if total['max_mem_process']['mem'] < rss:
            total['max_mem_process']['pid'] = pid
            total['max_mem_process']['name'] = ' '.join(command)
            total['max_mem_process']['mem'] = rss

        if total['max_cpu_process']['cpu'] < cpu_percent:
            total['max_cpu_process']['pid'] = pid
            total['max_cpu_process']['name'] = ' '.join(command)
            total['max_cpu_process']['cpu'] = cpu_percent

    total['total_processes'] = len(lines) - 2
    return total


def get_ps_aux_and_save():
    total = parse_ps_aux()
    user_names = ', '.join(total["users"].keys())
    lines = [
        'Отчёт о состоянии системы:',
        f'Пользователи системы: {user_names}',
        f'Процессов запущено: {total["total_processes"]}',
        'Пользовательских процессов:',
    ]
    for user_name, processes in total['users'].items():
        lines.append(f'{user_name}: {processes}')

    lines.extend(
        [
            f'Всего памяти используется: {round(total["total_mem"] / KILOBYTES_IN_MEGABYTE, 1)} mb',
            f'Всего CPU используется: {round(total["total_cpu"], 1)}%',
            f'Больше всего памяти использует: {total["max_mem_process"]["name"][:20]}',
            f'Больше всего CPU использует: {total["max_cpu_process"]["name"][:20]}',
        ]
    )

    with open(f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}-scan.txt', 'w+') as f:
        for line in lines:
            f.write(f'{line}\n')


if __name__ == '__main__':
    get_ps_aux_and_save()

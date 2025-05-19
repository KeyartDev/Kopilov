import pandas as pd
import random

DATA_FILE = "data_input.txt"
OUTPUT_FILE = "timetable_output.txt"
DAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
TIMES = ['8:10-9:40', '9:50-11:20', '11:50-13:20', '13:30-15:00']

def load_data(filename):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден!")
        exit()

def create_empty_timetable(groups, days, times):
    timetable = {}
    for group in groups:
        timetable[group] = pd.DataFrame(index=times, columns=days)
    return timetable

def is_slot_available(timetable, group, day, time, teacher):
    if not pd.isna(timetable[group].loc[time, day]):
        return False

    # Check for teacher conflicts in other groups
    for g in timetable:
        if g != group and not pd.isna(timetable[g].loc[time, day]) and teacher in timetable[g].loc[time, day]:
            return False
    return True

def assign_lessons(timetable, data):
    lessons_assigned = {}
    for group in timetable:
        lessons_assigned[group] = {day: [] for day in DAYS}

    # Group data by group for more efficient processing
    grouped_data = data.groupby('Группа')

    for group, group_data in grouped_data:
        print(f"Составляем расписание для группы: {group}")
        
        # Try assigning lessons multiple times to fill more slots
        for attempt in range(5):  # Try 5 times
            print(f"Попытка {attempt + 1} для группы {group}")
            
            # Shuffle the lesson data for each attempt
            shuffled_data = group_data.sample(frac=1).reset_index(drop=True)

            for index, row in shuffled_data.iterrows():
                teacher = row['Учитель']
                subject = row['Предмет']

                available_days = DAYS[:]
                random.shuffle(available_days)

                assigned = False
                for day in available_days:
                    if subject in lessons_assigned[group][day]:
                        continue

                    available_times = TIMES[:]
                    random.shuffle(available_times)

                    # Try to find a slot with some "jitter"
                    for _ in range(3):
                        time = random.choice(available_times)
                        if is_slot_available(timetable, group, day, time, teacher):
                            timetable[group].loc[time, day] = f"{subject} ({teacher})"
                            lessons_assigned[group][day].append(subject)
                            print(f"Назначен урок: {subject} ({teacher}) для {group} в {day} {time}")
                            assigned = True
                            break

                    if assigned:
                        break

                if not assigned:
                    print(f"Не удалось назначить {subject} ({teacher}) для {group}")

    return timetable

def save_timetable(timetable_data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Расписание:\n\n")
        for group, timetable in timetable_data.items():
            f.write(f"Группа: {group}\n")
            f.write(timetable.to_string())
            f.write("\n\n")
    print(f"Расписание сохранено в файл: {filename}")


def main():
    data = load_data(DATA_FILE)
    print("Входные данные:\n", data.head())

    groups = data['Группа'].unique()
    timetable = create_empty_timetable(groups, DAYS, TIMES)
    timetable = assign_lessons(timetable, data)
    save_timetable(timetable, OUTPUT_FILE)
    print("Готово")


if __name__ == "__main__":
    main()

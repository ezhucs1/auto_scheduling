import random
import csv

# Staff
charge_persons = ['Jesse', 'Joe', 'Travis', 'Michelle', 'Fabian', 'Savanna', 'Dawn', 'Desiree']
full_time = ['Elizabeth', 'Evan', 'Shanice', 'Latreesha', 'Jeremy', 'Jonathan', 'Cory', 'Kierra', 'Leo']
all_employees = charge_persons + full_time

# Max shifts each week per employee
MAX_SHIFTS = 3

# Routine schedules (people who can only work on certain days)
routine_work_days = {
    'Evan': [1, 6, 7]
}

# Track shifts assigned per employee
shift_count = {employee: 0 for employee in all_employees}

# Generate schedule (arr[1] = Sunday)
days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

# Initialize schedule dictionary
schedule = {name: [name] + [''] * len(days) for name in all_employees}

# Assign routine schedule staff first
for employee, allowed_days in routine_work_days.items():
    for day in allowed_days:
        if shift_count[employee] < MAX_SHIFTS:
            if schedule[employee][day] == '':
                schedule[employee][day] = 'S'
                shift_count[employee] += 1

# Function to get available staff
def get_available_staff(staff_list, exclude=[], day_index=None):
    return [p for p in staff_list if shift_count[p] < MAX_SHIFTS and p not in exclude and (p not in routine_work_days or day_index + 1 in routine_work_days[p])]

# Assign remaining shifts
for i, day in enumerate(days):
    # Select 2 charge persons
    available_charges = get_available_staff(charge_persons, day_index=i)
    charge_selected = random.sample(available_charges, 2) if len(available_charges) >= 2 else available_charges

    # Select up to 6 others
    available_others = get_available_staff(all_employees, exclude=charge_selected, day_index=i)
    others_selected = random.sample(available_others, min(6, len(available_others)))

    # Update shift count
    for person in charge_selected:
        shift_count[person] += 1
        schedule[person][i + 1] = 'C1' if charge_selected.index(person) == 0 else 'C2'

    for person in others_selected:
        shift_count[person] += 1
        schedule[person][i + 1] = 'S'

# Save schedule to CSV
with open('weekly_schedule.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Name'] + [f'Day {i+1}' for i in range(len(days))])
    for row in schedule.values():
        writer.writerow(row)

# Read the schedule and count staff per day
staff_counts = [0] * len(days)
under_scheduled_days = []
under_scheduled_people = []

with open('weekly_schedule.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip header
    for row in reader:
        shifts_worked = 0
        for i in range(1, len(row)):
            if row[i]:  # Count non-empty slots
                staff_counts[i-1] += 1
                shifts_worked += 1
        if shifts_worked < MAX_SHIFTS:
            under_scheduled_people.append(row[0])

# Highlight columns where staff count is not 8
highlighted_schedule = []
with open('weekly_schedule.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)
    highlighted_schedule.append(header)
    for row in reader:
        new_row = [
            f'#{row[0]}#' if row[0] in under_scheduled_people else row[0]
        ] + [
            f'*{row[i]}*' if staff_counts[i-1] != 8 and row[i] else row[i] for i in range(1, len(row))
        ]
        highlighted_schedule.append(new_row)

# Save highlighted schedule
with open('highlighted_schedule.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(highlighted_schedule)

print("Highlighted schedule saved as 'highlighted_schedule.csv'")

# Auto Scheduling

## Auto Employee Scheduling System (working progress)

### Overview

This Python script automatically generates a weekly work schedule for employees, ensuring fair distribution of shifts while considering availability constraints. The system assigns charge persons and other employees while limiting the number of shifts per worker.

### Features

Automatic shift allocation: Assigns charge persons and other employees based on availability.

Routine schedules: Supports employees with fixed workdays.

Shift limits: Ensures no employee exceeds the maximum number of shifts per week.

Schedule validation: Identifies and highlights under-scheduled days and employees.

CSV output: Saves the generated schedule as weekly_schedule.csv and highlights issues in highlighted_schedule.csv.

### Installation

Prerequisites

Python 3.x

Required libraries: random, csv

Clone the Repository

******************************************************

For Google Colab:
```bash
!git clone https://github.com/eggrollqq/auto_scheduling.git
cd auto_scheduling
```

Usage

Run the script using:
```bash
!python auto_scheduling.py
```

******************************************************

### Output Files

weekly_schedule.csv: The generated weekly schedule.

highlighted_schedule.csv: The schedule with under-scheduled employees and days highlighted.

### Configuration

You can modify the following variables in the script to adjust scheduling:

charge_persons: List of employees eligible for charge positions.

full_time: List of other staff.

MAX_SHIFTS: Maximum shifts per employee per week.

routine_work_days: Predefined workdays for certain employees.

### License

MIT License

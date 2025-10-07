### Auto Scheduling

An intelligent scheduling system for hospital day/night shift staff that automatically creates fair and balanced 6-week schedules while respecting staff constraints, role requirements, and time-off requests.

### Features

Multi-Week Scheduling: Generates complete 6-week schedules (Sunday to Saturday)

Role-Based Assignments: Automatically assigns Charge Nurses, Backup Charge, and NICU/PICU specialists

Fairness Optimization: Balances workload across all staff members using fairness algorithms

Time-Off Management: Respects staff vacation and request-off dates

Constraint Enforcement: Ensures no staff works more than 3 days per week

Comprehensive Metrics: Provides detailed fairness analysis and workload distribution

### Key Constraints

Maximum 6 staff per shift

Maximum 3 shifts per week per staff member

Required roles each night:

  - Charge Nurse

  - Backup Charge Nurse

  - NICU/PICU Specialist

  - Regular staff to fill remaining slots (ER/ICUs trained)

Staff can only be assigned to roles they're trained for

Time-off requests are strictly honored

### Installation

```bash
git clone https://github.com/ezhucs1/auto_scheduling.git
cd auto_scheduling
pip install numpy
```

### Usage

```bash
from scheduler import NightShiftScheduler, create_sample_staff

# Initialize scheduler
scheduler = NightShiftScheduler()

# Create staff with their trained roles
staff = create_sample_staff()

# Set schedule start date
scheduler.set_schedule_start_date('2024-09-01')

# Add time-off requests
scheduler.add_request_off(1, '2024-09-10', '2024-09-12')  # Staff ID 1 off Sept 10-12

# Generate 6-week schedule
schedule = scheduler.schedule_multiple_weeks(staff, num_weeks=6)
```

### Algorithm

The scheduler uses a multi-phase approach:

Daily Assignment: Processes each day Sunday through Saturday

Role Priority: Assigns critical roles first (Charge → Backup → NICU → Regular)

Fairness Selection: Uses weighted scoring considering:

Current week workload

Long-term workload distribution

Staff qualifications

Constraint Validation: Ensures all business rules are satisfied

### Fairness Metrics

The system provides comprehensive fairness analysis:

Fairness Score: Higher values indicate better workload distribution

Standard Deviation: Measures consistency of days worked across staff

Individual Statistics: Per-staff breakdown of total days and weekly distribution

******************************************************
### Example Output
```python
=== SHIFT SCHEDULING (6 Weeks) ===

--- Week 1 Schedule ---
Sun: Staff [1, 2, 3, 4, 5, 6] - Roles: {'charge': 1, 'backup_charge': 1, 'nicu': 1, 'regular': 3}
Mon: Staff [7, 8, 9, 10, 11, 12] - Roles: {'charge': 1, 'backup_charge': 1, 'nicu': 1, 'regular': 3}
...

=== FAIRNESS METRICS ===
Fairness Score: 8.42 (higher is better)
Total Days - Mean: 15.0, Std Dev: 1.2
Total Days - Min: 13, Max: 16, Range: 3
```
******************************************************

### Customization

You can modify the scheduling parameters:

Change num_weeks for different schedule durations

Adjust fairness weights in _select_fair_staff method

Modify maximum days per week constraint (currently 3)

Add new role types as needed

### Requirements

Python 3.6+

numpy

datetime (standard library)

collections (standard library)

### Contributing

1. Fork the repository

2. Create a feature branch

3. Make your changes

4. Add tests if applicable

5. Submit a pull request

### License

MIT License - see LICENSE file for details

import random
from typing import List, Dict, Set
from collections import defaultdict, Counter
import numpy as np

class NightShiftScheduler:
    def __init__(self):
        self.schedule_weeks = {}
        self.fairness_metrics = {}
        self.request_off_dates = {}
        self.schedule_start_date = None
        
    def set_schedule_start_date(self, start_date: str):
        """Set the actual calendar start date (e.g., '2024-09-01')"""
        from datetime import datetime, timedelta
        self.schedule_start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    def add_request_off(self, staff_id: int, start_date: str, end_date: str):
        """Add request off for a staff member for a date range"""
        from datetime import datetime, timedelta
        
        if self.schedule_start_date is None:
            raise ValueError("Please set schedule start date first")
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if staff_id not in self.request_off_dates:
            self.request_off_dates[staff_id] = set()
        
        # Convert date range to schedule day numbers
        current_date = start_dt
        while current_date <= end_dt:
            days_diff = (current_date - self.schedule_start_date).days
            if 0 <= days_diff < 42:  # 6 weeks * 7 days
                schedule_day = days_diff + 1
                self.request_off_dates[staff_id].add(schedule_day)
            current_date += timedelta(days=1)
    
    def schedule_multiple_weeks(self, staff_list: List[Dict], num_weeks: int = 6) -> Dict:
        """
        Schedule staff for multiple weeks (Sunday=1 to Saturday=7)
        """
        all_schedules = {}
        staff_work_stats = {staff['id']: {'total_days': 0, 'week_counts': [0]*num_weeks} 
                          for staff in staff_list}
        
        for week in range(1, num_weeks + 1):
            print(f"Scheduling week {week}...")
            week_schedule = self._schedule_single_week(staff_list, staff_work_stats, week, num_weeks)
            all_schedules[week] = week_schedule
            
            # Update statistics
            for day in range(1, 8):
                for assignment in week_schedule[day]:
                    staff_id = assignment['id']
                    staff_work_stats[staff_id]['total_days'] += 1
                    staff_work_stats[staff_id]['week_counts'][week-1] += 1
        
        # Calculate fairness metrics
        self.fairness_metrics = self._calculate_fairness_metrics(staff_work_stats, num_weeks)
        
        return all_schedules
    
    def _schedule_single_week(self, staff_list: List[Dict], staff_work_stats: Dict, 
                            current_week: int, total_weeks: int) -> Dict:
        """
        Schedule a single week following all constraints
        """
        schedule = {day: [] for day in range(1, 8)}  # Sunday(1) to Saturday(7)
        staff_week_days = {staff['id']: 0 for staff in staff_list}
        
        # Schedule each day
        for day in range(1, 8):
            day_schedule = []
            available_staff = self._get_available_staff(staff_list, staff_work_stats, 
                                                      staff_week_days, day_schedule, 
                                                      current_week, total_weeks, day)
            
            # 1. Assign Charge Nurse
            charge_assigned = self._assign_role(available_staff, staff_work_stats, staff_week_days, 
                                              'charge', 'charge', day_schedule)
            if charge_assigned:
                staff_week_days[charge_assigned['id']] += 1
            
            # 2. Assign Backup Charge
            available_staff = self._get_available_staff(staff_list, staff_work_stats, 
                                                      staff_week_days, day_schedule, 
                                                      current_week, total_weeks, day)
            backup_assigned = self._assign_role(available_staff, staff_work_stats, staff_week_days, 
                                              'charge', 'backup_charge', day_schedule)
            if backup_assigned:
                staff_week_days[backup_assigned['id']] += 1
            
            # 3. Assign NICU/PICU Person
            available_staff = self._get_available_staff(staff_list, staff_work_stats, 
                                                      staff_week_days, day_schedule, 
                                                      current_week, total_weeks, day)
            nicu_assigned = self._assign_role(available_staff, staff_work_stats, staff_week_days, 
                                            'nicu', 'nicu', day_schedule)
            if nicu_assigned:
                staff_week_days[nicu_assigned['id']] += 1
            
            # 4. Fill remaining slots up to max 6
            available_staff = self._get_available_staff(staff_list, staff_work_stats, 
                                                      staff_week_days, day_schedule, 
                                                      current_week, total_weeks, day)
            remaining_slots = 6 - len(day_schedule)
            
            for _ in range(remaining_slots):
                if not available_staff:
                    break
                    
                # Use fairness-based selection
                regular_staff = self._select_fair_staff(available_staff, staff_work_stats, 
                                                      staff_week_days, current_week, total_weeks)
                day_schedule.append({'id': regular_staff['id'], 'role': 'regular'})
                staff_week_days[regular_staff['id']] += 1
                available_staff = self._get_available_staff(staff_list, staff_work_stats, 
                                                          staff_week_days, day_schedule, 
                                                          current_week, total_weeks, day)
            
            schedule[day] = day_schedule
        
        return schedule
    
    def _get_available_staff(self, staff_list: List[Dict], staff_work_stats: Dict, 
                           staff_week_days: Dict, current_day_schedule: List, 
                           current_week: int, total_weeks: int, current_day: int) -> List[Dict]:
        """
        Get staff available for assignment considering all constraints
        """
        scheduled_ids = {assignment['id'] for assignment in current_day_schedule}
        
        # Calculate absolute day number (1-42 for 6 weeks)
        absolute_day = (current_week - 1) * 7 + current_day
        
        available = []
        for staff in staff_list:
            staff_id = staff['id']
            
            # Check if staff is already scheduled today
            if staff_id in scheduled_ids:
                continue
            
            # Check max days per week constraint (3 days)
            if staff_week_days[staff_id] >= 3:
                continue
            
            # Check if staff requested off this day
            if staff_id in self.request_off_dates and absolute_day in self.request_off_dates[staff_id]:
                continue
            
            # Check long-term fairness (not working significantly more than others)
            if current_week > 1:
                avg_days_per_week = staff_work_stats[staff_id]['total_days'] / (current_week - 1)
                if avg_days_per_week > 3.2:  # Allow slight variation
                    continue
                
            available.append(staff)
        
        return available
    
    def _assign_role(self, candidates: List[Dict], staff_work_stats: Dict, 
                   staff_week_days: Dict, required_role: str, assignment_role: str, 
                   day_schedule: List) -> Dict:
        """
        Assign a specific role to the most appropriate candidate
        """
        role_candidates = [s for s in candidates if required_role in s['roles']]
        
        if not role_candidates:
            print(f"Warning: No {required_role} available!")
            return None
        
        selected = self._select_fair_staff(role_candidates, staff_work_stats, 
                                         staff_week_days, current_week=1, total_weeks=1)
        day_schedule.append({'id': selected['id'], 'role': assignment_role})
        return selected
    
    def _select_fair_staff(self, candidates: List[Dict], staff_work_stats: Dict, 
                         staff_week_days: Dict, current_week: int, total_weeks: int) -> Dict:
        """
        Select staff using fairness-weighted criteria
        """
        if len(candidates) == 1:
            return candidates[0]
        
        # Calculate fairness scores
        scores = []
        for staff in candidates:
            staff_id = staff['id']
            
            # Base score: inverse of days worked this week
            week_score = 1.0 / (staff_week_days[staff_id] + 0.1)
            
            # Long-term fairness: inverse of total days worked
            if current_week > 1:
                total_days = staff_work_stats[staff_id]['total_days']
                expected_days = (current_week - 1) * 2.5  # Target 2.5 days/week avg
                fairness_score = 1.0 / (abs(total_days - expected_days) + 1)
            else:
                fairness_score = 1.0
            
            # Combined score
            total_score = week_score * 0.6 + fairness_score * 0.4
            scores.append((staff, total_score))
        
        # Select staff with highest fairness score
        return max(scores, key=lambda x: x[1])[0]
    
    def _calculate_fairness_metrics(self, staff_work_stats: Dict, num_weeks: int) -> Dict:
        """
        Calculate comprehensive fairness metrics
        """
        total_days = [stats['total_days'] for stats in staff_work_stats.values()]
        
        metrics = {
            'total_days_distribution': {
                'mean': np.mean(total_days),
                'std_dev': np.std(total_days),
                'min': min(total_days),
                'max': max(total_days),
                'range': max(total_days) - min(total_days)
            },
            'fairness_score': 1.0 / (np.std(total_days) + 0.1),  # Higher is better
            'individual_stats': {
                staff_id: {
                    'total_days': stats['total_days'],
                    'avg_days_per_week': stats['total_days'] / num_weeks,
                    'weekly_distribution': stats['week_counts']
                }
                for staff_id, stats in staff_work_stats.items()
            }
        }
        
        return metrics

def create_sample_staff():
    """Create sample staff with trained areas"""
    return [
        {'id': 1, 'name': 'Alice', 'roles': ['charge', 'regular']},
        {'id': 2, 'name': 'Bob', 'roles': ['charge', 'nicu', 'regular']},
        {'id': 3, 'name': 'Charlie', 'roles': ['charge', 'regular']},
        {'id': 4, 'name': 'Diana', 'roles': ['nicu', 'regular']},
        {'id': 5, 'name': 'Eve', 'roles': ['nicu', 'regular']},
        {'id': 6, 'name': 'Frank', 'roles': ['regular']},
        {'id': 7, 'name': 'Grace', 'roles': ['regular']},
        {'id': 8, 'name': 'Henry', 'roles': ['charge', 'nicu', 'regular']},
        {'id': 9, 'name': 'Ivy', 'roles': ['regular']},
        {'id': 10, 'name': 'Jack', 'roles': ['charge', 'nicu', 'regular']},
        {'id': 11, 'name': 'Lee', 'roles': ['nicu', 'regular']},
        {'id': 12, 'name': 'Anderson', 'roles': ['charge', 'nicu', 'regular']},
        {'id': 13, 'name': 'Wang', 'roles': ['charge', 'nicu', 'regular']},
        {'id': 14, 'name': 'Park', 'roles': ['charge', 'nicu', 'regular']},
    ]

def run_scheduling():
    scheduler = NightShiftScheduler()
    staff = create_sample_staff()
    
    # Set start date and add some request off
    scheduler.set_schedule_start_date('2024-09-22')
    scheduler.add_request_off(1, '2024-09-24', '2024-09-26')  # Alice off Sept 24-26
    
    print("=== NIGHT SHIFT SCHEDULING (6 Weeks) ===\n")
    
    # Schedule 6 weeks
    schedule = scheduler.schedule_multiple_weeks(staff, num_weeks=6)
    
    # Display schedule
    for week in range(1, 7):
        print(f"\n--- Week {week} Schedule ---")
        for day in range(1, 8):
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            day_name = day_names[day-1]
            assignments = schedule[week][day]
            role_counts = Counter([a['role'] for a in assignments])
            staff_ids = [a['id'] for a in assignments]
            print(f"{day_name}: Staff {staff_ids} - Roles: {dict(role_counts)}")
    
    # Display fairness metrics
    print("\n=== FAIRNESS METRICS ===")
    metrics = scheduler.fairness_metrics
    dist = metrics['total_days_distribution']
    
    print(f"Fairness Score: {metrics['fairness_score']:.2f} (higher is better)")
    print(f"Total Days - Mean: {dist['mean']:.1f}, Std Dev: {dist['std_dev']:.1f}")
    print(f"Total Days - Min: {dist['min']}, Max: {dist['max']}, Range: {dist['range']}")
    
    print("\nIndividual Staff Statistics:")
    for staff_id, stats in metrics['individual_stats'].items():
        print(f"Staff {staff_id}: {stats['total_days']} total days ({stats['avg_days_per_week']:.1f}/week)")

# Run the scheduling
if __name__ == "__main__":
    run_scheduling()

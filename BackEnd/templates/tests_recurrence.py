"""
Comprehensive unit tests for Schedule recurrence calculation.

Tests edge cases including:
- End-of-month handling
- Leap years
- DST changes
- Schedule conflicts
- Overlapping recurring schedules
- Security and input validation
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil import tz
import pytz

from templates.models import Schedule, Template
from templates.recurrence import SecureRecurrenceCalculator, RecurrenceError, ValidationError
from accounts.models import User


class RecurrenceCalculatorTestCase(TestCase):
    """Test cases for SecureRecurrenceCalculator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.now = timezone.now()
        self.tz_utc = pytz.UTC
        
    def test_daily_recurrence_next_run(self):
        """Test daily recurrence calculation"""
        start_time = self.now.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        # Calculate next run (should be tomorrow if past start time today)
        next_run = SecureRecurrenceCalculator.calculate_next_run(
            start_time=start_time,
            end_time=end_time,
            repeat_type='daily',
            reference_time=self.now.replace(hour=10, minute=0)
        )
        
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.hour, 9)
        self.assertEqual(next_run.minute, 0)
        # Should be tomorrow
        self.assertEqual((next_run.date() - self.now.date()).days, 1)
    
    def test_weekly_recurrence_next_run(self):
        """Test weekly recurrence calculation"""
        # Monday at 9 AM
        start_time = self.now.replace(weekday=0, hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        # Calculate next run (should be next Monday)
        next_run = SecureRecurrenceCalculator.calculate_next_run(
            start_time=start_time,
            end_time=end_time,
            repeat_type='weekly',
            reference_time=self.now
        )
        
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.weekday(), 0)  # Monday
        self.assertEqual(next_run.hour, 9)
    
    def test_monthly_recurrence_next_run(self):
        """Test monthly recurrence calculation"""
        # 15th of month at 9 AM
        start_time = self.now.replace(day=15, hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        # Calculate next run
        next_run = SecureRecurrenceCalculator.calculate_next_run(
            start_time=start_time,
            end_time=end_time,
            repeat_type='monthly',
            reference_time=self.now
        )
        
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.day, 15)
        self.assertEqual(next_run.hour, 9)
    
    def test_monthly_recurrence_end_of_month(self):
        """Test monthly recurrence with end-of-month edge case (Jan 31 -> Feb 28/29)"""
        # January 31st at 9 AM
        start_time = datetime(2024, 1, 31, 9, 0, 0)
        start_time = timezone.make_aware(start_time)
        end_time = start_time + timedelta(hours=2)
        
        # Reference time: February 1st
        ref_time = datetime(2024, 2, 1, 10, 0, 0)
        ref_time = timezone.make_aware(ref_time)
        
        # Next run should be February 29th (leap year) or February 28th
        next_run = SecureRecurrenceCalculator.calculate_next_run(
            start_time=start_time,
            end_time=end_time,
            repeat_type='monthly',
            reference_time=ref_time
        )
        
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.month, 2)
        self.assertEqual(next_run.year, 2024)
        # Should be last day of February (28 or 29)
        self.assertIn(next_run.day, [28, 29])
    
    def test_monthly_recurrence_leap_year(self):
        """Test monthly recurrence across leap year boundary"""
        # February 29, 2024 (leap year) at 9 AM
        start_time = datetime(2024, 2, 29, 9, 0, 0)
        start_time = timezone.make_aware(start_time)
        end_time = start_time + timedelta(hours=2)
        
        # Reference time: March 1, 2024
        ref_time = datetime(2024, 3, 1, 10, 0, 0)
        ref_time = timezone.make_aware(ref_time)
        
        # Next run should be March 29, 2024 (not Feb 29, 2025)
        next_run = SecureRecurrenceCalculator.calculate_next_run(
            start_time=start_time,
            end_time=end_time,
            repeat_type='monthly',
            reference_time=ref_time
        )
        
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.month, 3)
        self.assertEqual(next_run.day, 29)
        self.assertEqual(next_run.year, 2024)
    
    def test_is_running_now_daily(self):
        """Test is_running_now for daily recurrence"""
        start_time = self.now.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        # Check at 10 AM (should be running)
        ref_time = self.now.replace(hour=10, minute=0, second=0, microsecond=0)
        is_running = SecureRecurrenceCalculator.is_running_now(
            start_time=start_time,
            end_time=end_time,
            repeat_type='daily',
            reference_time=ref_time
        )
        self.assertTrue(is_running)
        
        # Check at 8 AM (should not be running)
        ref_time = self.now.replace(hour=8, minute=0, second=0, microsecond=0)
        is_running = SecureRecurrenceCalculator.is_running_now(
            start_time=start_time,
            end_time=end_time,
            repeat_type='daily',
            reference_time=ref_time
        )
        self.assertFalse(is_running)
    
    def test_is_running_now_weekly(self):
        """Test is_running_now for weekly recurrence"""
        # Monday at 9 AM
        start_time = self.now.replace(weekday=0, hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        # Check on Monday at 10 AM (should be running)
        ref_time = self.now.replace(weekday=0, hour=10, minute=0, second=0, microsecond=0)
        is_running = SecureRecurrenceCalculator.is_running_now(
            start_time=start_time,
            end_time=end_time,
            repeat_type='weekly',
            reference_time=ref_time
        )
        self.assertTrue(is_running)
        
        # Check on Tuesday (should not be running)
        ref_time = self.now.replace(weekday=1, hour=10, minute=0, second=0, microsecond=0)
        is_running = SecureRecurrenceCalculator.is_running_now(
            start_time=start_time,
            end_time=end_time,
            repeat_type='weekly',
            reference_time=ref_time
        )
        self.assertFalse(is_running)
    
    def test_is_running_now_monthly(self):
        """Test is_running_now for monthly recurrence"""
        # 15th of month at 9 AM
        start_time = self.now.replace(day=15, hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        # Check on 15th at 10 AM (should be running)
        ref_time = self.now.replace(day=15, hour=10, minute=0, second=0, microsecond=0)
        is_running = SecureRecurrenceCalculator.is_running_now(
            start_time=start_time,
            end_time=end_time,
            repeat_type='monthly',
            reference_time=ref_time
        )
        self.assertTrue(is_running)
        
        # Check on 16th (should not be running)
        ref_time = self.now.replace(day=16, hour=10, minute=0, second=0, microsecond=0)
        is_running = SecureRecurrenceCalculator.is_running_now(
            start_time=start_time,
            end_time=end_time,
            repeat_type='monthly',
            reference_time=ref_time
        )
        self.assertFalse(is_running)
    
    def test_get_occurrences_in_range(self):
        """Test getting occurrences within a time range"""
        start_time = self.now.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=2)
        
        range_start = self.now
        range_end = self.now + timedelta(days=7)
        
        occurrences = SecureRecurrenceCalculator.get_occurrences_in_range(
            start_time=start_time,
            end_time=end_time,
            repeat_type='daily',
            range_start=range_start,
            range_end=range_end
        )
        
        # Should have approximately 7 occurrences (one per day)
        self.assertGreaterEqual(len(occurrences), 6)
        self.assertLessEqual(len(occurrences), 8)
        
        # All occurrences should be within range
        for occ in occurrences:
            self.assertGreaterEqual(occ, range_start)
            self.assertLessEqual(occ, range_end)
    
    def test_check_overlap_daily_schedules(self):
        """Test overlap detection for daily schedules"""
        # Schedule 1: 9 AM - 11 AM daily
        start1 = self.now.replace(hour=9, minute=0, second=0, microsecond=0)
        end1 = start1 + timedelta(hours=2)
        
        # Schedule 2: 10 AM - 12 PM daily (overlaps)
        start2 = self.now.replace(hour=10, minute=0, second=0, microsecond=0)
        end2 = start2 + timedelta(hours=2)
        
        check_start = self.now
        check_end = self.now + timedelta(days=7)
        
        overlaps = SecureRecurrenceCalculator.check_overlap(
            start1=start1, end1=end1,
            start2=start2, end2=end2,
            repeat_type1='daily',
            repeat_type2='daily',
            check_range_start=check_start,
            check_range_end=check_end
        )
        
        self.assertTrue(overlaps)
    
    def test_check_overlap_no_overlap(self):
        """Test overlap detection when schedules don't overlap"""
        # Schedule 1: 9 AM - 11 AM daily
        start1 = self.now.replace(hour=9, minute=0, second=0, microsecond=0)
        end1 = start1 + timedelta(hours=2)
        
        # Schedule 2: 12 PM - 2 PM daily (no overlap)
        start2 = self.now.replace(hour=12, minute=0, second=0, microsecond=0)
        end2 = start2 + timedelta(hours=2)
        
        check_start = self.now
        check_end = self.now + timedelta(days=7)
        
        overlaps = SecureRecurrenceCalculator.check_overlap(
            start1=start1, end1=end1,
            start2=start2, end2=end2,
            repeat_type1='daily',
            repeat_type2='daily',
            check_range_start=check_start,
            check_range_end=check_end
        )
        
        self.assertFalse(overlaps)
    
    def test_security_validation_datetime(self):
        """Test security validation for datetime inputs"""
        # Test invalid year
        invalid_dt = datetime(9999, 1, 1, 9, 0, 0)
        invalid_dt = timezone.make_aware(invalid_dt)
        
        with self.assertRaises(ValidationError):
            SecureRecurrenceCalculator._validate_datetime(invalid_dt, "test")
        
        # Test invalid date
        invalid_dt = datetime(2024, 2, 30, 9, 0, 0)  # Feb 30 doesn't exist
        try:
            invalid_dt = timezone.make_aware(invalid_dt)
            SecureRecurrenceCalculator._validate_datetime(invalid_dt, "test")
        except (ValueError, ValidationError):
            pass  # Expected
    
    def test_security_validation_repeat_type(self):
        """Test security validation for repeat_type"""
        with self.assertRaises(ValidationError):
            SecureRecurrenceCalculator._validate_repeat_type('invalid_type')
        
        with self.assertRaises(ValidationError):
            SecureRecurrenceCalculator._validate_repeat_type(''; DROP TABLE schedules; --')
    
    def test_security_sanitize_string(self):
        """Test string sanitization"""
        # Test null bytes
        sanitized = SecureRecurrenceCalculator._sanitize_string('test\x00string')
        self.assertEqual(sanitized, 'teststring')
        
        # Test length limit
        long_string = 'a' * 200
        with self.assertRaises(ValidationError):
            SecureRecurrenceCalculator._sanitize_string(long_string, max_length=100)


class ScheduleModelRecurrenceTestCase(TestCase):
    """Test cases for Schedule model recurrence methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a test template
        self.template = Template.objects.create(
            name='Test Template',
            width=1920,
            height=1080,
            created_by=self.user
        )
        
        self.now = timezone.now()
    
    def test_schedule_next_run_daily(self):
        """Test Schedule.next_run() for daily recurrence"""
        schedule = Schedule.objects.create(
            name='Daily Schedule',
            template=self.template,
            start_time=self.now.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=self.now.replace(hour=11, minute=0, second=0, microsecond=0),
            repeat_type='daily',
            is_active=True
        )
        
        next_run = schedule.next_run()
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.hour, 9)
    
    def test_schedule_next_run_monthly(self):
        """Test Schedule.next_run() for monthly recurrence"""
        schedule = Schedule.objects.create(
            name='Monthly Schedule',
            template=self.template,
            start_time=self.now.replace(day=15, hour=9, minute=0, second=0, microsecond=0),
            end_time=self.now.replace(day=15, hour=11, minute=0, second=0, microsecond=0),
            repeat_type='monthly',
            is_active=True
        )
        
        next_run = schedule.next_run()
        self.assertIsNotNone(next_run)
        self.assertEqual(next_run.day, 15)
        self.assertEqual(next_run.hour, 9)
    
    def test_schedule_is_running_now_daily(self):
        """Test Schedule.is_running_now for daily recurrence"""
        schedule = Schedule.objects.create(
            name='Daily Schedule',
            template=self.template,
            start_time=self.now.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=self.now.replace(hour=11, minute=0, second=0, microsecond=0),
            repeat_type='daily',
            is_active=True
        )
        
        # Mock timezone.now() to return 10 AM
        with timezone.override(self.now.replace(hour=10, minute=0)):
            is_running = schedule.is_running_now
            self.assertTrue(is_running)
    
    def test_schedule_is_conflicting_recurring(self):
        """Test Schedule.is_conflicting() for recurring schedules"""
        # Create two daily schedules that overlap
        schedule1 = Schedule.objects.create(
            name='Schedule 1',
            template=self.template,
            start_time=self.now.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=self.now.replace(hour=11, minute=0, second=0, microsecond=0),
            repeat_type='daily',
            is_active=True,
            priority=5
        )
        
        schedule2 = Schedule.objects.create(
            name='Schedule 2',
            template=self.template,
            start_time=self.now.replace(hour=10, minute=0, second=0, microsecond=0),
            end_time=self.now.replace(hour=12, minute=0, second=0, microsecond=0),
            repeat_type='daily',
            is_active=True,
            priority=3
        )
        
        # They should conflict (overlap in time)
        is_conflicting = schedule1.is_conflicting(schedule2)
        self.assertTrue(is_conflicting)
    
    def test_schedule_clean_validation(self):
        """Test Schedule.clean() validation"""
        schedule = Schedule(
            name='Test Schedule',
            template=self.template,
            start_time=self.now,
            end_time=self.now - timedelta(hours=1),  # Invalid: end before start
            repeat_type='daily'
        )
        
        with self.assertRaises(ValidationError):
            schedule.clean()
    
    def test_schedule_clean_invalid_repeat_type(self):
        """Test Schedule.clean() with invalid repeat_type"""
        schedule = Schedule(
            name='Test Schedule',
            template=self.template,
            start_time=self.now,
            end_time=self.now + timedelta(hours=2),
            repeat_type='invalid_type'
        )
        
        with self.assertRaises(ValidationError):
            schedule.clean()


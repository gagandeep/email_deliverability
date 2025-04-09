"""IP warming tools to gradually build sender reputation."""
from datetime import datetime, timedelta
import math


class IPWarmingScheduler:
    def __init__(self, daily_target=None, warmup_days=30, start_date=None):
        """
        Initialize IP warming scheduler.
        
        Args:
            daily_target (int): Target daily email volume
            warmup_days (int): Number of days for warmup
            start_date (datetime): Date to start warming
        """
        self.daily_target = daily_target
        self.warmup_days = warmup_days
        self.start_date = start_date or datetime.now()
        
    def generate_schedule(self):
        """
        Generate an IP warming schedule.
        
        Returns:
            list: Daily sending volumes for warming period
        """
        if not self.daily_target:
            raise ValueError("Daily target volume must be set")
        
        schedule = []
        
        # Calculate starting volume (typically around 50-100 emails)
        start_volume = min(100, max(50, int(self.daily_target * 0.01)))
        
        # Use logarithmic growth for a smooth ramp-up
        for day in range(1, self.warmup_days + 1):
            # Calculate progress factor (0 to 1)
            progress = day / self.warmup_days
            
            # Calculate daily volume using logarithmic growth
            # This gives slower growth at the beginning and faster at the end
            if day == self.warmup_days:
                daily_volume = self.daily_target  # Ensure the last day hits target
            else:
                log_factor = math.log10(day * 9 + 1) / math.log10(self.warmup_days * 9 + 1)
                daily_volume = start_volume + (self.daily_target - start_volume) * log_factor
            
            daily_volume = int(daily_volume)
            
            # Calculate the date for this step
            current_date = self.start_date + timedelta(days=day-1)
            
            schedule.append({
                "day": day,
                "date": current_date.strftime('%Y-%m-%d'),
                "volume": daily_volume,
                "percent_of_target": round(daily_volume / self.daily_target * 100, 1)
            })
        
        return schedule
    
    def distribute_volume_by_hour(self, daily_volume):
        """
        Distribute a daily volume across 24 hours following best practices.
        
        Args:
            daily_volume (int): Total emails to send in a day
            
        Returns:
            dict: Hourly distribution of email volume
        """
        # Define the distribution pattern (percentage of daily total by hour)
        # This follows a common pattern of avoiding sending during overnight hours
        # and concentrating sends during business hours
        hourly_distribution = {
            0: 1, 1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5, 5: 1,
            6: 2, 7: 4, 8: 6, 9: 8, 10: 10, 11: 9,
            12: 7, 13: 7, 14: 8, 15: 9, 16: 8, 17: 6,
            18: 4, 19: 3, 20: 3, 21: 2, 22: 1, 23: 1
        }
        
        # Normalize the distribution (ensure it sums to 100%)
        total_percentage = sum(hourly_distribution.values())
        normalized_distribution = {
            hour: (percentage / total_percentage) * 100
            for hour, percentage in hourly_distribution.items()
        }
        
        # Calculate hourly volumes based on the distribution
        hourly_volumes = {}
        remaining_volume = daily_volume
        
        for hour, percentage in normalized_distribution.items():
            if hour < 23:  # Distribute all hours except the last
                hourly_volume = int(daily_volume * percentage / 100)
                hourly_volumes[hour] = hourly_volume
                remaining_volume -= hourly_volume
            else:
                # Assign all remaining volume to the last hour to avoid rounding errors
                hourly_volumes[hour] = remaining_volume
        
        return hourly_volumes
        
    def warm_multiple_ips(self, ip_count, daily_target):
        """
        Create warming schedules for multiple IPs.
        
        Args:
            ip_count (int): Number of IPs to warm up
            daily_target (int): Total target volume across all IPs
            
        Returns:
            dict: Schedule for each IP
        """
        ip_target = daily_target // ip_count
        schedules = {}
        
        for i in range(1, ip_count + 1):
            ip_scheduler = IPWarmingScheduler(
                daily_target=ip_target,
                warmup_days=self.warmup_days,
                start_date=self.start_date
            )
            
            schedules[f"ip_{i}"] = ip_scheduler.generate_schedule()
        
        return schedules
    
    def get_recommendations(self):
        """
        Get best practice recommendations for IP warming.
        
        Returns:
            list: IP warming recommendations
        """
        recommendations = [
            "Monitor bounce rates daily. Keep them under 3%.",
            "Segment your list and start with most engaged subscribers.",
            "Maintain consistent sending patterns (similar times each day).",
            "Send relevant, engaging content during the warming period.",
            "Monitor inbox placement with seed testing.",
            "If bounce rates increase, slow down the warming schedule.",
            "Set up proper authentication (SPF, DKIM, DMARC) before warming.",
            "Respond quickly to feedback loop complaints.",
            "Gradually increase both volume and frequency."
        ]
        
        return recommendations
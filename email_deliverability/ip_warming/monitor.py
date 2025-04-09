"""Monitor IP warming progress and performance."""
from datetime import datetime, timedelta
import csv
import io
import json
from ..reputation.monitor import ReputationMonitor


class WarmingMonitor:
    def __init__(self, target_volume=None, start_date=None):
        """
        Initialize IP warming monitor.
        
        Args:
            target_volume (int): Target daily volume
            start_date (datetime): Start date of warming
        """
        self.target_volume = target_volume
        self.start_date = start_date or datetime.now()
        self.reputation_monitor = ReputationMonitor()
        
    def load_plan(self, warming_plan):
        """
        Load an IP warming plan.
        
        Args:
            warming_plan (dict): IP warming plan
            
        Returns:
            bool: Success status
        """
        if not warming_plan or "schedule" not in warming_plan:
            return False
            
        self.target_volume = warming_plan.get("daily_target")
        schedule = warming_plan.get("schedule", [])
        
        if schedule and "date" in schedule[0]:
            try:
                self.start_date = datetime.strptime(schedule[0]["date"], '%Y-%m-%d')
            except ValueError:
                pass
                
        return True
    
    def track_progress(self, sent_volumes):
        """
        Track warming progress against the plan.
        
        Args:
            sent_volumes (list): List of (date, volume) tuples
            
        Returns:
            dict: Progress report
        """
        if not self.target_volume:
            return {"error": "No target volume defined"}
            
        if not sent_volumes:
            return {"error": "No sending data provided"}
            
        # Calculate days since start
        today = datetime.now()
        days_since_start = (today - self.start_date).days
        
        # Convert sent_volumes to a dictionary for easy lookup
        volume_by_date = {}
        for date_str, volume in sent_volumes:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                volume_by_date[date] = volume
            except ValueError:
                continue
        
        # Calculate expected volumes
        expected_volumes = {}
        actual_volumes = {}
        adherence = {}
        
        current_date = self.start_date.date()
        end_date = min(today.date(), self.start_date.date() + timedelta(days=30))
        
        while current_date <= end_date:
            day_num = (current_date - self.start_date.date()).days + 1
            
            # Calculate expected volume for this day (simplified formula)
            if day_num > 30:
                expected_vol = self.target_volume
            else:
                progress_factor = day_num / 30
                expected_vol = int(self.target_volume * progress_factor)
            
            expected_volumes[current_date] = expected_vol
            
            # Get actual volume
            actual_vol = volume_by_date.get(current_date, 0)
            actual_volumes[current_date] = actual_vol
            
            # Calculate adherence (actual/expected)
            if expected_vol > 0:
                adherence[current_date] = min(actual_vol / expected_vol, 1.0)
            else:
                adherence[current_date] = 1.0 if actual_vol == 0 else 0.0
                
            current_date += timedelta(days=1)
        
        # Calculate overall adherence
        total_expected = sum(expected_volumes.values())
        total_actual = sum(actual_volumes.values())
        overall_adherence = total_actual / total_expected if total_expected > 0 else 0
        
        # Format for response
        formatted_expected = [
            {"date": date.strftime('%Y-%m-%d'), "volume": vol}
            for date, vol in expected_volumes.items()
        ]
        
        formatted_actual = [
            {"date": date.strftime('%Y-%m-%d'), "volume": vol}
            for date, vol in actual_volumes.items()
        ]
        
        formatted_adherence = [
            {"date": date.strftime('%Y-%m-%d'), "adherence": round(adh * 100, 1)}
            for date, adh in adherence.items()
        ]
        
        return {
            "days_since_start": days_since_start,
            "total_expected": total_expected,
            "total_sent": total_actual,
            "overall_adherence": round(overall_adherence * 100, 1),
            "expected_volumes": formatted_expected,
            "actual_volumes": formatted_actual,
            "adherence": formatted_adherence,
            "status": self._determine_status(overall_adherence)
        }
    
    def _determine_status(self, adherence):
        """Determine warming status based on adherence."""
        if adherence >= 0.95:
            return "on_track"
        elif adherence >= 0.8:
            return "slightly_behind"
        elif adherence >= 0.5:
            return "behind"
        else:
            return "critical"
    
    def monitor_key_metrics(self, performance_data):
        """
        Monitor key performance metrics during warming.
        
        Args:
            performance_data (dict): Performance metrics
            
        Returns:
            dict: Analysis of warming performance
        """
        metrics = {
            "bounce_rate": performance_data.get("bounce_rate", 0),
            "complaint_rate": performance_data.get("complaint_rate", 0),
            "open_rate": performance_data.get("open_rate", 0),
            "click_rate": performance_data.get("click_rate", 0),
            "delivery_rate": performance_data.get("delivery_rate", 100)
        }
        
        # Define warning thresholds
        thresholds = {
            "bounce_rate": {"warning": 2, "critical": 5},
            "complaint_rate": {"warning": 0.08, "critical": 0.2},
            "open_rate": {"warning": 10, "good": 15},
            "click_rate": {"warning": 1, "good": 2}
        }
        
        # Check for issues
        issues = []
        for metric, value in metrics.items():
            if metric in thresholds:
                threshold = thresholds[metric]
                
                # Check if it's a negative metric (lower is better)
                if "critical" in threshold:
                    if value >= threshold["critical"]:
                        issues.append({
                            "metric": metric,
                            "value": value,
                            "severity": "critical",
                            "message": f"{metric.replace('_', ' ').title()} is too high: {value}%"
                        })
                    elif value >= threshold["warning"]:
                        issues.append({
                            "metric": metric,
                            "value": value,
                            "severity": "warning",
                            "message": f"{metric.replace('_', ' ').title()} is elevated: {value}%"
                        })
                # Positive metric (higher is better)
                elif "good" in threshold:
                    if value < threshold["warning"]:
                        issues.append({
                            "metric": metric,
                            "value": value,
                            "severity": "warning",
                            "message": f"{metric.replace('_', ' ').title()} is low: {value}%"
                        })
        
        # Calculate overall health
        if any(issue["severity"] == "critical" for issue in issues):
            health = "critical"
        elif any(issue["severity"] == "warning" for issue in issues):
            health = "warning"
        else:
            health = "good"
        
        # Generate recommendations
        recommendations = []
        
        if metrics["bounce_rate"] > thresholds["bounce_rate"]["warning"]:
            recommendations.append(
                "Slow down your warming schedule until bounce rates improve. " +
                "Review your email list for quality issues."
            )
            
        if metrics["complaint_rate"] > thresholds["complaint_rate"]["warning"]:
            recommendations.append(
                "Pause warming and review your content and targeting. " +
                "High complaint rates can quickly damage IP reputation."
            )
            
        if metrics["open_rate"] < thresholds["open_rate"]["warning"]:
            recommendations.append(
                "Your engagement rates are low. Send to your most engaged users " +
                "during the warming period to build a positive reputation."
            )
        
        return {
            "metrics": metrics,
            "issues": issues,
            "health": health,
            "recommendations": recommendations
        }
    
    def check_blacklist_during_warming(self):
        """
        Check if the IP is on blacklists during warming.
        
        Returns:
            dict: Blacklist check results
        """
        blacklist_results = self.reputation_monitor.check_ip_blacklists()
        
        if blacklist_results["status"] != "clean":
            blacklist_results["recommendations"] = [
                "Your IP is listed on blacklists during warming, which is a serious issue.",
                "Pause sending immediately and investigate the listings.",
                "Contact the blacklist operators for delisting instructions.",
                "Review your list quality and sending practices before resuming.",
                "Consider using a new IP address for warming."
            ]
            blacklist_results["warming_impact"] = "critical"
        else:
            blacklist_results["recommendations"] = [
                "Continue monitoring blacklist status throughout warming."
            ]
            blacklist_results["warming_impact"] = "none"
            
        return blacklist_results
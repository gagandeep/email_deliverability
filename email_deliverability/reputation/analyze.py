"""Analyze email sender reputation data."""
from datetime import datetime, timedelta
import json
import math


class ReputationAnalyzer:
    def __init__(self):
        """Initialize the reputation analyzer."""
        self.score_weights = {
            "authentication": 0.3,
            "bounces": 0.25,
            "complaints": 0.25,
            "blacklists": 0.15,
            "engagement": 0.05
        }
        
    def calculate_reputation_score(self, metrics):
        """
        Calculate an overall reputation score from component metrics.
        
        Args:
            metrics (dict): Component metrics (authentication, bounces, etc.)
            
        Returns:
            float: Overall reputation score (0-100)
        """
        score = 0
        
        for category, weight in self.score_weights.items():
            if category in metrics:
                category_score = metrics[category]
                score += category_score * weight
                
        # Round to one decimal place
        return round(score, 1)
    
    def categorize_reputation(self, score):
        """
        Categorize a reputation score.
        
        Args:
            score (float): Reputation score (0-100)
            
        Returns:
            str: Reputation category
        """
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 50:
            return "poor"
        else:
            return "critical"
    
    def analyze_bounce_trend(self, bounce_history):
        """
        Analyze bounce rate trends over time.
        
        Args:
            bounce_history (list): List of (date, bounce_rate) tuples
            
        Returns:
            dict: Trend analysis
        """
        if not bounce_history or len(bounce_history) < 2:
            return {"trend": "insufficient_data"}
            
        # Sort by date
        bounce_history.sort(key=lambda x: x[0])
        
        # Calculate moving average
        window_size = min(7, len(bounce_history))
        moving_avg = []
        
        for i in range(len(bounce_history) - window_size + 1):
            window = bounce_history[i:i+window_size]
            avg_rate = sum(rate for _, rate in window) / window_size
            moving_avg.append((window[-1][0], avg_rate))
        
        # Calculate trend
        first_avg = moving_avg[0][1] if moving_avg else 0
        last_avg = moving_avg[-1][1] if moving_avg else 0
        
        change = last_avg - first_avg
        change_percent = (change / first_avg * 100) if first_avg else 0
        
        result = {
            "first_date": bounce_history[0][0],
            "last_date": bounce_history[-1][0],
            "current_rate": bounce_history[-1][1],
            "change": change,
            "change_percent": round(change_percent, 1)
        }
        
        # Determine trend direction
        if change_percent > 10:
            result["trend"] = "increasing"  # Bad
        elif change_percent < -10:
            result["trend"] = "decreasing"  # Good
        else:
            result["trend"] = "stable"
            
        # Add risk assessment
        if bounce_history[-1][1] > 5:
            result["risk"] = "high"
        elif bounce_history[-1][1] > 2:
            result["risk"] = "medium"
        else:
            result["risk"] = "low"
            
        return result
    
    def analyze_authentication_results(self, auth_data, days=30):
        """
        Analyze email authentication pass rates.
        
        Args:
            auth_data (list): List of authentication results
            days (int): Number of days to analyze
            
        Returns:
            dict: Authentication analysis
        """
        if not auth_data:
            return {"status": "no_data"}
            
        # Count pass/fail by mechanism
        mechanisms = ["spf", "dkim", "dmarc"]
        results = {mech: {"pass": 0, "fail": 0} for mech in mechanisms}
        
        for record in auth_data:
            for mech in mechanisms:
                if record.get(mech) == "pass":
                    results[mech]["pass"] += 1
                elif record.get(mech) in ["fail", "permerror", "temperror"]:
                    results[mech]["fail"] += 1
        
        # Calculate pass rates
        analysis = {}
        for mech in mechanisms:
            total = results[mech]["pass"] + results[mech]["fail"]
            if total > 0:
                pass_rate = results[mech]["pass"] / total * 100
                analysis[f"{mech}_pass_rate"] = round(pass_rate, 1)
                
                # Determine status
                if pass_rate >= 95:
                    analysis[f"{mech}_status"] = "excellent"
                elif pass_rate >= 90:
                    analysis[f"{mech}_status"] = "good"
                elif pass_rate >= 80:
                    analysis[f"{mech}_status"] = "fair"
                else:
                    analysis[f"{mech}_status"] = "poor"
            else:
                analysis[f"{mech}_pass_rate"] = 0
                analysis[f"{mech}_status"] = "no_data"
        
        # Calculate overall authentication score (0-100)
        if all(analysis.get(f"{mech}_pass_rate", 0) > 0 for mech in mechanisms):
            spf_weight = 0.3
            dkim_weight = 0.3
            dmarc_weight = 0.4
            
            auth_score = (
                analysis.get("spf_pass_rate", 0) * spf_weight +
                analysis.get("dkim_pass_rate", 0) * dkim_weight +
                analysis.get("dmarc_pass_rate", 0) * dmarc_weight
            )
            
            analysis["authentication_score"] = round(auth_score, 1)
        
        return analysis
    
    def analyze_complaint_patterns(self, complaints):
        """
        Analyze patterns in spam complaints.
        
        Args:
            complaints (list): List of complaint records
            
        Returns:
            dict: Complaint pattern analysis
        """
        if not complaints:
            return {"status": "no_data"}
            
        # Group by campaign, content type, sending time
        by_campaign = {}
        by_hour = [0] * 24
        by_day = [0] * 7
        content_types = {"promotional": 0, "transactional": 0, "newsletter": 0, "other": 0}
        
        for complaint in complaints:
            # Campaign analysis
            campaign_id = complaint.get("campaign_id", "unknown")
            if campaign_id not in by_campaign:
                by_campaign[campaign_id] = 0
            by_campaign[campaign_id] += 1
            
            # Time analysis
            timestamp = complaint.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    by_hour[dt.hour] += 1
                    by_day[dt.weekday()] += 1
                except (ValueError, TypeError):
                    pass
                    
            # Content type
            content_type = complaint.get("content_type", "other").lower()
            if content_type in content_types:
                content_types[content_type] += 1
            else:
                content_types["other"] += 1
                
        # Find campaign with highest complaint rate
        total_complaints = sum(by_campaign.values())
        campaign_percentages = {
            campaign: (count / total_complaints * 100)
            for campaign, count in by_campaign.items()
        }
        
        # Find peak hours
        peak_hour = by_hour.index(max(by_hour)) if sum(by_hour) > 0 else -1
        peak_day = by_day.index(max(by_day)) if sum(by_day) > 0 else -1
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        analysis = {
            "total_complaints": total_complaints,
            "by_campaign": campaign_percentages,
            "worst_campaign": max(by_campaign.items(), key=lambda x: x[1])[0] if by_campaign else None,
            "peak_hour": peak_hour,
            "peak_day": day_names[peak_day] if peak_day >= 0 else None,
            "by_content_type": content_types
        }
        
        # Add recommendations
        recommendations = []
        
        if analysis["worst_campaign"]:
            campaign = analysis["worst_campaign"]
            recommendations.append(
                f"Review campaign '{campaign}' which has the highest complaint rate"
            )
            
        if peak_hour >= 0:
            recommendations.append(
                f"Consider adjusting send times to avoid peak complaint hour ({peak_hour}:00)"
            )
            
        analysis["recommendations"] = recommendations
        
        return analysis
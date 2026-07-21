"""Dashboard analytics service."""

import hashlib
import random
from datetime import datetime, timedelta, timezone

from app.schemas.report import (
    ActivityDataPoint,
    DashboardData,
    DashboardStats,
    NetworkUsage,
    RiskDistribution,
    TopWallet,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class DashboardService:
    """Service for aggregating dashboard analytics data.

    In demo mode, generates realistic synthetic analytics.
    In production, would query PostgreSQL aggregated views.
    """

    async def get_dashboard_data(self) -> DashboardData:
        """Get complete dashboard analytics data.

        Returns:
            DashboardData with all widget data.
        """
        rng = random.Random(42)

        stats = DashboardStats(
            total_addresses_analyzed=12847,
            total_investigations=342,
            active_investigations=28,
            high_risk_addresses=1203,
            total_alerts=567,
            unread_alerts=23,
            total_reports=89,
            avg_risk_score=34.7,
        )

        risk_dist = RiskDistribution(
            critical=127,
            high=456,
            medium=2341,
            low=5890,
            minimal=4033,
        )

        # Daily activity (last 30 days)
        now = datetime.now(timezone.utc)
        daily_activity = []
        for i in range(30):
            date = now - timedelta(days=29 - i)
            daily_activity.append(ActivityDataPoint(
                timestamp=date.strftime("%Y-%m-%d"),
                value=float(rng.randint(50, 500)),
                label=date.strftime("%b %d"),
            ))

        # Hourly activity
        hourly_activity = [
            ActivityDataPoint(
                timestamp=f"{h:02d}:00",
                value=float(rng.randint(10, 200)),
                label=f"{h:02d}:00",
            )
            for h in range(24)
        ]

        # Network usage
        networks = [
            ("Ethereum", 4521),
            ("Bitcoin", 2890),
            ("Tron", 1876),
            ("BNB Chain", 1245),
            ("Polygon", 987),
            ("Arbitrum", 654),
            ("Solana", 543),
            ("Optimism", 321),
            ("Base", 234),
            ("Litecoin", 156),
            ("Dogecoin", 120),
        ]
        total_network = sum(n[1] for n in networks)
        network_usage = [
            NetworkUsage(
                chain=name,
                count=count,
                percentage=round(count / total_network * 100, 1),
            )
            for name, count in networks
        ]

        # Top wallets
        top_wallets = [
            TopWallet(
                address="0x28c6c06298d514db089934071355e5743bf21d60",
                chain="ethereum",
                label="Binance Hot Wallet",
                volume_usd=45_678_234.50,
                risk_score=15,
            ),
            TopWallet(
                address="0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",
                chain="ethereum",
                label="Tornado Cash Router",
                volume_usd=12_345_678.90,
                risk_score=95,
            ),
            TopWallet(
                address="bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h",
                chain="bitcoin",
                label="Binance BTC Hot",
                volume_usd=89_012_345.67,
                risk_score=12,
            ),
            TopWallet(
                address="0x098b716b8aaf21512996dc57eb0615e2383e2f96",
                chain="ethereum",
                label="Lazarus Group",
                volume_usd=2_345_678.90,
                risk_score=99,
            ),
            TopWallet(
                address="0x5041ed759dd4afc3a72b8192c143f72f4724081a",
                chain="ethereum",
                label="OKX",
                volume_usd=34_567_890.12,
                risk_score=18,
            ),
        ]

        # Volume history
        volume_history = []
        for i in range(30):
            date = now - timedelta(days=29 - i)
            volume_history.append(ActivityDataPoint(
                timestamp=date.strftime("%Y-%m-%d"),
                value=round(rng.uniform(1_000_000, 50_000_000), 2),
                label=date.strftime("%b %d"),
            ))

        # Recent alerts
        recent_alerts = [
            {
                "id": "alert_1",
                "type": "sanctions_match",
                "severity": "critical",
                "title": "OFAC Sanctions Match Detected",
                "message": "Address 0x098b...2f96 matches Lazarus Group",
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "is_read": False,
            },
            {
                "id": "alert_2",
                "type": "high_risk",
                "severity": "high",
                "title": "High Risk Score Alert",
                "message": "Address 0xd90e...4f31 scored 95/100",
                "timestamp": (now - timedelta(hours=5)).isoformat(),
                "is_read": False,
            },
            {
                "id": "alert_3",
                "type": "anomaly",
                "severity": "medium",
                "title": "Anomalous Pattern Detected",
                "message": "Rapid movement pattern on 0x3fc9...7fad",
                "timestamp": (now - timedelta(hours=12)).isoformat(),
                "is_read": True,
            },
            {
                "id": "alert_4",
                "type": "pattern",
                "severity": "high",
                "title": "Smurfing Pattern Detected",
                "message": "Multiple structured transactions on 0x1f98...4081",
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "is_read": True,
            },
        ]

        return DashboardData(
            stats=stats,
            risk_distribution=risk_dist,
            daily_activity=daily_activity,
            hourly_activity=hourly_activity,
            network_usage=network_usage,
            top_wallets=top_wallets,
            recent_alerts=recent_alerts,
            volume_history=volume_history,
        )

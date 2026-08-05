from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
import logging

from app.models.analytics import AnalyticsEvent, DailyStat
from app.models.chat import ChatMessage
from app.models.user import User
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class AnalyticsService:
    """سرویس تحلیل داده‌ها"""

    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        user_id: Optional[int],
        session_id: str,
        event_type: str,
        event_name: Optional[str] = None,
        event_data: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
        duration: Optional[float] = None
    ) -> AnalyticsEvent:
        """ثبت رویداد تحلیلی"""
        event = AnalyticsEvent(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            event_name=event_name,
            event_data=event_data or {},
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            duration=duration
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def get_daily_stats(self, target_date: Optional[date] = None) -> Dict:
        """دریافت آمار روزانه"""
        if target_date is None:
            target_date = date.today()

        stat = self.db.query(DailyStat).filter(
            DailyStat.stat_date == target_date
        ).first()

        if not stat:
            return self._generate_daily_stats(target_date)

        return {
            "date": stat.stat_date.isoformat(),
            "total_users": stat.total_users,
            "new_users": stat.new_users,
            "active_users": stat.active_users,
            "chat_messages": stat.chat_messages,
            "chat_sessions": stat.chat_sessions,
            "avg_response_time": stat.avg_response_time,
            "service_searches": stat.service_searches,
            "location_requests": stat.location_requests,
            "route_requests": stat.route_requests,
            "page_views": stat.page_views,
            "total_requests": stat.total_requests,
            "error_count": stat.error_count
        }

    def _generate_daily_stats(self, target_date: date) -> Dict:
        """تولید آمار روزانه از داده‌های موجود"""
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())

        # تعداد کاربران جدید
        new_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= start,
            User.created_at <= end
        ).scalar() or 0

        # تعداد پیام‌های چت
        chat_messages = self.db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.created_at >= start,
            ChatMessage.created_at <= end
        ).scalar() or 0

        # میانگین زمان پاسخ
        avg_response = self.db.query(
            func.avg(ChatMessage.processing_time)
        ).filter(
            ChatMessage.created_at >= start,
            ChatMessage.created_at <= end
        ).scalar() or 0

        # تعداد رویدادها
        total_requests = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.created_at >= start,
            AnalyticsEvent.created_at <= end
        ).scalar() or 0

        error_count = self.db.query(func.count(AnalyticsEvent.id)).filter(
            AnalyticsEvent.created_at >= start,
            AnalyticsEvent.created_at <= end,
            AnalyticsEvent.event_type == "error"
        ).scalar() or 0

        return {
            "date": target_date.isoformat(),
            "total_users": 0,
            "new_users": new_users,
            "active_users": 0,
            "chat_messages": chat_messages,
            "chat_sessions": 0,
            "avg_response_time": round(avg_response or 0, 3),
            "service_searches": 0,
            "location_requests": 0,
            "route_requests": 0,
            "page_views": 0,
            "total_requests": total_requests,
            "error_count": error_count
        }

    def get_user_activity(self, user_id: int, days: int = 7) -> List[Dict]:
        """دریافت فعالیت‌های کاربر"""
        start_date = datetime.utcnow() - timedelta(days=days)

        events = self.db.query(AnalyticsEvent).filter(
            AnalyticsEvent.user_id == user_id,
            AnalyticsEvent.created_at >= start_date
        ).order_by(AnalyticsEvent.created_at.desc()).all()

        return [
            {
                "id": e.id,
                "type": e.event_type,
                "name": e.event_name,
                "data": e.event_data,
                "timestamp": e.created_at.isoformat()
            }
            for e in events
        ]

    def get_system_stats(self) -> Dict:
        """آمار کلی سیستم"""
        # تعداد کل کاربران
        total_users = self.db.query(func.count(User.id)).scalar() or 0

        # کاربران فعال (ورود در ۷ روز اخیر)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users = self.db.query(func.count(User.id)).filter(
            User.last_login >= week_ago
        ).scalar() or 0

        # تعداد کل پیام‌های چت
        total_messages = self.db.query(func.count(ChatMessage.id)).scalar() or 0

        # میانگین کلی زمان پاسخ
        avg_response = self.db.query(
            func.avg(ChatMessage.processing_time)
        ).scalar() or 0

        # تعداد کل رویدادها
        total_events = self.db.query(func.count(AnalyticsEvent.id)).scalar() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_messages": total_messages,
            "avg_response_time": round(avg_response or 0, 3),
            "total_events": total_events,
            "event_types": self._get_event_type_counts()
        }

    def _get_event_type_counts(self) -> List[Dict]:
        """تعداد رویدادها بر اساس نوع"""
        results = self.db.query(
            AnalyticsEvent.event_type,
            func.count(AnalyticsEvent.id).label('count')
        ).group_by(AnalyticsEvent.event_type).all()

        return [
            {"type": r[0], "count": r[1]}
            for r in results
        ]

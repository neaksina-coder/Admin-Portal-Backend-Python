# api/v1/api_router.py
from fastapi import APIRouter
from api.v1 import auth, users, businesses, plans, subscriptions, customers, dashboard, ai_insights, sales, reports, marketing_campaigns, promos, invoices, audit_logs, admin_digests, chat, notifications


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["ai-insights"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(marketing_campaigns.router, prefix="/marketing", tags=["marketing"])
api_router.include_router(promos.router, prefix="/promos", tags=["promos"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(admin_digests.router, prefix="/admin-digest", tags=["admin-digest"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

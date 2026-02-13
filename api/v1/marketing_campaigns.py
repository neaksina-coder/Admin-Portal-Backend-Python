# api/v1/marketing_campaigns.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api import deps
from crud import marketing_campaign as crud_campaign
from models.customer import Customer
from models.marketing_email_log import MarketingEmailLog
from utils.email import send_email
from core.config import settings
from schemas.marketing_campaign import (
    MarketingCampaignCreate,
    MarketingCampaignUpdate,
    MarketingCampaignResponse,
    MarketingCampaignListResponse,
    MarketingCampaignSendRequest,
)
from schemas.marketing_email_log import MarketingEmailLogListResponse

router = APIRouter()


def _render_campaign_html(subject: str, body: str) -> str:
    safe_body = (body or "").replace("\n", "<br>")
    return f"""\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{subject}</title>
    <!--[if mso]>
    <style type="text/css">
     
    </style>
    <![endif]-->
  </head>
  <body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background:#f8fafc;">
      <tr>
        <td align="center" style="padding:40px 20px;">
          
          <!-- Main Container -->
          <table role="presentation" cellpadding="0" cellspacing="0" width="600" style="max-width:600px;background:#ffffff;border-radius:16px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1),0 2px 4px -1px rgba(0,0,0,0.06);overflow:hidden;">
            
            <!-- Header Brand Bar -->
            <tr>
              <td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:32px 40px;text-align:center;">
                <h2 style="margin:0;color:#ffffff;font-size:18px;font-weight:600;letter-spacing:0.5px;">
                  SINA NEAK BUSINESS TOOLS
                </h2>
              </td>
            </tr>
            
            <!-- Subject Header -->
            <tr>
              <td style="padding:40px 40px 20px 40px;">
                <h1 style="margin:0;font-size:26px;font-weight:700;color:#0f172a;line-height:1.3;">
                  {subject}
                </h1>
              </td>
            </tr>
            
            <!-- Divider -->
            <tr>
              <td style="padding:0 40px;">
                <div style="height:3px;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);border-radius:2px;width:60px;"></div>
              </td>
            </tr>
            
            <!-- Body Content -->
            <tr>
              <td style="padding:24px 40px 40px 40px;color:#475569;font-size:15px;line-height:1.7;">
                {safe_body}
              </td>
            </tr>
            
            <!-- Footer Section -->
            <tr>
              <td style="background:#f8fafc;padding:32px 40px;border-top:1px solid #e2e8f0;">
                <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                  <tr>
                    <td style="color:#64748b;font-size:13px;line-height:1.6;">
                      <p style="margin:0 0 8px 0;font-weight:500;color:#475569;">
                        Sina Neak Business Tools
                      </p>
                      <p style="margin:0;color:#94a3b8;">
                        This email was sent from an automated system. Please do not reply directly to this message.
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            
            <!-- Copyright Bar -->
            <tr>
              <td style="background:#0f172a;padding:20px 40px;text-align:center;">
                <p style="margin:0;color:#94a3b8;font-size:12px;">
                  © 2024 Sina Neak Business Tools. All rights reserved.
                </p>
              </td>
            </tr>
            
          </table>
          
        </td>
      </tr>
    </table>
  </body>
</html>
"""


@router.post("/", response_model=MarketingCampaignResponse, status_code=201)
def create_campaign(
    campaign_in: MarketingCampaignCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    campaign = crud_campaign.create_campaign(db, campaign_in)
    return {
        "success": True,
        "status_code": 201,
        "message": "Campaign created successfully",
        "data": campaign,
    }


@router.get("/", response_model=MarketingCampaignListResponse)
def list_campaigns(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    campaigns = crud_campaign.list_campaigns(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Campaigns retrieved successfully",
        "total": len(campaigns),
        "data": campaigns,
    }


@router.get("/{campaign_id}", response_model=MarketingCampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    campaign = crud_campaign.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Campaign retrieved successfully",
        "data": campaign,
    }


@router.put("/{campaign_id}", response_model=MarketingCampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_in: MarketingCampaignUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    campaign = crud_campaign.update_campaign(db, campaign_id, campaign_in)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Campaign updated successfully",
        "data": campaign,
    }


@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    campaign = crud_campaign.delete_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"success": True, "message": "Campaign deleted successfully"}


@router.post("/{campaign_id}/send")
def send_campaign_email(
    campaign_id: int,
    payload: MarketingCampaignSendRequest,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    campaign = crud_campaign.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    segment = payload.target_segment or payload.segment or campaign.target_segment
    if segment:
        segment = segment.strip().lower()
        if segment == "all":
            segment = None

    if not (settings.EMAIL_FROM and settings.SMTP_USER and settings.SMTP_PASSWORD):
        raise HTTPException(status_code=500, detail="SMTP is not configured")

    query = db.query(Customer).filter(
        Customer.business_id == campaign.business_id,
        Customer.email.isnot(None),
    )
    if segment:
        query = query.filter(func.lower(Customer.segment) == segment)
    recipients = [row.email for row in query.all() if row.email]

    if payload.dry_run:
        return {
            "success": True,
            "status_code": 200,
            "message": "Dry run: no emails sent",
            "data": {"recipients": len(recipients)},
        }

    sent = 0
    for email in recipients:
        status = "sent"
        error_message = None
        html = payload.html or _render_campaign_html(payload.subject, payload.body)
        try:
            send_email(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_password=settings.SMTP_PASSWORD,
                smtp_use_tls=settings.SMTP_USE_TLS,
                from_email=settings.EMAIL_FROM,
                to_email=email,
                subject=payload.subject,
                content=payload.body,
                html_content=html,
            )
            sent += 1
        except Exception as exc:
            status = "failed"
            error_message = str(exc)
        db.add(
            MarketingEmailLog(
                campaign_id=campaign.id,
                business_id=campaign.business_id,
                recipient_email=email,
                subject=payload.subject,
                status=status,
                error_message=error_message,
            )
        )

    # Update metrics (basic)
    metrics = campaign.performance_metrics or {}
    metrics["sent"] = sent
    campaign.performance_metrics = metrics
    db.add(campaign)
    db.commit()

    return {
        "success": True,
        "status_code": 200,
        "message": "Campaign emails sent",
        "data": {"sent": sent, "segment": segment},
    }


@router.get("/{campaign_id}/logs", response_model=MarketingEmailLogListResponse)
def list_campaign_logs(
    campaign_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    logs = (
        db.query(MarketingEmailLog)
        .filter(MarketingEmailLog.campaign_id == campaign_id)
        .order_by(MarketingEmailLog.sent_at.desc())
        .all()
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Campaign email logs",
        "total": len(logs),
        "data": logs,
    }

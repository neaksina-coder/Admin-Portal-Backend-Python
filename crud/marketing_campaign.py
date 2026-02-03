# crud/marketing_campaign.py
from sqlalchemy.orm import Session
from typing import Optional, List

from models.marketing_campaign import MarketingCampaign
from schemas.marketing_campaign import MarketingCampaignCreate, MarketingCampaignUpdate


def get_campaign(db: Session, campaign_id: int) -> Optional[MarketingCampaign]:
    return db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()


def list_campaigns(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[MarketingCampaign]:
    return (
        db.query(MarketingCampaign)
        .filter(MarketingCampaign.business_id == business_id)
        .order_by(MarketingCampaign.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_campaign(db: Session, campaign_in: MarketingCampaignCreate) -> MarketingCampaign:
    db_campaign = MarketingCampaign(**campaign_in.dict(by_alias=False))
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def update_campaign(
    db: Session, campaign_id: int, campaign_in: MarketingCampaignUpdate
) -> Optional[MarketingCampaign]:
    db_campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
    if not db_campaign:
        return None
    update_data = campaign_in.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_campaign, key, value)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def delete_campaign(db: Session, campaign_id: int) -> Optional[MarketingCampaign]:
    db_campaign = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
    if not db_campaign:
        return None
    db.delete(db_campaign)
    db.commit()
    return db_campaign

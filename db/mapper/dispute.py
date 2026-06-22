import domain
from db import models
from .registry import registry


def map_dispute_to_domain(orm_obj: models.Dispute) -> domain.Dispute:
    return domain.Dispute(
        dispute_id=orm_obj.id,
        order_id=orm_obj.order_id,
        opened_by_id=orm_obj.opened_by_id,
        reason=orm_obj.reason,
        status=domain.DisputeStatuses(orm_obj.status_name),
        resolved_by_id=orm_obj.resolved_by_id,
        created_at=orm_obj.created_at,
        resolved_at=orm_obj.resolved_at
    )


def map_dispute_to_orm(d_obj: domain.Dispute) -> models.Dispute:
    return models.Dispute(
        id=d_obj.id,
        order_id=d_obj.order_id,
        opened_by_id=d_obj.opened_by_id,
        reason=d_obj.reason,
        status_name=d_obj.status,
        resolved_by_id=d_obj.resolved_by_id,
        created_at=d_obj.created_at,
        resolved_at=d_obj.resolved_at
    )


def map_dispute_message_to_domain(orm_obj: models.DisputeMessage) -> domain.DisputeMessage:
    return domain.DisputeMessage(
        sender_id=orm_obj.sender_id,
        dispute_id=orm_obj.dispute_id,
        text=orm_obj.text,
        created_at=orm_obj.created_at,
        message_id=orm_obj.id
    )

def map_dispute_message_to_orm(d_obj: domain.DisputeMessage) -> models.DisputeMessage:
    return models.DisputeMessage(
        sender_id=d_obj.sender_id,
        dispute_id=d_obj.dispute_id,
        text=d_obj.text,
        created_at=d_obj.created_at,
    )

registry.register(domain.Dispute, models.Dispute, to_orm=map_dispute_to_orm, to_domain=map_dispute_to_domain)
registry.register(domain.DisputeMessage, models.DisputeMessage, to_orm=map_dispute_message_to_orm, to_domain=map_dispute_message_to_domain)
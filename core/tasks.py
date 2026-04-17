import logging

from celery import shared_task

from leads.email_automation import EmailFollowUpSystem
from leads.models import CommunicationLog, Lead

logger = logging.getLogger(__name__)

AUTO_WELCOME_SUBJECT_PREFIX = "[AUTO_WELCOME]"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_welcome_email_task(self, lead_id):
    """
    Send exactly one welcome email for a lead.
    Retries transient failures, and never blocks request/response flow.
    """
    lead = Lead.objects.filter(pk=lead_id).first()
    if not lead:
        logger.warning("Welcome email skipped: lead not found (id=%s)", lead_id)
        return False

    if CommunicationLog.objects.filter(
        lead_id=lead_id,
        communication_type="email",
        direction="out",
        subject__startswith=AUTO_WELCOME_SUBJECT_PREFIX,
    ).exists():
        logger.info("Welcome email skipped: already sent (lead=%s)", lead_id)
        return True

    sent = bool(EmailFollowUpSystem(lead).send_welcome_email())
    if not sent:
        raise RuntimeError(f"SMTP send failed for lead={lead_id}")

    CommunicationLog.objects.create(
        lead=lead,
        communication_type="email",
        direction="out",
        subject=f"{AUTO_WELCOME_SUBJECT_PREFIX} Welcome email delivered",
        content="Automatic welcome email sent successfully.",
        staff_member=None,
    )
    logger.info("Welcome email sent successfully for lead=%s", lead_id)
    return True

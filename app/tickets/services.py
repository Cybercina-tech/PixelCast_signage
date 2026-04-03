"""
Ticket domain service layer.

All state transitions, assignment, SLA computation, and merge logic
go through this module so validation happens in one place.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional

from django.db import models, transaction
from django.utils import timezone

from .models import (
    Ticket, TicketAuditEvent, TicketMessage, TicketRelation,
    TicketRoutingRule, TicketSlaPolicy, TicketSlaSnapshot,
)

logger = logging.getLogger(__name__)

VALID_TRANSITIONS: dict[str, set[str]] = {
    'open': {'assigned', 'in_progress', 'closed'},
    'assigned': {'in_progress', 'pending', 'resolved', 'closed'},
    'in_progress': {'pending', 'resolved', 'closed'},
    'pending': {'in_progress', 'resolved', 'closed'},
    'resolved': {'closed'},
    'closed': set(),
}


class TicketTransitionError(Exception):
    pass


def _audit(ticket, actor, action, changes=None):
    TicketAuditEvent.objects.create(
        ticket=ticket,
        actor=actor,
        action=action,
        changes=changes or {},
    )


def _transition(ticket: Ticket, new_status: str, actor, *, reason: str = ''):
    allowed = VALID_TRANSITIONS.get(ticket.status, set())
    if new_status not in allowed:
        raise TicketTransitionError(
            f'Cannot move from {ticket.status} to {new_status}'
        )
    old = ticket.status
    ticket.status = new_status
    now = timezone.now()
    if new_status == 'resolved':
        ticket.resolved_at = now
    elif new_status == 'closed':
        ticket.closed_at = now
    ticket.save(update_fields=['status', 'resolved_at', 'closed_at', 'updated_at'])
    _audit(ticket, actor, f'status_change', {'from': old, 'to': new_status, 'reason': reason})


# ---------------------------------------------------------------
# Public API
# ---------------------------------------------------------------

@transaction.atomic
def create_ticket(
    *,
    tenant,
    requester,
    subject: str,
    body: str,
    priority: str = 'medium',
    source: str = 'web',
    category: str = '',
    language: str = 'en',
    attachments=None,
) -> Ticket:
    ticket = Ticket(
        tenant=tenant,
        subject=subject,
        priority=priority,
        source=source,
        requester=requester,
        category=category,
        language=language,
    )
    ticket.save()

    TicketMessage.objects.create(
        ticket=ticket,
        author=requester,
        body=body,
        is_internal=False,
        source=source,
    )
    ticket.last_message_at = timezone.now()
    ticket.save(update_fields=['last_message_at'])

    _apply_sla(ticket)
    _auto_route(ticket)
    _audit(ticket, requester, 'created')
    return ticket


@transaction.atomic
def assign_ticket(ticket: Ticket, assignee, actor) -> Ticket:
    old_assignee = ticket.assignee_id
    ticket.assignee = assignee
    if ticket.status == 'open':
        ticket.status = 'assigned'
    ticket.save(update_fields=['assignee', 'status', 'updated_at'])
    _audit(ticket, actor, 'assigned', {
        'from_assignee': str(old_assignee) if old_assignee else None,
        'to_assignee': str(assignee.id),
    })
    return ticket


@transaction.atomic
def start_progress(ticket: Ticket, actor) -> Ticket:
    _transition(ticket, 'in_progress', actor)
    if not ticket.first_responded_at:
        ticket.first_responded_at = timezone.now()
        ticket.save(update_fields=['first_responded_at'])
        _mark_sla_achieved(ticket, 'first_response')
    return ticket


@transaction.atomic
def pend_ticket(ticket: Ticket, actor, *, reason: str = '') -> Ticket:
    _transition(ticket, 'pending', actor, reason=reason)
    return ticket


@transaction.atomic
def resolve_ticket(ticket: Ticket, actor, *, reason: str = '') -> Ticket:
    _transition(ticket, 'resolved', actor, reason=reason)
    _mark_sla_achieved(ticket, 'resolution')
    return ticket


@transaction.atomic
def close_ticket(ticket: Ticket, actor, *, reason: str = '') -> Ticket:
    _transition(ticket, 'closed', actor, reason=reason)
    return ticket


@transaction.atomic
def reopen_ticket(ticket: Ticket, actor, *, reason: str = '') -> Ticket:
    if ticket.status not in ('resolved', 'closed'):
        raise TicketTransitionError('Can only reopen resolved or closed tickets')
    old = ticket.status
    ticket.status = 'open'
    ticket.resolved_at = None
    ticket.closed_at = None
    ticket.save(update_fields=['status', 'resolved_at', 'closed_at', 'updated_at'])
    _audit(ticket, actor, 'reopened', {'from': old, 'reason': reason})
    _apply_sla(ticket)
    return ticket


@transaction.atomic
def escalate_ticket(ticket: Ticket, actor, *, reason: str = '') -> Ticket:
    if ticket.priority == 'critical':
        new_priority = 'critical'
    else:
        order = ['low', 'medium', 'high', 'critical']
        idx = order.index(ticket.priority)
        new_priority = order[min(idx + 1, len(order) - 1)]
    old = ticket.priority
    ticket.priority = new_priority
    ticket.save(update_fields=['priority', 'updated_at'])
    _audit(ticket, actor, 'escalated', {'from_priority': old, 'to_priority': new_priority, 'reason': reason})
    _apply_sla(ticket)
    return ticket


@transaction.atomic
def merge_tickets(source: Ticket, target: Ticket, actor) -> Ticket:
    if source.tenant_id != target.tenant_id:
        raise TicketTransitionError('Cannot merge tickets across tenants')
    source.merged_into = target
    source.status = 'closed'
    source.closed_at = timezone.now()
    source.save(update_fields=['merged_into', 'status', 'closed_at', 'updated_at'])
    TicketRelation.objects.create(
        source=source, target=target, relation_type='merged_from', created_by=actor,
    )
    _audit(source, actor, 'merged', {'into_ticket': str(target.id)})
    _audit(target, actor, 'merge_received', {'from_ticket': str(source.id)})
    return target


def add_reply(
    ticket: Ticket, author, body: str, *, is_internal: bool = False,
    source: str = 'web', body_html: str = '',
) -> TicketMessage:
    msg = TicketMessage.objects.create(
        ticket=ticket,
        author=author,
        body=body,
        body_html=body_html,
        is_internal=is_internal,
        source=source,
    )
    ticket.last_message_at = msg.created_at
    ticket.save(update_fields=['last_message_at', 'updated_at'])
    if not is_internal and not ticket.first_responded_at and author != ticket.requester:
        ticket.first_responded_at = msg.created_at
        ticket.save(update_fields=['first_responded_at'])
        _mark_sla_achieved(ticket, 'first_response')
    _audit(ticket, author, 'internal_note' if is_internal else 'reply')
    return msg


# ---------------------------------------------------------------
# SLA helpers
# ---------------------------------------------------------------

def _apply_sla(ticket: Ticket):
    policy = TicketSlaPolicy.objects.filter(
        tenant=ticket.tenant, priority=ticket.priority, is_active=True,
    ).first()
    if not policy:
        return
    ticket.sla_policy = policy
    now = timezone.now()
    ticket.first_response_due_at = now + timedelta(minutes=policy.first_response_minutes)
    ticket.resolution_due_at = now + timedelta(minutes=policy.resolution_minutes)
    ticket.save(update_fields=['sla_policy', 'first_response_due_at', 'resolution_due_at'])

    for metric, target_at in [
        ('first_response', ticket.first_response_due_at),
        ('resolution', ticket.resolution_due_at),
    ]:
        TicketSlaSnapshot.objects.update_or_create(
            ticket=ticket, metric=metric,
            defaults={'target_at': target_at, 'status': 'on_track'},
        )


def _mark_sla_achieved(ticket: Ticket, metric: str):
    snap = TicketSlaSnapshot.objects.filter(ticket=ticket, metric=metric).first()
    if snap and snap.status in ('on_track', 'warning'):
        snap.status = 'achieved'
        snap.achieved_at = timezone.now()
        snap.save(update_fields=['status', 'achieved_at', 'updated_at'])


# ---------------------------------------------------------------
# Auto-routing
# ---------------------------------------------------------------

def _auto_route(ticket: Ticket):
    rules = TicketRoutingRule.objects.filter(
        tenant=ticket.tenant, is_active=True,
    ).select_related('queue').order_by('priority_order')
    for rule in rules:
        if _rule_matches(rule, ticket):
            ticket.queue = rule.queue
            ticket.save(update_fields=['queue'])
            if rule.strategy == 'round_robin':
                _round_robin_assign(ticket, rule.queue)
            elif rule.strategy == 'least_busy':
                _least_busy_assign(ticket, rule.queue)
            return
    from .models import TicketQueue
    default_queue = TicketQueue.objects.filter(
        tenant=ticket.tenant, is_default=True, is_active=True,
    ).first()
    if default_queue:
        ticket.queue = default_queue
        ticket.save(update_fields=['queue'])


def _rule_matches(rule: TicketRoutingRule, ticket: Ticket) -> bool:
    conds = rule.conditions or {}
    if 'priority' in conds and ticket.priority not in (conds['priority'] if isinstance(conds['priority'], list) else [conds['priority']]):
        return False
    if 'category' in conds and ticket.category not in (conds['category'] if isinstance(conds['category'], list) else [conds['category']]):
        return False
    if 'language' in conds and ticket.language not in (conds['language'] if isinstance(conds['language'], list) else [conds['language']]):
        return False
    return True


def _round_robin_assign(ticket: Ticket, queue):
    from .models import TicketRoleProfile
    agents = list(
        TicketRoleProfile.objects.filter(
            tenant=ticket.tenant, role__in=['agent', 'supervisor'], is_active=True,
        ).values_list('user_id', flat=True)
    )
    if not agents:
        return
    last_assigned = (
        Ticket.objects.filter(tenant=ticket.tenant, queue=queue, assignee__isnull=False)
        .order_by('-updated_at')
        .values_list('assignee_id', flat=True)
        .first()
    )
    if last_assigned and last_assigned in agents:
        idx = (agents.index(last_assigned) + 1) % len(agents)
    else:
        idx = 0
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        assignee = User.objects.get(pk=agents[idx])
        ticket.assignee = assignee
        if ticket.status == 'open':
            ticket.status = 'assigned'
        ticket.save(update_fields=['assignee', 'status'])
    except User.DoesNotExist:
        pass


def _least_busy_assign(ticket: Ticket, queue):
    from django.contrib.auth import get_user_model
    from django.db.models import Count
    from .models import TicketRoleProfile
    User = get_user_model()
    agents = list(
        TicketRoleProfile.objects.filter(
            tenant=ticket.tenant, role__in=['agent', 'supervisor'], is_active=True,
        ).values_list('user_id', flat=True)
    )
    if not agents:
        return
    least = (
        User.objects.filter(pk__in=agents)
        .annotate(open_count=Count(
            'assigned_tickets',
            filter=models.Q(assigned_tickets__status__in=['open', 'assigned', 'in_progress']),
        ))
        .order_by('open_count')
        .first()
    )
    if least:
        ticket.assignee = least
        if ticket.status == 'open':
            ticket.status = 'assigned'
        ticket.save(update_fields=['assignee', 'status'])

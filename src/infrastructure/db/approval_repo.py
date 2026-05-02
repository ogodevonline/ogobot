"""SQLAlchemy implementation of ApprovalRepository."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.application.dto import ApprovalDTO
from src.application.repositories import ApprovalRepository
from src.infrastructure.db.models import Approval


class SqlApprovalRepository(ApprovalRepository):
    """SQLAlchemy-based approval storage."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def create(self, approval: ApprovalDTO) -> ApprovalDTO:
        """Persist a new approval record."""
        async with self._session_factory() as session:
            record = Approval(
                id=approval.id,
                task_id=approval.task_id,
                action_type=approval.action_type,
                action_data=approval.action_data,
                status=approval.status,
                user_id=approval.user_id,
                created_at=approval.created_at,
                approved_at=approval.approved_at,
            )
            session.add(record)
            await session.commit()
        return approval

    async def update_status(
        self, approval_id: str, status: str, approved_at: datetime | None
    ) -> ApprovalDTO:
        """Update approval status and timestamp."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(Approval).where(Approval.id == approval_id)
            )
            record = result.scalar_one_or_none()
            if record is None:
                raise ValueError(f"Approval {approval_id} not found")
            record.status = status
            record.approved_at = approved_at
            await session.commit()
            return self._to_dto(record)

    async def get_pending_by_task_id(self, task_id: str) -> ApprovalDTO | None:
        """Find pending approval for a given task."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(Approval)
                .where(Approval.task_id == task_id)
                .where(Approval.status == "pending")
                .order_by(Approval.created_at.desc())
                .limit(1)
            )
            record = result.scalar_one_or_none()
            return self._to_dto(record) if record else None

    @staticmethod
    def _to_dto(record: Approval) -> ApprovalDTO:
        """Map ORM model to DTO."""
        return ApprovalDTO(
            id=record.id,
            task_id=record.task_id,
            action_type=record.action_type,
            action_data=record.action_data,
            status=record.status,
            user_id=record.user_id,
            created_at=record.created_at,
            approved_at=record.approved_at,
        )

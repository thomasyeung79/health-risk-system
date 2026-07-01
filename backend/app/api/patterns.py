"""Pattern Discovery API — automatically discover behaviour patterns for a member."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.wellness_os import PatternDiscoveryResponse
from app.services.auth import get_current_user
from app.services.pattern_discovery_service import discover_patterns

router = APIRouter(prefix="/api/v1/patterns", tags=["patterns"])


@router.get("/{member_id}", response_model=PatternDiscoveryResponse)
def get_patterns(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Discover behavioural patterns for a member."""
    member = db.get(Member, member_id)
    if member is None or member.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Member not found")
    result = discover_patterns(db=db, user_id=current_user.id, member_id=member_id)
    return PatternDiscoveryResponse(**result)

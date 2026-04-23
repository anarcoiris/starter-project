from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserProfile, WalletUpdate
from app.repositories.user_repository import UserRepository
from app.api.deps import get_user_repository

router = APIRouter()

@router.get("/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str, repo: UserRepository = Depends(get_user_repository)):
    profile = await repo.get_by_id(user_id)
    if not profile:
        profile = UserProfile(userId=user_id)
        await repo.update_activity(user_id)
    return profile

@router.post("/{user_id}/wallet")
async def link_wallet(
    user_id: str, 
    update: WalletUpdate, 
    repo: UserRepository = Depends(get_user_repository)
):
    # En el futuro, aquí validaríamos una firma digital (ECDSA) de la wallet
    success = await repo.update_wallet(user_id, update.walletAddress)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update wallet")
    return {"status": "success", "message": "Wallet linked successfully"}

from core.models import PromoCode, PromoCodeActivation


async def get_activations(promo_code_id: str) -> int:
    return await PromoCodeActivation.objects.filter(
        promo_code_id=promo_code_id,
    ).acount()


async def get_remaining_activations(promo_code: PromoCode) -> int:
    return promo_code.activations_limit - await get_activations(promo_code.pk)


async def promo_code_is_active(promo_code: PromoCode | None) -> bool:
    if not promo_code:
        return False
    return await get_remaining_activations(promo_code) > 0

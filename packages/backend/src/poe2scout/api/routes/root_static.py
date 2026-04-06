from fastapi import APIRouter
from pydantic import BaseModel

from poe2scout.db.repositories import game_repository, league_repository, realm_repository


router = root_static_router = APIRouter(prefix="/Static", tags=["Static"])


class RealmOptionResponse(BaseModel):
    value: str
    label: str
    game_api_id: str
    realm_api_id: str
    trade_api_path: str
    default_league_value: str


@router.get("/Realms")
async def get_realms() -> list[RealmOptionResponse]:
    games = await game_repository.get_games()
    realms = await realm_repository.get_realms()

    game_lookup = {game.game_id: game for game in games}
    default_league_lookup: dict[int, str] = {}
    for game in games:
        default_league_id = await game_repository.get_default_league(game.game_id)
        default_league = await league_repository.get_league(default_league_id)
        default_league_lookup[game.game_id] = default_league.value

    game_display_lookup = {
        "poe": "poe1",
        "poe2": "poe2",
    }

    def realm_sort_key(realm) -> tuple[int, int]:
        game = game_lookup[realm.game_id]
        realm_order = {
            "pc": 0,
            "xbox": 1,
            "sony": 2,
            "poe2": 0,
        }
        game_order = {
            "poe": 0,
            "poe2": 1,
        }
        return (
            game_order.get(game.api_id, 99),
            realm_order.get(realm.api_id, 99),
        )

    return [
        RealmOptionResponse(
            value=f"{game_display_lookup.get(game_lookup[realm.game_id].api_id, game_lookup[realm.game_id].api_id)}/{realm.api_id}",
            label=f"{game_display_lookup.get(game_lookup[realm.game_id].api_id, game_lookup[realm.game_id].api_id)}/{realm.api_id}",
            game_api_id=game_lookup[realm.game_id].api_id,
            realm_api_id=realm.api_id,
            trade_api_path=game_lookup[realm.game_id].ggg_api_trade_identifier,
            default_league_value=default_league_lookup[realm.game_id],
        )
        for realm in sorted(realms, key=realm_sort_key)
    ]

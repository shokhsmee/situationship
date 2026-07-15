"""Game start + private role/evidence delivery via DM."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.game_kb import open_game_keyboard
from bot.services.api_client import ApiClient

router = Router()


def role_card_text(state: dict) -> str:
    me = state.get("me", {})
    role = me.get("role") or {}
    lines = [f"🎭 <b>Your role: {role.get('name', 'Investigator')}</b>", role.get("description", "")]
    if me.get("is_insider"):
        lines += ["", "🕵️ <b>YOU ARE THE INSIDER</b>", me.get("insider_goal", "")]
    hand = me.get("hand", [])
    if hand:
        lines += ["", "🔎 <b>Your private evidence:</b>"]
        lines += [f"• {e['title']}" for e in hand]
    return "\n".join(line for line in lines if line is not None)


@router.callback_query(F.data.startswith("start:"))
async def start_investigation(cb: CallbackQuery, api: ApiClient):
    game_id = int(cb.data.split(":")[1])
    try:
        await api.start_game(cb.from_user.id, game_id)
    except Exception:
        await cb.answer("Cannot start yet (need ≥3 players, host only).", show_alert=True)
        return

    dealt = 0
    for tg_id in api.members(game_id):
        try:
            state = await api.get_state(tg_id, game_id)
            await cb.bot.send_message(
                tg_id, role_card_text(state), reply_markup=open_game_keyboard(game_id)
            )
            dealt += 1
        except Exception:
            continue
    await cb.answer(f"🔔 Roles dealt to {dealt} players!")
    await cb.message.answer("The investigation has begun. Check your DMs for your secret role.")


@router.message(Command("myrole"))
async def my_role(message: Message, command, api: ApiClient):
    args = (command.args or "").strip()
    if not args.isdigit():
        await message.answer("Usage: /myrole <game_id>")
        return
    try:
        state = await api.get_state(message.from_user.id, int(args))
    except Exception:
        await message.answer("Couldn't fetch your role — are you in that game?")
        return
    await message.answer(role_card_text(state), reply_markup=open_game_keyboard(int(args)))

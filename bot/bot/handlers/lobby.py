"""Lobby creation and joining: /new, scenario pick, /join CODE."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.lobby_kb import lobby_keyboard, scenarios_keyboard
from bot.services.api_client import ApiClient

router = Router()


@router.message(Command("new"))
async def new_game(message: Message, api: ApiClient):
    scenarios = await api.list_scenarios()
    if not scenarios:
        await message.answer("No published cases yet. Ask an admin to publish one in the Studio.")
        return
    await message.answer("Choose a case to investigate:", reply_markup=scenarios_keyboard(scenarios))


@router.callback_query(F.data.startswith("new:"))
async def create_from_scenario(cb: CallbackQuery, api: ApiClient):
    scenario_id = int(cb.data.split(":")[1])
    try:
        game = await api.create_game(cb.from_user.id, scenario_id)
    except Exception:
        await cb.answer("Could not create game", show_alert=True)
        return
    api.track_member(game["id"], cb.from_user.id)
    await cb.message.answer(
        f"🎬 Lobby created!\nCode: <b>{game['code']}</b>\n"
        f"Share it or tap invite. You are the host.",
        reply_markup=lobby_keyboard(game["id"], game["code"], is_host=True),
    )
    await cb.answer()


@router.message(Command("join"))
async def join(message: Message, command, api: ApiClient):
    code = (command.args or "").strip().upper()
    if not code:
        await message.answer("Usage: /join <code>ABC123</code>")
        return
    try:
        state = await api.join_game(message.from_user.id, code)
    except Exception:
        await message.answer("❌ Couldn't join. Check the code.")
        return
    api.track_member(state["id"], message.from_user.id)
    await message.answer(
        f"✅ Joined <b>{code}</b>!",
        reply_markup=lobby_keyboard(state["id"], code, is_host=False),
    )

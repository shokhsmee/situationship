"""/start — welcome and deep-link lobby join (?start=join_<code>)."""
from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from bot.keyboards.lobby_kb import lobby_keyboard
from bot.services.api_client import ApiClient

router = Router()

WELCOME = (
    "🔍 <b>Situationship</b>\n\n"
    "A team investigates a hidden crime — but one of you is the <b>Insider</b>.\n\n"
    "• /new — create a case and invite friends\n"
    "• /join <code>CODE</code> — join an existing lobby\n"
)


@router.message(CommandStart(deep_link=True))
async def start_deeplink(message: Message, command: CommandObject, api: ApiClient):
    payload = command.args or ""
    if not payload.startswith("join_"):
        await message.answer(WELCOME)
        return
    code = payload.removeprefix("join_").upper()
    try:
        state = await api.join_game(message.from_user.id, code)
    except Exception:
        await message.answer("❌ Couldn't join that lobby. Check the code or try /new.")
        return
    api.track_member(state["id"], message.from_user.id)
    is_host = bool(state.get("me", {}).get("is_host"))
    await message.answer(
        f"✅ Joined lobby <b>{code}</b>!\nWaiting room below 👇",
        reply_markup=lobby_keyboard(state["id"], code, is_host=is_host),
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME)

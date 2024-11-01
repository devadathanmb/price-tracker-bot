from aiogram import Dispatcher
from aiogram.filters import Command

from .start import command_start_handler
from .list import command_list_handler
from .state_machines.track_item import track_item_router
from .state_machines.remove_item import remove_item_router
from .state_machines.purge import purge_router

def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(command_start_handler, Command("start"))
    dp.message.register(command_list_handler, Command("list"))
    dp.include_router(track_item_router)
    dp.include_router(remove_item_router)
    dp.include_router(purge_router)

from typing import TYPE_CHECKING, Any

from lib.extension import Extension, initExt

if TYPE_CHECKING:
    from lib.ctx import Ctx

    from .widgets.widget import Widget as WidgetType


class Widget(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.widgets: list[tuple[type['WidgetType'], dict[str, Any]]]
        super().__init__(ctx, cfg)

    async def __ainit__(self):
        for widget, args in self.widgets:
            await initExt(widget, self.ctx, {**args, 'win': self.ctx.root})

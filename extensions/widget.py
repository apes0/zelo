from lib.extension import Extension
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lib.ctx import Ctx
    from .widgets.widget import Widget as WidgetType


class Widget(Extension):
    def __init__(self, ctx: 'Ctx', cfg) -> None:
        self.widgets: dict[type['WidgetType'], dict[str, Any]]
        super().__init__(ctx, cfg)

        for widget, args in self.widgets.items():
            widget(ctx=ctx, cfg={**args, 'win': ctx.root})

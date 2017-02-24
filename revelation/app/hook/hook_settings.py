from .hooks.bizocean import BizoceanHook
from .hooks.movieform import MovieformHook
from .hooks.docreq import DocreqHook

INSTALLED_HOOKS = (
    BizoceanHook,
    MovieformHook,
    DocreqHook,
)

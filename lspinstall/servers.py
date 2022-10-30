from .source.npm import *
from .source.go import *
from .source.pip import *
from .source.archive import *


lang_servers = [
    sumneko,
    bicep,
    rust_analuzer,
    omnisharp,
    elixirls,
    pylsp,
    gopls,
    tsserver,
    vscode_langservers_extracted,
    bashls,
    yamlls,
    awk_ls,
]

lang_servers_dict = {s.name: s for s in lang_servers}

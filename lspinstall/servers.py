from .source import archive, go, npm, pip

lang_servers = [
    archive.sumneko,
    archive.bicep,
    archive.rust_analuzer,
    archive.omnisharp,
    archive.elixirls,
    archive.clojure_lsp,
    pip.pylsp,
    go.gopls,
    npm.tsserver,
    npm.vscode_langservers_extracted,
    npm.bashls,
    npm.yamlls,
    npm.awk_ls,
]

lang_servers_dict = {s.name: s for s in lang_servers}

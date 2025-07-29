require('lspconfig').basedpyright.setup({
    cmd = { 'docker', 'compose', 'exec', 'model', 'basedpyright-langserver', '--stdio' }
})

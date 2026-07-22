def register_onkey(channel_id, nvim):
    lua_script = f"""
vim.on_key(function(key)
    -- Enviar notificación RPC al canal del cliente
    -- 'tecla_presionada' es el nombre del evento que el cliente debe escuchar
    vim.rpcnotify({channel_id}, 'tecla_presionada', key)
end)
"""
    nvim.exec_lua(lua_script, [])


def register_onkey3(channel_id, nvim):
    lua_script = f"""
local ns = vim.api.nvim_create_namespace('mi_capturador_teclas')

vim.on_key(function(key)
    if not key or key == '' then return end
    
    -- pcall intenta ejecutar la notificación. Si falla (canal inválido),
    -- simplemente no hace nada en lugar de lanzar el error visual en Neovim.
    pcall(vim.rpcnotify, {channel_id}, 'tecla_presionada', key)
end, ns)
"""



    nvim.exec_lua(lua_script, [])


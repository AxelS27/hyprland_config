local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
vim.opt.rtp:prepend(lazypath)

require("options")
require("keymaps")

local plugins = require("plugins")
require("lazy").setup(plugins)

vim.opt.termguicolors = true
require('onedark').setup { style = 'dark' }
require('onedark').load()

local ok, ts = pcall(require, "nvim-treesitter.configs")
if ok then
    ts.setup {
        ensure_installed = { "c", "cpp", "python", "lua", "javascript", "html", "css" },
        highlight = { enable = true, additional_vim_regex_highlighting = false }
    }
end

local presence_ok, presence = pcall(require, "presence")
if presence_ok then
    presence.setup({
        auto_update = true,
        neovim_image_text = "Neovim Editor",
        main_image = "neovim",
        enable_line_number = true,
        blacklist = {},
    })
end


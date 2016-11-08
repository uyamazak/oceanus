set nocompatible
set backupdir=$HOME/backup/vim
"表示
set number
set ruler
set statusline=%F%m%r%h%w\ [FORMAT=%{&ff}]\ [TYPE=%Y]\ [ASCII=\%03.3b]\ [HEX=\%02.2B]\ [POS=%04l,%04v][%p%%]\ [LEN=%L]
"set list
set title
set showmatch

colorscheme ron

"日本語
set termencoding=utf-8
set encoding=utf-8

"タブ
set ts=4
set softtabstop=4
set autoindent
set expandtab

"カーソルで前行へ
set whichwrap=b,s,h,l,<,>,[,]

"入力補助
set backspace=indent,eol,start
set formatoptions+=m

"行末の空白削除
autocmd BufWritePre * :%s/\s\+$//e

"辞書
autocmd FileType php :set dictionary+=~/.vim/dict/php.dict

let g:neocomplcache_enable_at_startup = 1
function InsertTabWrapper()
        if pumvisible()
            return "\<c-n>"
        endif
        let col = col('.') - 1
        if !col || getline('.')[col - 1] !~ '\k\|<\|/'
            return "\<tab>"
        elseif exists('&omnifunc') && &omnifunc == ''
            return "\<c-n>"
        else
            return "\<c-x>\<c-o>"
        endif
endfunction
inoremap <tab> <c-r>=InsertTabWrapper()<cr>
"補完が動かなかったので追加
setlocal omnifunc=syntaxcomplete#Complete

" 全角スペース・行末のスペース・タブの可視化
if has("syntax")
    syntax on

    " PODバグ対策
    syn sync fromstart

    function! ActivateInvisibleIndicator()
        "# 下の行の"　"は全角スペース
        syntax match InvisibleJISX0208Space "　" display containedin=ALL
        highlight InvisibleJISX0208Space term=underline ctermbg=Blue guibg=darkgray gui=underline
        syntax match InvisibleTrailedSpace "[ \t]\+$" display containedin=ALL
        highlight InvisibleTrailedSpace term=underline ctermbg=Red guibg=NONE gui=undercurl guisp=darkorange
        syntax match InvisibleTab "\t" display containedin=ALL
        highlight InvisibleTab term=underline ctermbg=white gui=undercurl guisp=darkslategray
    endfunction

    augroup invisible
        autocmd! invisible
        autocmd BufNew,BufRead * call ActivateInvisibleIndicator()
    augroup END
endif

"特殊な拡張子の設定
au BufNewFile,BufRead *.twig setf html





"NeoBundle Scripts-----------------------------
if &compatible
  set nocompatible               " Be iMproved
endif

" Required:
set runtimepath^=/home/BIZOCEAN/yu_yamazaki/.vim/bundle/neobundle.vim/

" Required:
call neobundle#begin(expand('/home/BIZOCEAN/yu_yamazaki/.vim/bundle'))

" Let NeoBundle manage NeoBundle
" Required:
NeoBundleFetch 'Shougo/neobundle.vim'

" Add or remove your Bundles here:
NeoBundle 'Shougo/neosnippet.vim'
NeoBundle 'Shougo/neosnippet-snippets'
NeoBundle 'tpope/vim-fugitive'
NeoBundle 'ctrlpvim/ctrlp.vim'
NeoBundle 'flazz/vim-colorschemes'

" You can specify revision/branch/tag.
NeoBundle 'Shougo/vimshell', { 'rev' : '3787e5' }

NeoBundle 'stephpy/vim-yaml'

" Required:
call neobundle#end()

" Required:
filetype plugin indent on

" If there are uninstalled bundles found on startup,
" this will conveniently prompt you to install them.
NeoBundleCheck
"End NeoBundle Scripts-------------------------


NeoBundleLazy "nvie/vim-flake8", {
      \ "autoload": {
      \   "filetypes": ["python", "python3", "djangohtml"]
      \ }}

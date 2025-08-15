" Basic Vim Configuration

" Enable syntax highlighting
syntax enable

" Show line numbers
set number

" Show relative line numbers
"set relativenumber

" Enable mouse support
set mouse=a

" Set tab width
set tabstop=4
set shiftwidth=4
set expandtab

" Smart indentation
set smartindent
set autoindent

" Search settings
set ignorecase
set smartcase
set incsearch
set hlsearch

" Show matching brackets
set showmatch

" Enable backspace over everything
set backspace=indent,eol,start

" Don't create backup files
set nobackup
set nowritebackup
set noswapfile

" Better command line completion
set wildmenu
set wildmode=longest,list,full
set showcmd

" Keep more lines visible when scrolling
set scrolloff=8

" Show current position
set ruler

" Highlight current line
set cursorline

" Enable file type detection
filetype plugin indent on

" Clear search highlighting with Ctrl+Space
nnoremap <C-Space> :nohlsearch<CR>

" Make Y behave like C and D
"nnoremap Y y$

" Better window navigation
"nnoremap <C-h> <C-w>h
"nnoremap <C-j> <C-w>j
"nnoremap <C-k> <C-w>k
"nnoremap <C-l> <C-w>l

" Status line
set laststatus=2
set statusline=%f\ %m%r%h%w\ [%Y]\ %=%l/%L,%c\ (%p%%)

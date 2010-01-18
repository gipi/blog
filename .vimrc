if has("autocmd")
    " enable file type detection
    filetype on

    autocmd FileType python setlocal ts=4 sts=4 sw=4 expandtab
    autocmd FileType json setlocal ts=2 sts=2 sw=2 expandtab
endif

" settings for all
set textwidth=80
set smarttab
set smartindent
set noexpandtab

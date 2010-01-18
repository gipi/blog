if has("autocmd")
    " enable file type detection
    filetype on

    autocmd FileType python setlocal ts=4 sts=4 sw=4 expandtab
endif

" settings for all
set textwidth=80
set smarttab
set smartindent
set noexpandtab

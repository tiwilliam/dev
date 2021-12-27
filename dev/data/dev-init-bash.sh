create_pipe() {
    fifo=$(mktemp -t sh.XXXXX)

    exec 100< "$fifo"
    exec 101> "$fifo"

    rm -f "$fifo"
}

read_pipe() {
    while read -d $'\0' data; do
        while read line; do
            eval "$line"
        done <<< "$data"
    done <& 100
}

close_pipe() {
    exec 100>& -
    exec 101>& -
}

dev() {
    create_pipe

    SHELL_FD=101 INVOKED_VIA_SHELL=1 {dev-bare} "$@"

    read_pipe
    close_pipe
}

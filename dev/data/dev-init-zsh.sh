create_pipe() {
    fifo=$(mktemp -t sh.XXXXX)

    exec {DEV_SHELL_RFD}< $fifo
    exec {DEV_SHELL_WFD}> $fifo

    rm -f $fifo
}

read_pipe() {
    while read -d $'\0' data; do
        while read line; do
            eval "$line"
        done <<< $data
    done <& $DEV_SHELL_RFD
}

close_pipe() {
    exec {DEV_SHELL_RFD}>& -
    exec {DEV_SHELL_WFD}>& -
}

dev() {
    create_pipe

    SHELL_FD=$DEV_SHELL_WFD INVOKED_VIA_SHELL=1 {dev-bare} "$@"

    read_pipe
    close_pipe
}

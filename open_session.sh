DIR="/home/BIZOCEAN/yu_yamazaki/project-oceanus"
tmux new-session -d -s oceanus -c "$DIR"
tmux new-window -n zsh -c "$DIR"
tmux new-window -n zsh -c "$DIR"
tmux new-window -n oceanus -c "$DIR/oceanus"
tmux new-window -n oceanus -c "$DIR/oceanus"
tmux new-window -n r2bq -c "$DIR/redis2bq"
tmux new-window -n r2bq -c "$DIR/redis2bq"
tmux new-window -n reve -c "$DIR/sub2revelation"
tmux new-window -n reve -c "$DIR/sub2revelation"
tmux attach -t oceanus

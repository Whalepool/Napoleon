#!/bin/bash  
msg_squealer() { 
	SQUEALER_DIR=$(find /* -name squealer_pub.py -exec dirname {} \; 2>&1 | grep -v "Permission denied" )

	if [[ -n $SQUEALER_DIR  ]]; then
	    echo "Squealer is present on the server at $SQUEALER_DIR, msging $1"

	    EXECUTE='python3.6 '"$SQUEALER_DIR"'/squealer_pub.py --msg="$1" '
	    echo "executing: $EXECUTE"
	    eval $EXECUTE

	else
		echo 'no'
	fi
}

git remote -v update

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
	msg_squealer "Pulling from github to update napoleon"
    git pull 
elif [ $REMOTE = $BASE ]; then
	msg_squealer "Napoleon has changes that need to be pushed to github"
    echo "Need to push"
else
	msg_squealer "Napoleon has divered from github main branch, merge then commit"
    echo "Diverged"
fi
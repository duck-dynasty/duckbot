# ensure we're in the right directory
if git rev-parse --is-inside-work-tree > /dev/null 2>&1 && [[ $(basename `git rev-parse --show-toplevel`) == "duckbot" ]]; then
    # we're in the duckbot repo, move to the toplevel before executing
    cd `git rev-parse --show-toplevel`
else
    echo "Needs to be run from the duckbot git repository."
    return
fi

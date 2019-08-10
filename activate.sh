#!/bin/bash
:<<doc
activates analogy environment, if not it creates it
doc

if conda activate; then
    echo "Module loaded"
else
    echo "Loading module"
    module load python/anaconda3
    export PATH=`echo ${PATH} | cut -d ':' -f2-`

    # >>> conda initialize >>>
    # !! Contents within this block are managed by 'conda init' !!
    __conda_setup="$('/u/local/apps/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/u/local/apps/anaconda3/etc/profile.d/conda.sh" ]; then
            . "/u/local/apps/anaconda3/etc/profile.d/conda.sh"
        else
            export PATH="/u/local/apps/anaconda3/bin:$PATH"
        fi
    fi
    unset __conda_setup
    # <<< conda initialize <<<
fi

if conda activate analogy; then
    echo "Environment loaded"
else
    echo "Creating environment"
    conda create -n analogy python=3.7
    pip install -r requirements.txt
fi
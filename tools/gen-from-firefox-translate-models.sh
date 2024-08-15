#!/bin/bash
set -e
langs=`find firefox-translations-models/models/prod/ -type d -print0 | xargs -0 basename -a`
path_output=`pwd`/output/firefox
mkdir -p $path_output
rm $path_output/* || true
path_registry="$path_output/registry.json"

for lang in $langs; do
    if [ "$lang" == "prod" ]; then
        continue
    fi

    echo "[*] handling $lang" >&2
    pushd "firefox-translations-models/models/prod/$lang" >/dev/null
        path_tmp=$(mktemp -d)

        for path_gz in `ls *.gz`; do
            fn=${path_gz%???}
            path_file="$path_tmp/$fn"
            gunzip -c $path_gz > $path_file
        done;

        json_item=$(cat <<EOF
    "$lang": {
        "lex": {
            "API": 1,
            "modelType": "prod",
            "name": "`ls $path_tmp/lex* | xargs -0 basename`",
            "size": 6182512,
            "version": 1
        },
        "model": {
            "API": 1,
            "modelType": "prod",
            "name": "`ls $path_tmp/model* | xargs -0 basename`",
            "size": 17140899,
            "version": 1
        },
        "vocab": {
            "API": 1,
            "modelType": "prod",
            "name": "`ls $path_tmp/vocab* | xargs -0 basename -a`",
            "size": 920621,
            "version": 1
        }
    }
EOF
)
        cp $path_tmp/* $path_output
        echo $json_item > "$path_output/$lang.json"
    popd
done;

rm $path_registry || true
pushd $path_output >/dev/null
    for j in `ls *.json`; do echo "`cat $j`," >> $path_registry; done
    reg=`cat $path_registry`
    echo "{${reg%?}}" > /tmp/registry.json
    rm *.json
    rm kotki_models.zip || true
    mv /tmp/registry.json $path_registry
    zip kotki_models.zip *
popd
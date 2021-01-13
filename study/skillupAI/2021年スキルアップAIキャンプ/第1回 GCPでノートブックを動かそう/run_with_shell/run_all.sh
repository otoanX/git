#/bin/bash

csvfile=users.csv
core_num=2
echo core_num=$core_num

run () {
        local uid=$1
        echo $uid $family_name
        nohup python -u train.py --uid $uid >> log/log_$uid 2>&1
}
export -f run #xargsで呼び出すためにexportしておく
(cat $csvfile | while read line; do uid=`echo ${line} | cut -d ',' -f2`; echo $uid $family_name; done) | xargs -n 2 -P $core_num -I{} bash -c "run {}"
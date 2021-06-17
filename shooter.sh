if [ $1 == 'help' ]
then
    while read line; do echo $line; done < shooter.help
elif [ $1 == 'shoot' ]
then
    if [ $2 == 'daily' ] || [ $2 == 'weekly' ] || [ $2 == 'monthly' ]
    then
        python3 src/screenshot/fialda.py $2
    elif [ $2 == '15m' ] || [ $2 == '1h' ] || [ $2 == '1d' ]
    then
        python3 src/screenshot/fialda.py $2 $3
    elif [ $2 == 'portfolio' ] || [ $2 == 'following' ] || [ $2 == 'vn30' ]
    then
        python3 src/screenshot/fialda.py $2 $3
    else
        python3 src/screenshot/fialda.py $2 $3
    fi
elif [ $1 == 'vol' ] 
then
    python3 src/volume/analysisVolume.py $2 $3 $4 $5
elif [ $1 == 'check' ] 
then
    python3 src/volume/checkMarket.py $2 $3 $4 $5
elif [ $1 == 'scan' ] 
then
    python3 src/volume/scanAbnormal.py
fi

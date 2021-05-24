if [ $1 == 'help' ]
then
    while read line; do echo $line; done < kqls.help
elif [ $1 == 'auth' ]
then
    if [ $# == 3 ]
    then
        python3 src/api/auth.py $2 $3
    fi
    if [ $# == 4 ]
    then
        python3 src/api/auth.py $2 $3 $4
    fi
elif [ $1 == 'matched' ]
then
    echo Get matched transactions
    python3 src/api/volumes.py $1
elif [ $1 == 'volumes' ]
then
    echo Get high volumes
    python3 src/watch/signals.py $1
elif [ $1 == 'levels' ]
then
    echo Get stocks close to levels
    python3 src/watch/signals.py $1
elif [ $1 == 'extract_volumes' ]
then
    python3 src/watch/signals.py $1
elif [ $1 == 'extract_levels' ]
then
    python3 src/watch/signals.py $1
elif [ $1 == 'stats' ]
then
    if [ $# == 2 ]
    then
        echo Make stats reports of $2
        python3 src/analyze/stockStats.py $2
    else
        echo Make stats reports
        python3 src/analyze/marketStats.py $2
    fi
elif [ $1 == 'newTrades' ]
then
    echo Get new trades of $2 on $3
    if [ $# == 4 ]
    then
        python3 src/api/volumes.py $1 $2 $3 $4  
    fi
    if [ $# == 3 ]
    then
        python3 src/api/volumes.py $1 $2 $3
    fi
elif [ $1 == 'oldTrades' ]
then
    echo Get old trades of $2 from $3 to $4
    python3 src/api/volumes.py $1 $2 $3 $4
elif [ $1 == 'update' ]
then
    if [ $2 == 'daily' ]
    then
        echo Update daily
        python3 src/crawler/dailyCrawler.py
    fi
    if [ $2 == 'realtime' ]
    then
        echo Remove old files
        rm data/market/realtime/*.csv
        echo Copy the historical data
        cp data/market/intraday/*.csv data/market/realtime
        echo Update realtime data
        python3 src/api/realtimeUpdate.py
    fi
elif [ $1 == 'prices' ]
then
    if [ $# == 2 ]
    then
        echo List prices of $2
        python3 src/api/stock.py $1 $2
    fi
elif [ $1 == "cancel" ]
then
   echo Cancel $2
   python3 src/api/stock.py cancel $2
elif [ $1 == "orders" ]
then
    if [ $# == 1 ]
    then
        echo List all orders
        python3 src/api/stock.py orders
    else
        echo List orders of $2
        python3 src/api/stock.py orders $2
    fi
else
    if [ $# == 5 ]
    then
        echo Setup new order
        # Future BUY PVD 10 10.5 ACC1
        if [ $1 == "sell" ] || [ $1 == "s" ] || [ $1 == "SELL" ] || [ $1 == "S" ]
        then
            echo Sell $3 $2 with price $4 on $5
            python3 src/api/stock.py $1 $2 $3 $4 $5
        elif [ $1 == "buy" ] || [ $1 == "b" ] || [ $1 == "BUY" ] || [ $1 == "B" ]
        then
            echo Buy $3 $2 with price $4 on $5
            python3 src/api/stock.py $1 $2 $3 $4 $5
        fi
    else
        echo Wrong commands
    fi
fi

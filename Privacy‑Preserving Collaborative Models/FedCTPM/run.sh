num_clients=16
server_port=50027
server_ip=127.0.0.1
local_epochs=1
active_mode=adptpolu
dataset=METR_LA
mode=FED

declare -A rand_nums
rand_nums[$server_port]=1

echo "server ip: $server_ip"
echo "server port: $server_port"

python server.py -n $num_clients -p $server_port -i $server_ip &

(sleep 0.01

for i in $(seq 1 $num_clients)
do
    client_port=$((RANDOM % 40001 + 20000))
    while [[ -n ${rand_nums[$client_port]} ]]; do
        client_port=$((RANDOM % 40001 + 20000))
    done    rand_nums[$client_port]=1

    echo "client $i port: $client_port"
    python client.py --dataset $dataset --exp_mode $mode --cid $i -sip $server_ip -sp $server_port -cp $client_port --device cuda:0 --num_clients $num_clients --divide metis --fedavg --active_mode $active_mode --act_k 2 --local_epochs $local_epochs > train_16metis_LA.log 2>&1 &
done
)

## 等待所有后台进程完成
#wait
#
## 等待server进程完成
#wait $server_pid
#
## 训练完成，脚本结束
#echo "Training completed. Exiting script."
#exit 0

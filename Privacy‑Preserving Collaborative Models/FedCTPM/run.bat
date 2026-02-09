@echo off
set num_clients=16
set server_port=50027
set server_ip=127.0.0.1
set local_epochs=1
set active_mode=adptpolu
set dataset=METR_LA
set mode=FED

set rand_nums[%server_port%]=1

echo server ip: %server_ip%
echo server port: %server_port%

start "" python server.py -n %num_clients% -p %server_port% -i %server_ip%

timeout /t 0 /nobreak >nul

for /l %%i in (1,1,%num_clients%) do (
    setlocal enabledelayedexpansion
    set /a client_port=!random! %% 40001 + 20000
    call :check_port
    echo client %%i port: !client_port!
    start "" python client.py --dataset %dataset% --exp_mode %mode% --cid %%i -sip %server_ip% -sp %server_port% -cp !client_port! --device cuda:0 --num_clients %num_clients% --divide metis --fedavg --active_mode %active_mode% --act_k 2 --local_epochs %local_epochs% > train_16metis_LA.log 2>&1
    endlocal
)

exit /b

:check_port
if defined rand_nums[%client_port%] (
    set /a client_port=%random% %% 40001 + 20000
    goto :check_port
)
set rand_nums[%client_port%]=1
goto :eof
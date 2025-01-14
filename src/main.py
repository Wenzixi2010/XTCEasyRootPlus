import os
from time import sleep
import json
import time
import traceback
from types import TracebackType
from typing import Literal, Type
from modules import tools
import subprocess
import sys
import noneprompt
import requests
from rich.console import Console
from rich.table import Table
import shutil
import threading
from tkinter import filedialog
from modules import logging
# import traceback

version: list[int | Literal['b']] = [2, 0]

if not os.path.exists('logs/'):
    os.mkdir('logs')

debug: bool = False

for i in sys.argv:
    if i == '--debug':
        debug = True
if len(version) >= 3 and version[2] == 'b':
    debug = True

os.system(f'title XTCEasyRootPlus v{version[0]}.{version[1]}')
console = Console()
status = console.status('')
print = console.print

logging.set_config(f'logs/{time.strftime("%Y_%m_%d_%H-%M-%S", time.localtime())}.log', print=console.log, level=(logging.level.debug if debug else logging.level.info))

def global_exception_handler(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: TracebackType):
    exc_traceback_str = '全局错误\n' + \
        ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error(exc_traceback_str)

sys.excepthook = global_exception_handler

if not os.path.exists('tmp/'):
    os.mkdir('tmp')
else:
    for i in os.listdir('tmp'):
        if os.path.isfile(f'tmp/{i}'):
            os.remove(f'tmp/{i}')
        else:
            shutil.rmtree(f'tmp/{i}')

if not os.path.exists('data/'):
    os.mkdir('data')

if len(version) == 3 and version[2] == 'b':
    print('[red][!][/red]警告:这是一个测试版本,非常不稳定,若非测试人员请勿使用!')
    sleep(5)

# 检查更新
os.system('cls')
status.update('正在检查更新')
status.start()
logging.debug(f'当前版本:{version[0]}.{version[1]}')
logging.info('检查最新版本')
rainyun = requests.get('https://cn-nb1.rains3.com/xtceasyrootplus/version.json').status_code == 200
try:  # 尝试获取版本文件
    with requests.get(f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}version.json') as r:  # 获取版本信息
        read = r.content
        try:
            read = json.loads(read)
        except json.decoder.JSONDecodeError as e:
            status.stop()
            tools.logging_traceback('更新失败:JSON无法解码')
            logging.debug(f'版本信息原文:{read}')
            tools.exit_after_enter()
    latest_version = read
    logging.debug(f'最新版本:{latest_version[0]}.{latest_version[1]}')
    if ((latest_version[0] >= version[0] and latest_version[1] > version[1]) if not len(version) >= 3 else (latest_version[0] >= version[0] and latest_version[1] >= version[1])):
        logging.info(f'发现新版本:{latest_version[0]}.{latest_version[1]}')
        logging.info('开始下载新版本......')
        status.stop()
        tools.download_file(
            f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}XTCEasyRootPlusInstaller.exe', 'tmp/XTCEasyRootPlusInstaller.exe')
        subprocess.Popen('tmp/XTCEasyRootPlusInstaller.exe')
        sys.exit()
except requests.ConnectionError as e:  # 捕捉下载失败错误
    logging.error(e)
    logging.info('检查更新失败，请检查你的网络或稍后再试')
    status.stop()
    tools.exit_after_enter()  # 退出

logging.info('当前版本为最新!')
sleep(1)

if not os.path.exists('driver'):
    logging.info('初次使用,自动安装驱动!')
    status.update('安装驱动')
    logging.info('安装Qualcomm驱动')
    tools.run_wait('pnputil /i /a bin/qualcommdriver/*.inf')
    logging.info('安装Fastboot驱动')
    tools.run_wait('pnputil /i /a bin/fastbootdriver/*.inf')
    logging.info('安装驱动完毕!')
    open('driver', 'w').close()
    sleep(1)

while True:
    # 清屏并停止状态指示
    status.stop()
    os.system('cls')

    adb = tools.ADB('bin/adb.exe')

    # 主菜单
    tools.print_logo(version)
    print(f'\nXTCEasyRootPlus [blue]v{version[0]}.{version[1]}{' beta' if debug else ''}{f' {version[3]}' if debug else ''}[/blue]')
    print('本软件是[green]免费公开使用[/green]的，如果你是付费买来的请马上退款，你被骗了！\n')
    print('[red]XTCEasyRootPlus 已经停止维护! 因继续使用 XTCEasyRootPlus 导致的任何问题我们概不负责![/red]')
    print('[red]详情请见 https://github.com/OnesoftQwQ/XTCEasyRootPlus/issues/5[/red]\n')
    logging.debug('进入主菜单')
    choice = noneprompt.ListPrompt(
        '请选择功能',
        [
            noneprompt.Choice('1.一键Root'),
            noneprompt.Choice('2.超级恢复(救砖/降级/恢复原版系统)'),
            noneprompt.Choice('3.工具箱'),
            noneprompt.Choice('4.关于')
        ]
    ).prompt().name
    logging.debug(f'选择:{choice}')
    match choice:
        case '1.一键Root':
            console.rule('免责声明', characters='=')
            print(
                """1.所有已经解除第三方软件安装限制的手表都可以恢复到解除限制前之状态。
2.解除第三方软件安装限制后，您的手表可以无限制地安装第三方软件，需要家长加强对孩子的监管力度，避免孩子沉迷网络，影响学习；手表自带的功能不受影响。
3.您对手表进行解除第三方软件安装限制之操作属于您的自愿行为，若在操作过程中由于操作不当等自身原因，导致出现手表无法正常使用等异常情况，以及解除软件安装限制之后产生的一切后果将由您本人承担！""")
            console.rule('免责声明', characters='=')
            confirm = noneprompt.ConfirmPrompt(
                '你是否已阅读并同意本《免责声明》', default_choice=False).prompt()
            if not confirm:
                continue
            input('请拔出手表上的SIM卡,拔出后按下回车下一步')
            print('\r', end='')
            status.update("等待设备连接")
            status.start()
            print('请在手表上打开并用数据线将手表连接至电脑')
            adb.wait_for_connect()

            logging.info('设备已连接')
            status.update('获取设备信息')
            logging.info('获取设备信息')
            info = adb.get_info()
            logging.debug(f'设备信息:{info}')
            sdk_version = adb.get_version_of_sdk()
            model = tools.xtc_models[info['innermodel']]
            android_version = info['version_of_android_from_sdk']
            table = Table()
            table.add_column("型号", width=12)
            table.add_column("代号")
            table.add_column("系统版本", justify="right")
            table.add_column("安卓版本", justify="right")
            table.add_row(model, info['innermodel'], info['version_of_system'], android_version)
            print(table)
            status.stop()
            if not info['innermodel'] in tools.xtc_models.keys():
                logging.error('设备不是小天才设备')
                print('你的设备貌似不是小天才设备,或者还没被支持,目前暂不支持一键Root')
                tools.pause()
                break
            elif tools.xtc_models[info['innermodel']] == 'Z10':
                logging.error('Z10不支持Root')
                print('Z10不支持Root!')
                tools.pause()
                break

            if not android_version in ('7.1', '8.1'):
                logging.error('不支持的机型')
                print('不支持的机型!')
                break

            is_v3 : bool = True
            is_v3_encrypt: bool = True
            if android_version == '8.1':
                is_v3: bool = tools.is_v3(model, info['version_of_system'])
                """
                is_v3_encrypt = tools.is_v3_encrypt(model, info['version_of_system'])
                logging.debug(f'是否为V3加密版本: {'是' if is_v3_encrypt else '不是'}')
                """
                logging.debug(f'是否为V3: {'是' if is_v3 else '不是'}')
                logging.debug(f'是否是孤儿机型: {'是' if model in ('Z7A', 'Z6_DFB') else '不是'}')

            if android_version == '8.1':
                logging.debug('选择Magisk版本')
                choice = noneprompt.ListPrompt(
                    '请选择想要的Magisk版本',
                    choices=[
                        noneprompt.Choice('1.Magisk25200'),
                        noneprompt.Choice('2.MagiskDelta25210')
                    ],
                ).prompt()
                if choice.name == '1.Magisk25200':
                    magisk = '25200'
                elif choice.name == '2.MagiskDelta25210':
                    magisk = '25210'
                else:
                    magisk = ''
                logging.debug(f'选择Magisk版本:{magisk}')
            else:
                magisk = ''

            if not os.path.exists(f'data/{model}'):
                logging.info('下载文件')
                status.update('下载文件')
                tools.download_file(
                    f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}{model}.zip', f'tmp/{model}.zip')

                logging.info('解压文件')
                status.update('解压文件')
                tools.extract_all(f'tmp/{model}.zip', f'data/{model}/')

            if android_version == '8.1':
                logging.info('下载userdata')
                if magisk == '25200':
                    tools.download_file(
                        f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}1userdata.img', 'tmp/userdata.img')
                elif magisk == '25210':
                    tools.download_file(
                        f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}2userdata.img', 'tmp/userdata.img')

            if android_version == '7.1' or not is_v3: # type: ignore
                logging.debug('获取桌面版本列表')
                with requests.get(f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}launchers.json') as r:
                    read = r.content
                    try:
                        if android_version == '7.1':
                            launchers: dict[str, str] = json.loads(r.content)['711']
                        else:
                            launchers: dict[str, str] = json.loads(r.content)['810']
                    except json.decoder.JSONDecodeError:
                        status.stop()
                        tools.logging_traceback('获取桌面版本列表失败:JSON无法解码')
                        print('获取桌面版本列表失败!')
                        tools.pause()
                        break

                    if not len(launchers) == 1:
                        choices: list[noneprompt.Choice[None]] = []
                        for i in list(launchers.keys()):
                            choices.append(noneprompt.Choice(i))
                        status.stop()
                        choice = noneprompt.ListPrompt('请选择桌面版本(若不知道怎么选择直接选第一项即可)', choices, default_select=1).prompt().name
                        status.start()
                        launcher = launchers[choice]
                    else:
                        launcher = list(launchers.values())[0]
            else:
                logging.warning('V3默认使用121750桌面')
                launcher = '121750.apk'
            
            doze: bool = True
            if android_version == '8.1':
                choice = noneprompt.ConfirmPrompt('是否要需要禁用模式切换').prompt()
                launcher = launcher[:-4]+('_A' if choice else '_B')+launcher[-4:]
                if launcher[0:2] == '12':
                    choice = noneprompt.ConfirmPrompt('12版本桌面较为耗电,是否刷入Doze模块尝试优化耗电?').prompt()
                    doze = choice

            status.stop()

            def download_all_files():
                if android_version == '7.1':
                    filelist = ['appstore.apk', 'moyeinstaller.apk', 'xtctoolbox.apk','filemanager.apk', 'notice.apk', 'toolkit.apk', launcher, 'xws.apk', 'wxzf.apk']
                    for i in filelist:
                        tools.download_file(
                            f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}apps/{i}', f'tmp/{i}', progress_enable=False)
                elif android_version == '8.1':
                    filelist = ['appstore.apk', 'notice.apk', 'wxzf.apk', 'wcp2.apk', 'datacenter.apk','xws.apk', launcher, 'filemanager.apk', 'settings.apk', 'systemplus.apk', 'moyeinstaller.apk']
                    for i in filelist:
                        tools.download_file(f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}apps/{i}', f'tmp/{i}', progress_enable=False)
                    tools.download_file(f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}xtcpatch.zip', 'tmp/xtcpatch.zip', progress_enable=False)
                    if doze:
                        tools.download_file(f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}doze.zip', 'tmp/doze.zip', progress_enable=False)

            download_thread = threading.Thread(target=download_all_files)
            download_thread.start()

            mode: Literal['boot', 'recovery'] = 'recovery'
            if android_version == '7.1':
                logging.debug('选择Root方案')
                choice = noneprompt.ListPrompt(
                    '请选择Root方案',
                    choices=[
                        noneprompt.Choice('1.boot方案(如果你已经降级选这个)'),
                        noneprompt.Choice('2.recovery方案(如果你没有用过超级恢复/降级选这个)')
                    ]
                ).prompt()
                if choice.name == '1.boot方案(如果你已经降级选这个)':
                    mode = 'boot'
                elif choice.name == '2.recovery方案(如果你没有用过超级恢复/降级选这个)':
                    mode = 'recovery'
                logging.debug(f'选择方案:{mode}')

            while True:
                confirm = noneprompt.ConfirmPrompt(
                    '你是否已经将SIM卡拔出?', default_choice=False).prompt()
                if confirm:
                    break
                else:
                    print('请将SIM卡拔出!')
            while True:
                confirm = noneprompt.ConfirmPrompt(
                    '请确认你已经将SIM卡拔出!否则若Root后出现「手表验证异常」我们概不负责!', default_choice=False).prompt()
                if confirm:
                    break
                else:
                    print('请将SIM卡拔出!')

            output = adb.shell('getprop gsm.xtcplmn.plmnstatus')
            if '没有服务' in output:
                status.stop()
                input('手表状态:无服务,请确定您已拔卡!如果不想喜提「手表验证异常」请先拔卡,如已拔卡无视此提示')
            elif '只能拨打紧急电话' in output:
                status.stop()
                input('您似乎没有拔卡!如果不想喜提「手表验证异常」请先拔卡,如已拔卡无视此提示')

            if android_version == '7.1':
                try:
                    status.update('重启设备至9008模式')
                    status.start()
                    logging.info('重启设备至9008模式')
                    adb.reboot(adb.RebootMode.edl)
                    logging.info('等待连接')
                    port = tools.wait_for_edl()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备至9008模式失败')
                    tools.print_traceback_error('重启设备至9008模式失败')
                    tools.pause()
                    break

                logging.info('连接成功,开始读取boot分区')
                status.update('读取boot分区')
                qt = tools.QT('bin/QSaharaServer.exe',
                              'bin/fh_loader.exe', port, f'data/{model}/mbn.mbn')
                try:

                    qt.intosahara()
                    qt.read_partition('boot')
                    logging.info('读取boot分区成功!')
                    shutil.copy('boot.img', 'tmp/')
                    os.remove('boot.img')
                except qt.QSaharaServerError:
                    status.stop()
                    tools.logging_traceback('进入Sahara模式失败')
                    qt.exit9008()
                    tools.print_traceback_error('进入Sahara模式失败')
                    tools.pause()
                    break
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback('读取boot分区失败')
                    qt.exit9008()
                    tools.print_traceback_error('读取boot分区失败')
                    tools.pause()
                    break

                try:
                    logging.info('开始修补boot分区')
                    status.update('修补boot分区')
                    tools.patch_boot('bin/magiskboot.exe',
                                     'tmp/boot.img', 'bin/20400.zip', 'tmp/')
                    logging.info('修补完毕')
                except tools.MAGISKBOOT.MagiskBootError:
                    status.stop()
                    tools.logging_traceback('修补boot分区失败')
                    qt.exit9008()
                    tools.print_traceback_error('修补boot分区失败')
                    tools.pause()
                    break

                try:
                    if mode == 'boot':
                        logging.info('重新刷入boot')
                        status.update('刷入boot')
                        qt.write_partition('tmp/boot_new.img', 'boot')

                    elif mode == 'recovery':
                        logging.info('刷入recovery')
                        status.update('刷入recovery')
                        qt.write_partition('tmp/boot_new.img', 'recovery')

                        logging.info('刷入misc')
                        status.update('刷入misc')
                        qt.write_partition(f'data/{model}/misc.mbn', 'misc')
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback(f'刷入{mode}分区失败')
                    qt.exit9008()
                    tools.print_traceback_error(f'刷入{mode}分区失败')
                    tools.pause()
                    break

                try:
                    logging.info('刷入成功,退出9008模式')
                    status.update('退出9008')
                    qt.exit9008()
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback('退出9008模式失败')
                    tools.print_traceback_error('退出9008模式失败')
                    tools.pause()
                    break

                logging.info('等待重新连接')
                status.update('等待重新连接')
                adb.wait_for_connect()
                adb.wait_for_complete()

                try:
                    logging.info('安装Magisk管理器')
                    status.update('安装Magisk管理器')
                    adb.install(f'data/{model}/manager.apk')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装Magisk管理器失败')
                    tools.print_traceback_error('安装Magisk管理器失败')
                    tools.pause()
                    break

                try:
                    logging.info('启动管理器')
                    status.update('启动管理器')
                    sleep(5)
                    adb.shell('am start com.topjohnwu.magisk/a.c')
                    adb.push(f'data/{model}/xtcpatch', '/sdcard/')
                    adb.push(f'data/{model}/magiskfile', '/sdcard/')
                    adb.push('bin/2100.sh', '/sdcard/')
                    logging.info('刷入模块')
                    status.update('刷入模块')
                    adb.shell('su -c sh /sdcard/2100.sh')
                    adb.install_module('bin/xtcpatch2100.zip')
                    adb.shell(
                        'rm -rf /sdcard/xtcpatch /sdcard/magiskfile /sdcard/2100.sh')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('刷入模块失败')
                    tools.print_traceback_error('刷入模块失败')
                    tools.pause()
                    break

                if download_thread.is_alive():
                    logging.info('下载文件')
                    status.update('下载文件')
                    download_thread.join()

                try:
                    logging.info('安装弦-安装器')
                    adb.install('tmp/moyeinstaller.apk')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装弦-安装器失败')
                    tools.print_traceback_error('安装弦-安装器失败')
                    tools.pause()
                    break

                logging.info('设置充电可用')
                status.update('设置充电可用')
                adb.shell('setprop persist.sys.charge.usable true')

                logging.info('模拟未充电')
                status.update('模拟未充电')
                adb.shell('dumpsys battery unplug')

                status.stop()
                console.rule('接下来需要你对手表进行一些手动操作', characters='=')
                print('请完成激活向导,当提示绑定时直接右滑退出,完成开机向导,进入主界面')
                input('如果你已经进入主界面,请按回车继续')
                console.rule('', characters='=')

                status.update('设置默认软件包管理器')
                status.start()
                logging.info('设置默认软件包管理器')
                adb.push('tmp/notice.apk', '/sdcard/notice.apk')
                if not adb.is_screen_alive():
                    adb.shell('input keyevent 26')
                adb.shell('am start -a android.intent.action.VIEW -d file:///sdcard/notice.apk -t application/vnd.android.package-archive')

                status.stop()
                console.rule('接下来需要你对手表进行一些手动操作', characters='=')
                print('现在你的手表上出现了一个白色的"打开方式"对话框,请往下滑选择"使用弦安装器"并点击始终按钮;点击始终按钮后会弹出安装notice的对话框,点击取消即可')
                input('如果你已经进入主界面,请按回车继续')
                console.rule('', characters='=')
                status.start()

                try:
                    logging.info('安装Xposed Manager')
                    status.update('安装Xposed Manager')
                    adb.install('bin/xposed-magisk.apk', [])
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装Xposed Manager失败')
                    tools.print_traceback_error('安装Xposed Manager失败')
                    tools.pause()
                    break

                if mode == 'recovery':
                    try:
                        logging.info('重启设备至9008模式')
                        status.update('等待连接')
                        adb.reboot(adb.RebootMode.edl)
                        port = tools.wait_for_edl()
                    except adb.ADBError:
                        status.stop()
                        tools.logging_traceback('重启设备至9008模式失败')
                        tools.print_traceback_error('重启设备至9008模式失败')
                        tools.pause()
                        break

                    try:
                        logging.info('进入sahara模式')
                        status.update('进入sahara模式')
                        qt.intosahara()
                        logging.info('刷入recovery')
                        status.update('刷入recovery')
                        qt.write_partition('tmp/boot_new.img', 'recovery')
                        logging.info('刷入misc')
                        status.update('刷入misc')
                        qt.write_partition(f'data/{model}/misc.mbn', 'misc')
                    except qt.QSaharaServerError:
                        status.stop()
                        tools.logging_traceback('进入Sahara模式失败')
                        qt.exit9008()
                        tools.print_traceback_error('进入Sahara模式失败')
                        tools.pause()
                        break
                    except qt.FHLoaderError:
                        status.stop()
                        tools.logging_traceback('刷入recovery/misc失败')
                        qt.exit9008()
                        tools.print_traceback_error('刷入recovery/misc失败')
                        tools.pause()
                        break

                    try:
                        logging.info('退出9008模式')
                        status.update('等待重新连接')
                        qt.exit9008()
                    except qt.FHLoaderError:
                        status.stop()
                        tools.logging_traceback('退出9008模式失败')
                        tools.print_traceback_error('退出9008模式失败')
                        tools.pause()
                        break

                    adb.wait_for_connect()
                    adb.wait_for_complete()

                try:
                    logging.info('安装Xposed-[white]1[/white]')
                    status.update('安装Xposed')
                    adb.install_module('bin/xposed-magisk-1.zip')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装Xposed-1失败')
                    tools.print_traceback_error('安装Xposed-1失败')
                    tools.pause()
                    break

                try:
                    logging.info('重启设备')
                    logging.info(
                        '提示:首次刷入Xposed后开机可能需要[bold]7-15分钟[/bold],请耐心等待')
                    status.update('等待重新连接')
                    adb.reboot()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break

                adb.wait_for_connect()
                adb.wait_for_complete()
                logging.info('连接成功')

                try:
                    logging.info('安装Xposed-[white]2[/white]')
                    status.update('安装Xposed')
                    adb.install_module('bin/xposed-magisk-2.zip')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装Xposed-2失败')
                    tools.print_traceback_error('安装Xposed-2失败')
                    tools.pause()
                    break

                try:
                    logging.info('重启设备')
                    status.update('等待重新连接')
                    adb.reboot()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break

                adb.wait_for_connect()
                adb.wait_for_complete()
                logging.info('连接成功')

                try:
                    status.update('安装核心破解')
                    logging.info('安装核心破解')
                    adb.install('tmp/toolkit.apk')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装核心破解失败')
                    tools.print_traceback_error('安装核心破解失败')
                    tools.pause()
                    break

                try:
                    status.update('设置充电可用')
                    logging.info('设置充电可用')
                    adb.shell('setprop persist.sys.charge.usable true')

                    logging.info('充电可用已开启')
                    logging.info('模拟未充电状态')
                    status.update('模拟未充电状态')
                    adb.shell('dumpsys battery unplug')
                    logging.info('已模拟未充电状态')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('设置充电可用/模拟未充电失败')
                    tools.print_traceback_error('设置充电可用/模拟未充电失败')
                    tools.pause()
                    break

                status.stop()
                console.rule('接下来需要你对手表进行一些手动操作', characters='=')
                input(
                    '请打开手表上的"Xposed Installer"应用,点击左上角的三条杠,点击"模块",勾选"核心破解"选项\n完成操作后请按回车继续')
                console.rule(characters='=')

                try:
                    status.update('等待重新连接')
                    status.start()
                    logging.info('重启手表')
                    adb.reboot()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break

                adb.wait_for_connect()
                adb.wait_for_complete()

                logging.info('连接成功!')
                status.update('安装改版桌面')
                logging.info('开始安装改版系统桌面')
                adb.install(f'tmp/{launcher}')

                try:
                    status.update('等待重新连接')
                    logging.info('重启手表')
                    adb.reboot()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break

                adb.wait_for_connect()
                adb.wait_for_complete()

                logging.info('安装必备软件')
                status.update('安装必备软件')
                for i in os.listdir(f'tmp/'):
                    if i[-3:] == 'apk' and not i == 'moyeinstaller.apk' and not i == launcher and not i == 'toolkit.apk':
                        try:
                            logging.info(f'安装{i}')
                            adb.install(f'tmp/{i}')
                        except adb.ADBError:
                            status.stop()
                            tools.logging_traceback(f'安装{i}失败')
                            tools.print_traceback_error(f'安装{i}失败')
                            tools.pause()
                            break

                status.stop()
                # logging.info('恭喜你,你的手表ROOT完毕!')
                input('恭喜你,Root成功!按回车返回主界面')

            elif android_version == '8.1':
                status.update('等待连接')
                status.start()
                try:
                    logging.info('重启设备至9008模式')
                    adb.reboot(adb.RebootMode.edl)
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break
                logging.info('等待连接')
                port = tools.wait_for_edl()

                logging.info('连接成功')
                logging.info('开始读取boot分区')
                status.update('读取boot分区')
                qt = tools.QT('bin/QSaharaServer.exe',
                              'bin/fh_loader.exe', port, 'bin/msm8937.mbn')
                try:
                    qt.intosahara()
                    qt.read_partition('boot')
                except qt.QSaharaServerError:
                    status.stop()
                    tools.logging_traceback('进入Sahara模式失败')
                    qt.exit9008()
                    tools.print_traceback_error('进入Sahara模式失败')
                    tools.pause()
                    break
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback('读取boot分区失败')
                    qt.exit9008()
                    tools.print_traceback_error('读取boot分区失败')
                    tools.pause()
                    break

                logging.info('读取boot分区成功!')
                shutil.copy('boot.img', 'tmp/')
                os.remove('boot.img')

                try:
                    logging.info('开始修补boot分区')
                    status.update('修补boot分区')
                    tools.patch_boot('bin/magiskboot.exe', 'tmp/boot.img',
                                     f'bin/{magisk}.apk', 'tmp/')
                except tools.MAGISKBOOT.MagiskBootError:
                    status.stop()
                    tools.logging_traceback('修补boot分区失败')
                    qt.exit9008()
                    tools.print_traceback_error('修补boot分区失败')
                    tools.pause()
                    break

                logging.info('修补完毕')

                try:
                    if model in ('Z7A', 'Z6_DFB'):
                        logging.info('刷入recovery')
                        status.update('刷入recovery')
                        qt.write_partition('tmp/boot_new.img', 'recovery')
                    elif not is_v3:
                        logging.info('刷入boot')
                        status.update('刷入boot')
                        qt.write_partition('tmp/boot_new.img', 'boot')
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback(f'刷入{'recovery' if model in ('Z7A', 'Z6_DFB') else 'boot'}失败')
                    qt.exit9008()
                    tools.print_traceback_error(f'刷入{'recovery' if model in ('Z7A', 'Z6_DFB') else 'boot'}失败')
                    tools.pause()
                    break

                try:
                    logging.info('刷入aboot,recovery')
                    status.update('刷入aboot,recovery')
                    qt.fh_loader(rf'--port=\\.\COM{port} --memoryname=emmc --search_path=data/{model}/ --sendxml=data/{model}/rawprogram0.xml --noprompt')
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback('刷入aboot,recovery失败')
                    qt.exit9008()
                    tools.print_traceback_error('刷入aboot,recovery失败')
                    tools.pause()
                    break

                logging.info('刷入成功!')
                if not model in ('Z7A', 'Z6_DFB') and is_v3:
                    try:
                        status.update('刷入空boot')
                        logging.info('刷入空boot')
                        qt.write_partition('bin/eboot.img', 'boot')
                    except qt.FHLoaderError:
                        status.stop()
                        tools.logging_traceback('刷入空boot失败')
                        qt.exit9008()
                        tools.print_traceback_error('刷入空boot失败')
                        tools.pause()
                        break
                
                try:
                    status.update('退出9008')
                    logging.info('退出9008模式')
                    qt.exit9008()
                except qt.FHLoaderError:
                    status.stop()
                    tools.logging_traceback('退出9008模式失败')
                    tools.print_traceback_error('退出9008模式失败')
                    tools.pause()
                    break

                status.update('等待重新连接')
                fastboot = tools.FASTBOOT('bin/fastboot.exe')
                if not model in ('Z7A', 'Z6_DFB'):
                    if is_v3:
                        fastboot.wait_for_fastboot()
                        status.update('刷入boot')
                        logging.info('刷入boot')
                        try:
                            fastboot.flash('boot', 'tmp/boot_new.img')
                        except fastboot.FastbootError:
                            status.stop()
                            tools.logging_traceback('刷入boot失败')
                            tools.print_traceback_error('刷入boot失败')
                            tools.pause()
                            break
                    else:
                        adb.wait_for_connect()
                        adb.wait_for_complete()
                        try:
                            adb.reboot(adb.RebootMode.bootloader)
                        except adb.ADBError:
                            status.stop()
                            tools.logging_traceback('重启进入Bootloader失败')
                            tools.print_traceback_error('重启进入Bootloader失败')
                            tools.pause()
                            break
                        fastboot.wait_for_fastboot()
                    
                    try:
                        status.update('刷入userdata')
                        logging.info('刷入userdata')
                        fastboot.flash('userdata', 'tmp/userdata.img')
                        status.update('刷入misc')
                        logging.info('刷入misc')
                        with open('tmp/misc.bin', 'w') as f:
                            f.write('ffbm-02')
                        fastboot.flash('misc', 'tmp/misc.bin')
                    except fastboot.FastbootError:
                        status.stop()
                        tools.logging_traceback('刷入userdata/misc失败')
                        tools.print_traceback_error('刷入userdata/misc失败')
                        tools.pause()
                        break

                    try:
                        fastboot.reboot()
                    except fastboot.FastbootError:
                        status.stop()
                        tools.logging_traceback('重启进入系统失败')
                        tools.print_traceback_error('重启进入系统失败')
                        tools.pause()
                        break

                    status.update('等待重新连接')
                    logging.info('刷入完毕,重启进入系统')

                adb.wait_for_connect()
                adb.wait_for_complete()
                logging.info('连接成功')

                if is_v3:
                    try:
                        logging.info('创建空文件')
                        status.update('创建空文件')
                        adb.shell(
                            'mkdir /data/adb/modules/XTCPatch/system/app/XTCLauncher')
                        adb.shell(
                            'touch /data/adb/modules/XTCPatch/system/app/XTCLauncher/XTCLauncher.apk')
                        logging.info('重启设备')
                        status.update('等待重新连接')
                        adb.reboot()
                        adb.wait_for_connect()
                        adb.wait_for_complete()
                    except adb.ADBError:
                        status.stop()
                        tools.logging_traceback('创建空文件失败')
                        tools.print_traceback_error('创建空文件失败')
                        tools.pause()
                        break

                if model in ('Z7A', 'Z6_DFB'):
                    try:
                        if download_thread.is_alive():
                            logging.info('下载文件')
                            status.update('下载文件')
                            download_thread.join()
                        logging.info('安装11605桌面')
                        status.update('安装桌面')
                        adb.install('bin/11605launcher.apk')
                        logging.info('重启设备')
                        status.update('等待连接')
                        adb.reboot()
                        adb.wait_for_connect()
                        adb.wait_for_complete()
                    except adb.ADBError:
                        status.stop()
                        tools.logging_traceback('安装11605桌面失败')
                        tools.print_traceback_error('安装11605桌面失败')
                        tools.pause()
                        break

                try:
                    logging.info('开启充电可用')
                    status.update('开启充电可用')
                    adb.shell('setprop persist.sys.charge.usable true')
                    logging.info('模拟未充电')
                    status.update('模拟未充电')
                    adb.shell('dumpsys battery unplug')
                    status.stop()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('开启充电可用/模拟未充电失败')
                    tools.print_traceback_error('开启充电可用/模拟未充电失败')
                    tools.pause()
                    break

                console.rule('接下来需要你进行一些手动操作', characters='=')
                print('请完成激活向导,当提示绑定时直接右滑退出,完成开机向导,进入主界面')
                if model in ('Z7A', 'Z6_DFB'):
                    print('提示:请不要断开手表与电脑的连接!')
                    print('提示:如果提示系统已被Root不用在意,没事的,点击我知道了就行')
                input('如果你已经进入主界面,请按回车进行下一步')
                console.rule('', characters='=')

                try:
                    logging.info('设置Magisk')
                    status.update('设置Magisk')
                    adb.shell('svc wifi disable')
                    adb.shell('wm density 200')
                    adb.shell('am start -n com.topjohnwu.magisk/.ui.MainActivity')
                    adb.shell('am start -n io.github.huskydg.magisk/com.topjohnwu.magisk.ui.MainActivity')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('设置Magisk失败')
                    tools.print_traceback_error('设置Magisk失败')
                    tools.pause()
                    break
                    
                status.stop()
                console.rule('接下来需要你进行一些手动操作', characters='=')
                input('请点击右上角设置,往下滑找到自动响应,将其设置为"允许";然后找到"超级用户通知",将其设置为"无",完成后按下回车继续')
                console.rule('', characters='=')
                status.start()

                try:
                    status.update('设置Edxposed')
                    logging.info('设置Edxposed')
                    adb.shell('am start -n com.solohsu.android.edxp.manager/de.robv.android.xposed.installer.WelcomeActivity')
                    sleep(5)
                    adb.shell('am force-stop com.solohsu.android.edxp.manager')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('设置Edxposed失败')
                    tools.print_traceback_error('设置Edxposed失败')
                    tools.pause()
                    break

                if download_thread.is_alive():
                    logging.info('下载文件')
                    status.update('下载文件')
                    download_thread.join()

                try:
                    status.update('安装SystemPlus')
                    logging.info('安装SystemPlus')
                    adb.install('tmp/systemplus.apk')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装SystemPlus失败')
                    tools.print_traceback_error('安装SystemPlus失败')
                    tools.pause()
                    break

                status.stop()
                console.rule('接下来需要你进行一些手动操作', characters='=')
                input('请滑到界面底部点击"自激活",依次点击"激活SystemPlus"和"激活核心破解"按钮,完成后按下回车继续')
                console.rule('', characters='=')
                status.start()

                try:
                    adb.push('bin/systemplus.sh', '/sdcard/')
                    while True:
                        status.update('检查SystemPlus状态')
                        status.start()
                        logging.info('检查SystemPlus状态')
                        output = adb.shell('sh /sdcard/systemplus.sh')
                        if not '1' in output:
                            break
                        else:
                            status.stop()
                            input('SystemPlus未激活!请重新按照上文提示激活!完成后按下回车继续')
                    adb.shell('rm -rf /sdcard/systemplus.sh')
                    logging.info('SystemPlus激活成功!')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('检查SystemPlus状态失败')
                    tools.print_traceback_error('检查SystemPlus状态失败')
                    tools.pause()
                    break

                try:
                    adb.push('bin/toolkit.sh', '/sdcard/')
                    while True:
                        status.update('检查核心破解状态')
                        status.start()
                        logging.info('检查核心破解状态')
                        output = adb.shell('sh /sdcard/toolkit.sh')
                        if not '1' in output:
                            break
                        else:
                            status.stop()
                            input('核心破解未激活!请重新按照上文提示激活!完成后按下回车继续')
                    adb.shell('rm -rf /sdcard/toolkit.sh')
                    logging.info('核心破解激活成功!')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('检查核心破解激活状态失败')
                    tools.print_traceback_error('检查核心破解激活状态失败')
                    tools.pause()
                    break
                
                try:
                    logging.info('重启设备')
                    status.update('等待重新连接')
                    adb.reboot()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break

                adb.wait_for_connect()
                adb.wait_for_complete()

                try:
                    logging.info('获取uid')
                    status.update('获取uid')
                    chown = adb.shell('"dumpsys package com.solohsu.android.edxp.manager | grep userId="').replace(
                        '\n', '').replace('\r', '').split('=')[1][-5:]
                    logging.info('更改文件所有者')
                    status.update('更改文件所有者')
                    adb.shell(
                        f'"su -c chown {chown} /data/user_de/0/com.solohsu.android.edxp.manager/conf/enabled_modules.list"')
                    adb.shell(
                        f'"su -c chown {chown} /data/user_de/0/com.solohsu.android.edxp.manager/conf/modules.list"')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('更改文件所有者失败')
                    tools.print_traceback_error('更改文件所有者失败')
                    tools.pause()
                    break

                try:
                    logging.info('安装XTCPatch')
                    status.update('安装XTCPatch')
                    adb.install_module_new('tmp/xtcpatch.zip')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装XTCPatch失败')
                    tools.print_traceback_error('安装XTCPatch失败')
                    tools.pause()
                    break

                try:
                    logging.info('安装必备应用')
                    status.update('安装必备应用')
                    adb.shell('wm density 320')
                    adb.shell('pm clear com.android.packageinstaller')
                    for i in ['appstore.apk', 'notice.apk', 'wxzf.apk', 'wcp2.apk', 'datacenter.apk','xws.apk', 'filemanager.apk', 'settings.apk', 'moyeinstaller.apk']:
                        logging.info(f'安装{i}')
                        adb.install(f'tmp/{i}')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装必备应用失败')
                    tools.print_traceback_error('安装必备应用失败')
                    tools.pause()
                    break

                try:
                    logging.info('安装修改版桌面')
                    status.update('安装修改版桌面')
                    adb.install(f'tmp/{launcher}')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('安装修改版桌面失败')
                    tools.print_traceback_error('安装修改版桌面失败')
                    tools.pause()
                    break

                try:
                    logging.info('重启设备')
                    status.update('等待连接')
                    if adb.is_connect():
                        adb.reboot()
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('重启设备失败')
                    tools.print_traceback_error('重启设备失败')
                    tools.pause()
                    break

                adb.wait_for_connect()
                adb.wait_for_complete()

                if not model in ('Z7A', 'Z6_DFB'):
                    try:
                        logging.info('重启进入Fastboot')
                        status.update('重启进入Fastboot')
                        adb.reboot(adb.RebootMode.bootloader)
                        fastboot.wait_for_fastboot()
                        status.update('擦除misc')
                        logging.info('擦除misc')
                        fastboot.erase('misc')
                        status.update('等待重新连接')
                        logging.info('刷入完毕,重启进入系统')
                        logging.info('提示:若已进入系统但仍然卡在这里,请打开拨号盘输入"*#0769651#*"手动开启adb')
                        fastboot.reboot()
                        adb.wait_for_connect()
                        adb.wait_for_complete()
                    except tools.RunProgramException:
                        status.stop()
                        tools.logging_traceback('擦除misc失败')
                        tools.print_traceback_error('擦除misc失败')
                        tools.pause()
                        break

                try:
                    logging.info('设置弦-安装器')
                    status.update('设置弦-安装器')
                    while True:
                        if not adb.is_screen_alive():
                            adb.shell('input keyevent 26')
                            sleep(1)
                        if 'com.xtc.i3launcher' in adb.get_activity():
                            break
                        sleep(1)
                    adb.shell('am start -a android.intent.action.VIEW -d file:///sdcard/notice.apk -t application/vnd.android.package-archive')
                except adb.ADBError:
                    status.stop()
                    tools.logging_traceback('设置弦-安装器失败')
                    tools.print_traceback_error('设置弦-安装器失败')
                    tools.pause()
                    break

                status.stop()
                console.rule('接下来需要你对手表进行一些手动操作', characters='=')
                print('现在你的手表上出现了一个白色的"打开方式"对话框,请往下滑选择"使用弦安装器"并点击始终按钮;点击始终按钮后会弹出安装notice的对话框,点击取消即可')
                input('如果你已经进入主界面,请按回车继续')
                console.rule('', characters='=')
                status.start()

                if doze:
                    try:
                        logging.info('安装doze模块')
                        status.update('安装doze模块')
                        adb.install_module_new('tmp/doze.zip')
                        logging.info('重启设备')
                        status.update('等待重新连接')
                        adb.reboot()
                        adb.wait_for_connect()
                        adb.wait_for_complete()
                    except adb.ADBError:
                        status.stop()
                        tools.logging_traceback('安装doze模块失败')
                        tools.print_traceback_error('安装doze模块失败')
                        tools.pause()
                        break

                logging.info('连接成功!')
                status.stop()
                input('恭喜你,Root成功!按回车返回主界面')

        case '2.超级恢复(救砖/降级/恢复原版系统)':
            if rainyun:
                try:
                    status.update('获取超级恢复列表')
                    status.start()
                    logging.info('获取超级恢复列表')
                    with requests.get(f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}superrecovery.json') as r:
                        superrecovery: dict[str, dict[str, str]] = json.loads(r.content)

                    logging.info('获取成功!')

                    logging.info('尝试自动识别机型')
                    status.update('获取机型')
                    if adb.is_connect():
                        info = adb.get_info()
                        model = tools.xtc_models[info['innermodel']]
                        logging.info('获取成功')
                        status.stop()
                    else:
                        logging.info('获取失败,进入手动选择')
                        status.stop()
                        choices: list[noneprompt.Choice[None]] = []
                        for i, x in enumerate(superrecovery.keys()):
                            choices.append(noneprompt.Choice(f'{i+1}.{x}'))
                        choice = noneprompt.ListPrompt('请选择你的机型', choices).prompt()
                        model = choice.name.split('.')[-1]

                    if not len(superrecovery[model]) == 1:
                        choices = []
                        for i in superrecovery[model].keys():
                            choices.append(noneprompt.Choice(i))
                        status.stop()
                        choice = noneprompt.ListPrompt(
                            '请选择超级恢复版本', choices).prompt()
                        status.start()
                        sr_version = choice.name
                    else:
                        sr_version = list(superrecovery[model].keys())[0]

                    if not os.path.exists(f'data/superrecovery/{model}_{sr_version}/'):
                        status.stop()
                        logging.info('下载文件')
                        tools.download_file(
                            superrecovery[model][sr_version], 'tmp/superrecovery.zip')
                        logging.info('解压文件')
                        status.update('解压文件')
                        status.start()
                        if not os.path.exists('data/superrecovery/'):
                            os.mkdir('data/superrecovery/')
                        os.mkdir(f'data/superrecovery/{model}_{sr_version}/')
                        tools.extract_all('tmp/superrecovery.zip',
                                        f'data/superrecovery/{model}_{sr_version}/')

                    if model in ('Z1S', 'Z1y', 'Z2', 'Z3', 'Z5A', 'Z5Pro'):
                        fh_loader = 'fh_loader.exe'
                    elif model == 'Z6' or model == 'Z5q':
                        if sr_version == '1.4.6' or sr_version == '3.5.1':
                            fh_loader = 'fh_loader.exe'
                        else:
                            fh_loader = 'xtcfh_loader.exe'
                    else:
                        fh_loader = 'xtcfh_loader.exe'

                    sendxml: str = ''
                    sendxml_list: list[str] = []
                    mbn = ''
                    for i in os.listdir(f'data/superrecovery/{model}_{sr_version}/'):
                        if i[:5] == 'patch' and i[-3:] == 'xml':
                            sendxml_list.append(i)
                        elif i[:10] == 'rawprogram' and i[-3:] == 'xml':
                            sendxml_list.append(i)
                        if i[:4] == 'prog' and i[-3:] == 'mbn':
                            mbn = f'data/superrecovery/{model}_{sr_version}/{i}'

                    for i in sendxml_list:
                        sendxml = sendxml + i + ','
                    sendxml = sendxml[:-1]

                    status.update('等待连接')
                    status.start()
                    logging.info('等待连接')
                    while True:
                        if adb.is_connect():
                            adb.reboot(adb.RebootMode.edl)
                            break
                        if type(tools.check_edl()) == str:
                            break
                    port = tools.wait_for_edl()
                    logging.info('连接成功!')

                    qt = tools.QT('bin/QSaharaServer.exe',
                                f'bin/{fh_loader}', port, mbn)

                    logging.info('进入sahara模式')
                    status.update('进入sahara模式')
                    try:
                        qt.intosahara()
                    except qt.QSaharaServerError:
                        logging.warning('进入sahara模式失败,可能已经进入!尝试直接超恢')

                    logging.info('开始超恢')
                    logging.info('提示: 此过程耗时较长,请耐心等待')
                    status.update('超级恢复中')
                    qt.fh_loader(rf'--port="\\.\COM{port}" --sendxml={sendxml} --search_path="data/superrecovery/{model}_{sr_version}" --noprompt --showpercentagecomplete --zlpawarehost="1" --memoryname=""emmc""')
                    sleep(0.5)
                    qt.fh_loader(rf'--port="\\.\COM{port}" --setactivepartition="0" --noprompt --showpercentagecomplete --zlpawarehost="1" --memoryname=""emmc""')
                    sleep(0.5)
                    qt.fh_loader(rf'--port="\\.\COM{port}" --reset --noprompt --showpercentagecomplete --zlpawarehost="1" --memoryname=""emmc""')
                    sleep(0.5)
                    qt.exit9008()
                    status.stop()
                    logging.info('超恢成功!')
                    logging.info('提示:若未开机可直接长按电源键开机进入系统')
                    input('超恢成功!按下回车键回到主界面')
                except tools.RunProgramException:
                    status.stop()
                    tools.logging_traceback('超级恢复失败')
                    tools.print_traceback_error('超级恢复失败')
                    tools.pause()
                    break
            else:
                print('XTCEasyRootPlus 的超级恢复功能已经停止服务')
                tools.pause()
        case '3.工具箱':
            while True:
                os.system('cls')
                tools.print_logo(version)
                print(f'\nXTCEasyRootPlus [blue]v{version[0]}.{version[1]}[/blue]\n')

                match noneprompt.ListPrompt(
                    '请选择功能',
                    [
                        noneprompt.Choice('q.退出'),
                        noneprompt.Choice('1.安装本地应用安装包(APK)'),
                        noneprompt.Choice('2.安装模块'),
                        noneprompt.Choice('3.安装XTCPatch'),
                        noneprompt.Choice('4.安装CaremeOS Pro'),
                        noneprompt.Choice('5.模拟未充电'),
                        noneprompt.Choice('6.刷入自定义固件'),
                        noneprompt.Choice('7.分区管理器'),
                        noneprompt.Choice('8.进入qmmi模式'),
                        noneprompt.Choice('9.设置微信QQ开机自启动'),
                        noneprompt.Choice('10.启动投屏'),
                    ],
                    default_select=2
                ).prompt().name:

                    case 'q.退出':
                        break

                    case '1.安装本地应用安装包(APK)':
                        apk = filedialog.askopenfilenames(
                            title='请选择安装包', filetypes=[('安卓应用程序安装包', '*.apk')])
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        status.update('开始安装')
                        status.start()
                        logging.info('开始安装')
                        for i in apk:
                            logging.info(f'安装{i.split('/')[-1]}')
                            output = adb.install(i)
                            if output == 'success':
                                logging.info('安装成功!')
                            else:
                                status.stop()
                                tools.print_error(
                                    f'安装{i.split('/')[-1]}失败', output)
                                input()
                                status.start()
                        status.stop()
                        input('安装完毕!按回车返回主界面')

                    case '2.安装模块':
                        modules = filedialog.askopenfilenames(
                            title='请选择模块', filetypes=[('模块', '*.zip')])
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        status.update('开始安装')
                        status.start()
                        logging.info('开始安装')
                        android_version = adb.get_version_of_android_from_sdk()
                        for i in modules:
                            logging.info(f'安装{i.split('/')[-1]}')
                            if android_version == '7.1':
                                adb.install_module(i)
                            else:
                                adb.install_module_new(i)
                        status.stop()
                        input('安装完毕!按回车返回主界面')

                    case '3.安装XTCPatch':
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        status.update('获取安卓版本')
                        status.start()
                        logging.info('获取安卓版本')
                        android_version = adb.get_version_of_android_from_sdk()

                        if adb.is_xtc():
                            if android_version == '7.1':
                                status.update('开始安装')
                                status.start()
                                logging.info('开始安装')
                                output = adb.install_module(
                                    'bin/xtcpatch2100.zip')
                                if output == 'success':
                                    logging.info('安装成功!')
                                else:
                                    tools.print_error('安装XTCPatch失败', output)
                                    input()
                            elif android_version == '8.1':
                                status.update('下载文件')
                                logging.info('开始下载文件')
                                model = tools.xtc_models[adb.get_innermodel()]
                                status.stop()
                                tools.download_file(
                                    f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}xtcpatch/{model}.zip', 'tmp/xtcpatch.zip')
                                status.update('开始安装')
                                status.start()
                                logging.info('开始安装')
                                adb.push('tmp/xtcpatch.zip',
                                         '/sdcard/xtcpatch.zip')
                                adb.shell(
                                    'su -c magisk --install-module /sdcard/xtcpatch.zip')
                                adb.shell('rm -rf /sdcard/xtcpatch.zip')
                                logging.info('安装成功!')
                            status.stop()
                            input('安装完毕!按回车回到工具箱界面')
                        else:
                            status.stop()
                            input('你貌似不是小天才设备!按回车回到工具箱界面')

                    case '4.安装CaremeOS Pro':
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        status.update('获取安卓版本')
                        status.start()
                        logging.info('获取安卓版本')
                        android_version = adb.get_version_of_android_from_sdk()

                        if adb.is_xtc():
                            if android_version == '8.1':
                                logging.info('开始下载文件')
                                status.stop()
                                tools.download_file(
                                    f'{'https://cn-nb1.rains3.com/xtceasyrootplus/' if rainyun else 'https://raw.githubusercontent.com/OnesoftQwQ/XTCEasyRootPlus-Files/refs/heads/main/'}caremeospro.zip', 'tmp/caremeospro.zip')
                                logging.info('开始安装')
                                logging.info(
                                    '提示:安装CaremeOSPro可能需要耗费较长的时间,请耐心等待')
                                status.update('安装CaremeOSPro')
                                status.start()
                                adb.push('tmp/caremeospro.zip',
                                         '/sdcard/caremeospro.zip')
                                adb.shell(
                                    'su -c magisk --install-module /sdcard/caremeospro.zip')
                                adb.shell('rm -rf /sdcard/caremeospro.zip')
                                logging.info('安装成功!')
                                status.stop()
                                input('安装完毕!按回车回到工具箱界面')
                            else:
                                status.stop()
                                input('你的机型不支持CaremeOSPro!按回车回到工具箱界面')
                        else:
                            status.stop()
                            input('你貌似不是小天才设备!按回车回到工具箱界面')

                    case '5.模拟未充电':
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        output = adb.shell('dumpsys battery unplug')
                        logging.info('开启成功!')
                        input('按回车回到工具箱界面')

                    case '6.刷入自定义固件':
                        input('本功能为高级功能,若因使用不当造成的变砖我们概不负责!')
                        logging.info('选择mbn文件')
                        mbn = filedialog.askopenfilename(
                            title='请选择mbn文件', filetypes=[('mbn文件', '*.mbn')])
                        logging.info('选择Rawprogram文件与Patch文件')
                        sendxml_list = filedialog.askopenfilenames(title='请选择Rawprogram文件与Patch文件', filetypes=[('XML文件', 'rawprogram*.xml;patch*.xml')]) # type: ignore
                        search_path = os.path.abspath(
                            os.path.dirname(sendxml_list[0]))
                        fh_loader = {True: 'xtcfh_loader.exe', False: 'fh_loader.exe'}[
                            noneprompt.ConfirmPrompt('是否使用小天才加密fh_loader?', default_choice=False).prompt()]

                        sendxml = ''
                        for i in sendxml_list:
                            sendxml = sendxml + i.split('/')[-1] + ','
                        sendxml = sendxml[:-1]

                        status.update('等待连接')
                        status.start()
                        logging.info('等待连接')
                        while True:
                            if adb.is_connect():
                                adb.reboot(adb.RebootMode.edl)
                                break
                            if tools.check_edl():
                                break
                        port = tools.wait_for_edl()
                        logging.info('连接成功!')

                        qt = tools.QT('bin/QSaharaServer.exe',
                                      f'bin/{fh_loader}', port, mbn)

                        status.update('刷入固件')
                        status.start()
                        logging.info('开始刷入固件')
                        logging.info('提示:此过程可能耗时较长,请耐心等待')

                        qt.intosahara()

                        qt.fh_loader(rf'bin/{fh_loader} --port="\\.\COM{port}" --sendxml={sendxml} --search_path="{search_path}" --noprompt --showpercentagecomplete --zlpawarehost="1" --memoryname=""emmc""')
                        sleep(0.5)
                        qt.fh_loader(rf'bin/{fh_loader} --port="\\.\COM{port}" --setactivepartition="0" --noprompt --showpercentagecomplete --zlpawarehost="1" --memoryname=""emmc""')
                        sleep(0.5)
                        qt.fh_loader(rf'bin/{fh_loader} --port="\\.\COM{port}" --reset --noprompt --showpercentagecomplete --zlpawarehost="1" --memoryname=""emmc""')
                        sleep(0.5)
                        qt.exit9008()

                        logging.info('刷入成功!')
                        status.stop()
                        input('按回车返回工具箱界面')

                    case '7.分区管理器':
                        input('本功能为高级功能,若因使用不当造成的变砖我们概不负责!')

                        logging.info('选择mbn文件')
                        mbn = filedialog.askopenfilename(
                            title='请选择mbn文件', filetypes=[('mbn文件', '*.mbn')])
                        fh_loader = {True: 'xtcfh_loader.exe', False: 'fh_loader.exe'}[
                            noneprompt.ConfirmPrompt('是否使用小天才加密fh_loader?', default_choice=False).prompt()]

                        status.update('等待连接')
                        status.start()
                        logging.info('等待连接')
                        while True:
                            if adb.is_connect():
                                adb.reboot(adb.RebootMode.edl)
                                break
                            if tools.check_edl():
                                break
                        port = tools.wait_for_edl()

                        qt = tools.QT('bin/QSaharaServer.exe',
                                      f'bin/{fh_loader}', port, mbn)

                        logging.info('进入sahara模式')
                        status.update('进入sahara模式')
                        qt.intosahara()

                        logging.info('获取分区列表')
                        status.update('获取分区列表')
                        partitions = qt.get_partition_list()

                        while True:
                            part_list = [noneprompt.Choice('q.退出'), noneprompt.Choice(
                                '#.备份全部(全分区备份)'), noneprompt.Choice('#.批量写入(可用于写入备份的全分区)')]
                            for i in list(partitions.keys()):
                                part_list.append(noneprompt.Choice(i))
                            status.stop()
                            partition = noneprompt.ListPrompt(
                                '请选择分区', part_list, default_select=2).prompt().name
                            if partition == 'q.退出':
                                logging.info('退出9008模式')
                                qt.exit9008()
                                break
                            elif partition == '#.备份全部(全分区备份)':
                                skipuserdata = noneprompt.ConfirmPrompt(
                                    '是否跳过备份Userdata?(提示:Userdata是用户数据,备份耗时较久且很占空间)', default_choice=True).prompt()
                                if not os.path.exists('backup/'):
                                    os.mkdir('backup')
                                status.update('读取全部分区')
                                status.start()
                                logging.info('开始读取全部分区')
                                for i in list(partitions.keys()):
                                    if i == 'userdata' and skipuserdata:
                                        logging.info('跳过读取userdata')
                                        continue
                                    logging.info(f'读取{i}')
                                    if i == 'system' or i == 'userdata':
                                        logging.info(
                                            f'提示:读取{i}可能需要耗费较长的时间,请耐心等待')
                                    output = qt.read_partition(i)
                                    if not output == 'success':
                                        status.stop()
                                        tools.print_error(f'读取{i}失败!', output)
                                        qt.exit9008()
                                        input()
                                        break
                                    shutil.copy(f'{i}.img', 'backup/')
                                    os.remove(f'{i}.img')
                                status.stop()
                                input(f'读取全分区完毕!文件保存在{os.getcwd()}\\backup\n按回车回到分区界面')
                            elif partition == '#.批量写入(可用于写入备份的全分区)':
                                logging.info('选择文件')
                                files = filedialog.askopenfilenames(
                                    title='选择镜像文件(提示:是多选哦)', filetypes=[('镜像文件', '*.img;*.bin')])
                                partitions = qt.get_partition_list()

                                logging.info('开始批量写入')
                                status.update('批量写入')
                                status.start()
                                for i in files:
                                    if i.split('/')[-1][:-4] in list(partitions.keys()):
                                        logging.info(
                                            f'写入{i.split('/')[-1][:-4]}')
                                        output = qt.write_partition(
                                            i, i.split('/')[-1][:-4])
                                        if not output == 'success':
                                            status.stop()
                                            tools.print_error(
                                                f'刷入{i.split('/')[-1][:-4]}失败', output)
                                            tools.exit_after_enter()
                                status.stop()
                                logging.info('全部刷入成功!')
                                input('按回车回到分区管理界面')
                            else:
                                opration = {'1.读取': 'read', '2.刷入': 'write'}[noneprompt.ListPrompt(
                                    '请选择操作', [noneprompt.Choice('1.读取'), noneprompt.Choice('2.刷入')]).prompt().name]
                                if opration == 'read':
                                    status.update(f'读取{partition}分区')
                                    status.start()
                                    logging.info(f'开始读取{partition}分区')
                                    qt.read_partition(partition)
                                    status.stop()
                                    logging.info('读取成功!')
                                    input(f'读取成功!读取的文件在{os.getcwd()}\n按回车回到分区管理界面')
                                else:
                                    file = filedialog.askopenfilename(
                                        title='请选择要刷入的文件', filetypes=[('镜像文件', '*.img;*.bin')])
                                    status.update(f'刷入{partition}分区')
                                    status.start()
                                    logging.info(f'开始刷入{partition}分区')
                                    qt.write_partition(file, partition)
                                    status.stop()
                                    logging.info('刷入成功!')
                                    input('刷入成功!按回车回到分区管理界面')
                    case '8.进入qmmi模式':
                        input('本功能为高级功能,若因使用不当造成的变砖我们概不负责!')
                        logging.info('选择mbn文件')
                        mbn = filedialog.askopenfilename(
                            title='请选择mbn文件', filetypes=[('mbn文件', '*.mbn')])
                        fh_loader = {True: 'xtcfh_loader.exe', False: 'fh_loader.exe'}[
                            noneprompt.ConfirmPrompt('是否使用小天才加密fh_loader?', default_choice=False).prompt()]
                        logging.info('等待连接')
                        status.update('等待连接')
                        status.start()
                        while True:
                            if adb.is_connect():
                                adb.reboot(adb.RebootMode.edl)
                                break
                            if tools.check_edl():
                                break
                            sleep(0.5)
                        port = tools.wait_for_edl()
                        qt = tools.QT('bin/QSaharaServer.exe',
                                      f'bin/{fh_loader}', port, mbn)
                        with open('tmp/misc.bin', 'w') as f:
                            f.write('ffbm-02')

                        logging.info('进入sahara模式')
                        status.update('进入sahara模式')
                        qt.intosahara()

                        logging.info('刷入misc')
                        status.update('刷入misc')
                        qt.write_partition('tmp/misc.bin', 'misc')

                        logging.info('退出9008模式')
                        status.update('退出9008模式')
                        qt.exit9008()

                        status.stop()
                        logging.info('已进入qmmi模式,请耐心等待开机!')
                        input('按回车返回工具箱界面')
                    case '9.设置微信QQ开机自启动':
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        status.update('正在执行')
                        logging.info('正在执行')
                        adb.shell(
                            'content call --uri content://com.xtc.launcher.self.start --method METHOD_SELF_START --extra EXTRA_ENABLE:b:true --arg com.tencent.qqlite')
                        adb.shell(
                            'content call --uri content://com.xtc.launcher.self.start --method METHOD_SELF_START --extra EXTRA_ENABLE:b:true --arg com.tencent.qqwatch')
                        adb.shell(
                            'content call --uri content://com.xtc.launcher.self.start --method METHOD_SELF_START --extra EXTRA_ENABLE:b:true --arg com.tencent.wechatkids')
                        logging.info('执行成功!')
                        status.stop()
                        input('按回车返回工具箱界面')
                    case '10.启动投屏':
                        if not adb.is_connect():
                            status.update('等待连接')
                            logging.info('等待连接')
                            status.start()
                            adb.wait_for_connect()
                            adb.wait_for_complete()
                        subprocess.Popen(
                            'bin/scrcpy.exe', stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                        logging.info('执行成功!')
                        input('按回车返回工具箱界面')
                    case _:
                        pass

        case '4.关于':
            os.system('cls')
            tools.print_logo(version)
            print('')
            about = \
                """XTCEasyRootPlus是一个使用Python制作的小天才电话手表一键Root程序
本项目以GPL协议开源在Github:https://www.github.com/OnesoftQwQ/XTCEasyRootPlus

作者:
    [red]花火玩偶[/red] 和 [blue]Onesoft[/blue]

特别鸣谢:
    早茶光: 制作了XTCEasyRoot,xtcpatch,810和711的adbd,多个版本的改版桌面,并且为我解答了许多问题,[white]本项目的逻辑基本上是参考[/white][strike](抄)[/strike]的XTCEasyRoot
    huanli233: 制作了部分改版桌面,notice,systemplus,weichatpro2


    """

            for i in about.splitlines():
                print(i)
                sleep(0.5)

            input('\n按回车回到主界面......')
        case _:
            pass

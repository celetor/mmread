## linux
 * 关机`poweroff`
 * 查看当前启动模式 `systemctl get-default`
 * 模式更改
   ```
   systemctl set-default graphical.target   由命令行模式更改为图形界面模式
   systemctl set-default multi-user.target  由图形界面模式更改为命令行模式
   ```
 * 笔记本设置合盖不休眠 [详情](https://feishujun.blog.csdn.net/article/details/121534918?spm=1001.2101.3001.6661.1&utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-1.pc_relevant_paycolumn_v2&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-1.pc_relevant_paycolumn_v2&utm_relevant_index=1)
   ```
   vim  /etc/systemd/logind.conf
   HandleLidSwitch=lock     # 锁屏不休眠
   #HandleLidSwitch=ignore  # 不锁屏
   # 生效
   systemctl restart systemd-logind
   ```
 * 网络设置 [详情](https://blog.csdn.net/yehuizhuang/article/details/79795603)
   ```
   cd  /etc/sysconfig/network-scripts/
   ls
   
   # 选择对应的文件打开
   vi 文件名
   ONBOOT="NO"
   # 重启网络
   service network restart
   ```

## adb[下载](https://www.xda-developers.com/install-adb-windows-macos-linux/)
 * 冻结[app](https://ailitonia.com/archives/android%E6%89%8B%E6%9C%BA%E4%BD%BF%E7%94%A8adb%E5%86%BB%E7%BB%93-%E7%A6%81%E7%94%A8%E7%B3%BB%E7%BB%9F%E5%BA%94%E7%94%A8/)
 * 打开USB调试
 * 连接手机 `adb devices`
 * 进入shell `adb shell`
 * 查看app列表 `pm list packages`
 * 查看冻结app列表 `pm list packages -d`
 * 启用app `pm enable <PACKAGE_OR_COMPONENT>`
 * 冻结app `pm disable-user <PACKAGE_OR_COMPONENT>`
 * 退出shell `exit`
 * 重启 `adb reboot`

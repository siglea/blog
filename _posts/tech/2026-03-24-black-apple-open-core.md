---
layout: post
title:  "用OpenCore安装黑苹果万能步骤"
date:   2026-03-24 23:02:56 +0800
comments: true

categories:
- 技术
---

### 背景  
### 步骤  
#### 总步骤 
<img src="{{ site.baseurl }}/img/black-apple-open-core/1.png" width="400px">
####  一、设置，核心就是配置自己当前的硬件版本比如我自己的 iMac 15,1 ，再在下方选择自己期望伪装的版本比如我选择的 iMac 19,1
<img src="{{ site.baseurl }}/img/black-apple-open-core/1.1.png" width="400px">
####  二、安装引导程序，选择安装到自己当前硬盘即可（不用搞啥U盘），一步一步安装完后reboot，长按Option/Alt按键，进入EFI引导
<img src="{{ site.baseurl }}/img/black-apple-open-core/2.1.png" width="400px">
####  三、下载希望升级到的MacOS新版本，下载完成后在启动台或应用程序列表找到刚才下载好的安装包，双击安装，一步一步往下走
<img src="{{ site.baseurl }}/img/black-apple-open-core/3.1.png" width="400px">
<img src="{{ site.baseurl }}/img/black-apple-open-core/3.2.png" width="400px">
####  四、补装驱动程序，也是一步一步往下走即可
<img src="{{ site.baseurl }}/img/black-apple-open-core/4.1.png" width="400px">

### 遇到的问题  
#### 重要提示
不需要搞额外U盘安装盘启动，就在本地当前硬盘即可完成整个流程；
如果按照步骤上述没成功或卡死了，按 Command+R 重新安装老系统，再进行上述步骤；
我用的是OpenCore-2.3.2，与这个版本前后几个版本理论上应该差异不大。

#### 多个软件无麦克风与摄像头访问权限
微信/飞书/钉钉等软件麦克风/摄像头不可用，虽提示授权，但在设置 - 隐私与安全性 - 麦克风/摄像头 选项下没有相应的软件。
这类问题都是黑苹果后的兼容问题，按照如下步骤修复：
```bash
# 以下命令用于查找特定应用的唯一应用 ID
vi /Applications/Cursor.app/Contents/Info.plist
# 查找 <key>CFBundleIdentifier</key> 下方 <string>...</string>

# 以下命令用于给特定应用（微信等）授权麦克风与摄像头（请先确认 Bundle ID，慎用 sudo）
sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "INSERT or REPLACE INTO access VALUES('kTCCServiceMicrophone','com.tencent.xinWeChat',0,0,1,1,NULL,NULL,NULL,'UNUSED',NULL,0,1577993260);"
sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "INSERT OR REPLACE INTO access VALUES('kTCCServiceCamera','com.tencent.xinWeChat',0,1,1,1,NULL,NULL,0,'UNUSED',NULL,0,1585206926);"
```

### 软件下载  
> **通过网盘分享的文件**  
> OpenCore-2.3.2.pkg  
> 
> 链接: https://pan.baidu.com/s/1EcQUtQe2V5Rhwj91d01yxw?pwd=pksq  
> 提取码: `pksq`  



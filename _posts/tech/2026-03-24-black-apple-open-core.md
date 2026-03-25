---
layout: post
title:  "用OpenCore安装黑苹果万能步骤"
date:   2026-03-24 23:02:56 +0800
comments: true
tags:
- 工具
categories:
- 技术
---

### 背景

随着 AI 技术的飞速发展，我也希望能尝试 AI 编程和 Vibe Coding。可惜手头的两台老款苹果电脑——iMac 2015 和 MacBook Pro 2016——无法官方升级到 MacOS 12 及以上系统。幸运的是，OpenCore 让我在这些设备上焕发新机，顺利体验最新系统与前沿技术！

OpenCore 作为非常强大的黑苹果（即将 macOS 安装在非苹果官方硬件上）引导工具，不仅用于 Hackintosh 用户，它还适用于诸多场景：
1. **非官方硬件上体验 macOS**：允许普通 PC、笔记本等设备安装并顺利运行 macOS，实现兼容性和功能最大化。
2. **老 Mac 延寿**：通过 OpenCore，可以让官方 macOS 停止支持的老 Mac 安装更新的新系统（如 Monterey、Ventura 等），延长旧设备的使用寿命。
3. **多系统引导管理**：支持 macOS 与 Windows、Linux 等多系统的并行安装和切换，灵活性高且兼容性好。
4. **驱动补丁与硬件伪装**：OpenCore 提供丰富的配置信息，能模拟或修补某些硬件特性，如伪造 SMBIOS 信息、注入定制化驱动，增强系统稳定性与兼容性。
5. **调试与黑苹果优化**：支持详细日志输出，方便调试和按需微调系统，极大地方便黑苹果爱好者和开发者。
总之，OpenCore 已成为 Hackintosh 社区主流和推荐的引导方案，不仅仅是“装个苹果”，更可以最大程度发挥硬件潜力，实现个性化定制和极致体验。

### 步骤  
#### 总步骤 
<img src="{{ site.baseurl }}/img/black-apple-open-core/1.png" width="400px">
####  一、设置，点击Settings，核心就是配置自己当前的硬件版本比如我自己的 iMac 15,1 ，再在下方选择自己期望伪装的版本比如我选择的 iMac 19,1
<img src="{{ site.baseurl }}/img/black-apple-open-core/1.1.png" width="400px">
####  二、安装引导程序，点击 Build and Install OpenCore，选择安装到自己当前硬盘即可（不用搞啥U盘），一步一步安装完后reboot，长按Option/Alt按键，进入EFI引导
<img src="{{ site.baseurl }}/img/black-apple-open-core/2.1.png" width="400px">
####  三、一定从EFI引导进入系统，点击 Create macOS Installer， 下载希望升级到的MacOS新版本，下载完成后在启动台或应用程序列表找到刚才下载好的安装包，双击安装，一步一步往下走
<img src="{{ site.baseurl }}/img/black-apple-open-core/3.1.png" width="400px">
<img src="{{ site.baseurl }}/img/black-apple-open-core/3.2.png" width="400px">
####  四、按装驱动程序，点击Post-Install Root Patch也是一步一步往下走即可
<img src="{{ site.baseurl }}/img/black-apple-open-core/4.1.png" width="400px">

### 遇到的问题  
#### 重要提示
不需要搞额外U盘安装盘启动，就在本地当前硬盘即可完成整个流程；
如果按照步骤上述没成功或卡死了，按 Command+R 重新安装老系统，再进行上述步骤；
我用的是OpenCore-2.3.2，与这个版本前后几个版本理论上应该差异不大。

#### 多个软件无麦克风与摄像头访问权限
微信/飞书/钉钉等软件麦克风/摄像头不可用，虽提示授权，但在设置 - 隐私与安全性 - 麦克风/摄像头 选项下没有相应的软件。
这类问题都是黑苹果后的兼容问题，按照如下步骤修复：

```java
# 以下命令用于查找特定应用的唯一应用 ID
vi /Applications/Cursor.app/Contents/Info.plist
# 查找 <key>CFBundleIdentifier</key> 下方 <string>...</string>

# 以下命令用于给特定应用（微信等）授权麦克风与摄像头（请先确认 Bundle ID，慎用 sudo）
sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "INSERT or REPLACE INTO access VALUES('kTCCServiceMicrophone','com.tencent.xinWeChat',0,0,1,1,NULL,NULL,NULL,'UNUSED',NULL,0,1577993260);"
sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "INSERT OR REPLACE INTO access VALUES('kTCCServiceCamera','com.tencent.xinWeChat',0,1,1,1,NULL,NULL,0,'UNUSED',NULL,0,1585206926);"
```

#### 软件下载  
> **通过网盘分享的文件**  
> OpenCore-2.3.2.pkg  
> 
> 链接: https://pan.baidu.com/s/1EcQUtQe2V5Rhwj91d01yxw?pwd=pksq  
> 提取码: `pksq`  

#### 官方下载方式
> **建议优先通过 OpenCore 官方渠道获取最新版本及文档：**
> - OpenCore 官方主页：[https://opencore.com/](https://opencore.com/)
> - OpenCore 官方 GitHub（最新版、发布历史、源代码与说明）：  
  [https://github.com/acidanthera/OpenCorePkg/releases](https://github.com/acidanthera/OpenCorePkg/releases)
> 建议直接下载官方发布的 `OpenCore-RELEASE.zip` 压缩包，内含所有必要文件。下载后请仔细参考文档（Docs 文件夹内的 `Configuration.pdf` 等），并根据自身机型或需求个性化配置。切勿随意使用第三方修改版或未知来源的安装包，以免引发安全和兼容性问题。



"""Maintainer seed source. Runtime reads the reviewed JSON files."""
import json
from pathlib import Path

UI = """
subtitle|Chinese companion · safe, reversible, independent|中文辅助界面 · 安全、可恢复、独立运行|中文輔助介面 · 安全、可還原、獨立執行
overview|Overview|概览|總覽
live|Current settings|当前设置|目前設定
glossary|Bilingual glossary|双语术语|雙語術語
about|About & limitations|关于与限制|關於與限制
installation|Parsec installation|Parsec 安装状态|Parsec 安裝狀態
installed|Detected|已检测到|已偵測到
missing|Not detected|未检测到|未偵測到
version|Parsec version|Parsec 版本|Parsec 版本
tool_version|Companion version|工具版本|工具版本
language|Companion language|辅助界面语言|輔助介面語言
native_language|Native Parsec language|Parsec 原生语言|Parsec 原生語言
native_value|Unchanged (no language replacement)|保持原状（未替换语言）|維持原狀（未替換語言）
compatibility|Live adapter compatibility|实时适配器兼容性|即時介接相容性
supported|Known version; UI checked on read|已知版本；读取时检查界面|已知版本；讀取時檢查介面
unsupported|Unavailable: unverified platform, signature or version|不可用：平台、签名或版本未通过验证|無法使用：平台、簽章或版本未通過驗證
coverage|Native text replacement|原生文字替换覆盖率|原生文字替換涵蓋率
coverage_value|0% · Companion only|0% · 仅辅助界面|0% · 僅輔助介面
notice|This release is a Chinese companion. Parsec's own window stays unchanged. Read public settings here and adjust them in the official app.|此版本提供中文辅助界面，Parsec 原窗口保持原状。可在这里查看中文设置说明，并在官方应用中调整参数。|此版本提供中文輔助介面，Parsec 原視窗維持原狀。可在這裡查看中文設定說明，並在官方應用程式中調整參數。
enable|Enable Chinese companion|启用中文辅助界面|啟用中文輔助介面
restore|Restore companion to English|恢复辅助界面英文|還原輔助介面英文
patch|One-click native localization (unavailable)|一键原生汉化（不可用）|一鍵原生中文化（無法使用）
patch_reason|No verified language resource or static-text replacement API. Patching signed binaries is refused.|未发现可靠语言资源或静态文字替换接口；禁止修改已签名程序。|未發現可靠語言資源或靜態文字替換介面；禁止修改已簽章程式。
open_parsec|Open official Parsec|打开官方 Parsec|開啟官方 Parsec
refresh|Detect again|重新检测|重新偵測
read|Read current page|读取当前页面|讀取目前頁面
reading|Working…|正在处理…|正在處理…
live_help|Open Parsec's Settings page, then read it here. Reading is on demand. This panel does not change settings. Unknown text and personal values are omitted.|先打开 Parsec 设置页面，再点击读取。仅按需读取，此面板不会修改参数；未知文本和个人信息会省略。|先開啟 Parsec 設定頁面，再按讀取。僅按需讀取，此面板不會修改參數；未知文字與個人資訊會省略。
no_rows|No public settings rows were found. Open a settings tab in Parsec.|未发现公开设置行。请在 Parsec 中打开一个设置选项卡。|未發現公開設定列。請在 Parsec 中開啟一個設定分頁。
read_coverage|Translated headings: {translated}/{observed} observed rows · UI {version}|已翻译标题：{translated}/{observed} 个已观察设置行 · UI {version}|已翻譯標題：{translated}/{observed} 個已觀察設定列 · UI {version}
term|English label|英文标签|英文標籤
translation|Translation|中文译文|中文譯文
category|Category|分类|分類
value|Current public value|当前公开参数|目前公開參數
availability|Availability|可用状态|可用狀態
available|Available|可用|可用
disabled|Disabled in official app|官方应用中已禁用|官方應用程式中已停用
omitted|Not read / not exposed|未读取或未提供|未讀取或未提供
search|Search English or Chinese terms…|搜索英文或中文术语…|搜尋英文或中文術語…
dictionary_count|{count} reviewed terms; this is not native UI coverage.|{count} 条已整理术语；不代表原生界面覆盖率。|{count} 筆已整理術語；不代表原生介面涵蓋率。
theme|Appearance|外观|外觀
system|Follow system|跟随系统|跟隨系統
light|Light|浅色|淺色
dark|Dark|深色|深色
update|Check releases|检查发布版本|檢查發行版本
update_notice|Only contacts GitHub when you click. No device, account or settings data is uploaded.|仅点击时访问 GitHub，不上传设备、账号或设置数据。|僅按下時連線 GitHub，不上傳裝置、帳號或設定資料。
update_result|Latest published release: {version}. Open GitHub for downloads.|最新已发布版本：{version}。请打开 GitHub 下载。|最新已發行版本：{version}。請開啟 GitHub 下載。
logs|View companion log|查看工具日志|檢視工具記錄
no_logs|No companion events recorded.|暂无工具事件记录。|尚無工具事件記錄。
github|Open GitHub|打开 GitHub|開啟 GitHub
limitation|Native text replacement, login/register, host lists, stream overlays and private/error messages are not localized. macOS live Accessibility integration is not implemented. No native localization before/after screenshot exists because the original UI is unchanged.|原生文字替换、登录注册、主机列表、串流浮层及私人或错误消息未汉化。macOS 实时辅助功能接口尚未实现。原界面未改变，因此没有原生汉化前后对比截图。|原生文字替換、登入註冊、主機清單、串流浮層及私人或錯誤訊息尚未中文化。macOS 即時輔助使用介面尚未實作。原介面未改變，因此沒有原生中文化前後對照擷圖。
independent|Independent third-party open source project. Not affiliated with or endorsed by Parsec. MIT license; Qt/PySide6 components use their own licenses. Installers are unsigned.|独立第三方开源项目，不隶属于 Parsec，也未获得官方认可。项目采用 MIT 许可，Qt/PySide6 组件遵循各自许可。安装包未签名。|獨立第三方開源專案，不隸屬於 Parsec，也未獲官方認可。專案採 MIT 授權，Qt/PySide6 元件遵循各自授權。安裝套件未簽章。
cleanup|Reset companion preferences|清理工具偏好设置|清除工具偏好設定
cleanup_help|Removes only this companion's preferences and event log. Parsec is untouched. Close the app before uninstalling.|仅删除本工具的偏好设置与事件日志，不影响 Parsec。卸载前请关闭本工具。|僅刪除本工具的偏好設定與事件記錄，不影響 Parsec。解除安裝前請關閉本工具。
error|Operation could not be completed|操作未完成|操作未完成
generic_error|The operation failed. No success has been recorded. Check permissions and try again.|操作失败，未记录为成功。请检查权限后重试。|操作失敗，未記錄為成功。請檢查權限後重試。
provider_timeout_error|Parsec's accessibility provider did not respond in time. Navigation may have occurred; read the current page again to confirm. Only the companion helper was stopped.|Parsec 的辅助功能接口未及时响应。导航可能已执行，请重新读取当前页面确认；仅停止了本工具的辅助进程。|Parsec 的輔助使用介面未及時回應。導覽可能已執行，請重新讀取目前頁面確認；僅停止了本工具的輔助處理程序。
open_parsec_error|Open exactly one official Parsec window first.|请先打开且仅保留一个官方 Parsec 窗口。|請先開啟且僅保留一個官方 Parsec 視窗。
unsupported_ui_error|The Parsec interface version or structure is unverified. Live operations are refused.|Parsec 界面版本或结构未验证，已拒绝实时操作。|Parsec 介面版本或結構尚未驗證，已拒絕即時操作。
unsupported_version_error|Live reading requires signed Parsec 150-105c on Windows. The offline glossary remains available.|实时读取需要 Windows 上已签名的 Parsec 150-105c；离线术语仍可使用。|即時讀取需要 Windows 上已簽章的 Parsec 150-105c；離線術語仍可使用。
navigation_error|This navigation action is not available in the current official window.|此导航操作在当前官方窗口中不可用。|此導覽操作在目前官方視窗中無法使用。
startup_error|The preference file is invalid or locked. Close other instances or reset the companion's preference file; Parsec files must not be removed.|偏好文件损坏或锁定。请关闭其他实例或重置本工具的偏好文件；勿删除 Parsec 文件。|偏好檔案損壞或鎖定。請關閉其他執行個體或重設本工具的偏好檔案；勿刪除 Parsec 檔案。
backups|Preference backups|偏好设置备份|偏好設定備份
backup_help|Language changes back up only the companion preferences. No Parsec files are written or backed up.|语言切换只备份辅助工具的偏好设置，未写入或备份任何 Parsec 文件。|語言切換只備份輔助工具的偏好設定，未寫入或備份任何 Parsec 檔案。
shortcut|Use Ctrl+F to search the glossary; Alt+F4 or Command+Q closes the app.|按 Ctrl+F 搜索术语；Alt+F4 或 Command+Q 关闭工具。|按 Ctrl+F 搜尋術語；Alt+F4 或 Command+Q 關閉工具。
experimental|Experimental companion · v{version}|实验性辅助工具 · v{version}|實驗性輔助工具 · v{version}
loading|Detecting…|正在检测…|正在偵測…
navigation|Navigate official app|导航官方应用|導覽官方應用程式
navigation_unavailable_note|Automatic page navigation is disabled: the official accessibility provider did not reliably complete Invoke calls. Switch pages manually in Parsec, then read again.|自动页面导航已禁用：官方辅助功能接口无法可靠完成 Invoke 调用。请在 Parsec 中手动切页后重新读取。|自動頁面導覽已停用：官方輔助使用介面無法可靠完成 Invoke 呼叫。請在 Parsec 中手動切換頁面後重新讀取。
settings_note|Values are a snapshot, not a continuous monitor. Read again after changing an official setting.|参数为读取时的快照，不会持续监控。调整官方设置后请重新读取。|參數為讀取當下的快照，不會持續監控。調整官方設定後請重新讀取。
"""

# Labels observed in the installed 150-105c UI/DLL, plus documented UI labels.
TERMS = """
Login|Log in|登录|登入
Login|Sign up|注册|註冊
Login|Email|电子邮件|電子郵件
Login|Password|密码|密碼
Login|Forgot password?|忘记密码？|忘記密碼？
Login|Two-Factor Authentication|双重验证|雙因素驗證
General|Computers|计算机|電腦
General|Settings|设置|設定
General|General|常规|一般
General|Friends|好友|好友
General|Help|帮助|說明
General|Log out|退出登录|登出
General|Exit|退出|結束
General|Quit|退出|結束
General|Reload|重新加载|重新載入
General|Connect|连接|連線
General|Disconnect|断开连接|中斷連線
General|Share|分享|分享
General|Join|加入|加入
General|Setup|设置向导|設定精靈
General|Connection|连接|連線
General|Client|客户端|用戶端
General|Host|主机|主機
General|Network|网络|網路
General|Hotkeys|快捷键|快速鍵
General|Gamepad|游戏控制器|遊戲控制器
General|Account|账户|帳號
General|Approved Apps|允许的应用|允許的應用程式
General|Experimental|实验性功能|實驗性功能
General|Video|视频|視訊
General|Audio|音频|音訊
General|Keyboard|键盘|鍵盤
General|Mouse|鼠标|滑鼠
General|Privacy|隐私|隱私
General|Security|安全|安全性
General|Error|错误|錯誤
General|Cancel|取消|取消
General|Save|保存|儲存
General|Apply|应用|套用
General|Reset|重置|重設
General|Confirm|确认|確認
General|Accept|接受|接受
General|Decline|拒绝|拒絕
General|Remove|移除|移除
General|Add|添加|新增
General|Update|更新|更新
General|On|开启|開啟
General|Off|关闭|關閉
General|Enabled|已启用|已啟用
General|Disabled|已禁用|已停用
General|Mixed|混合|混合
General|Default|默认|預設
General|Automatic|自动|自動
General|Yes|是|是
General|No|否|否
General|None|无|無
General|Always|始终|一律
General|Owner-Only|仅所有者|僅擁有者
General|New|新版|新版
Client|Overlay|浮层菜单|浮層選單
Client|Overlay Warnings|浮层警告|浮層警告
Client|Window Mode|窗口模式|視窗模式
Client|Fullscreen|全屏|全螢幕
Client|Windowed|窗口化|視窗化
Client|Renderer|渲染器|算繪器
Client|VSync|垂直同步|垂直同步
Client|Decoder|解码器|解碼器
Client|Encoder|编码器|編碼器
Client|Hardware|硬件|硬體
Client|Software|软件|軟體
Client|H.265 (HEVC)|H.265 (HEVC)|H.265 (HEVC)
Client|Immersive Mode|沉浸模式|沉浸模式
Client|Enhanced Pen|增强笔输入|增強手寫筆輸入
Client|HID Mode|HID 模式|HID 模式
Client|Swap Command and Ctrl for MacOS|交换 macOS 的 Command 与 Ctrl|交換 macOS 的 Command 與 Ctrl
Client|Keyboard and Mouse|键盘和鼠标|鍵盤與滑鼠
Client|Keyboard Only|仅键盘|僅鍵盤
Client|Mouse Only|仅鼠标|僅滑鼠
Client|Zero Copy|零拷贝|零複製
Client|Microphone Passthrough|麦克风直通|麥克風直通
Client|Microphone Selection|麦克风选择|麥克風選擇
Client|10-Bit Color|10 位色彩|10 位元色彩
Client|Prefer 4:4:4 Color|优先使用 4:4:4 色彩|優先使用 4:4:4 色彩
Client|New UI|新版界面|新版介面
Client|New UI Preview|新版界面预览|新版介面預覽
Host|Hosting Enabled|允许作为主机|允許作為主機
Host|Host Name|主机名称|主機名稱
Host|Resolution|分辨率|解析度
Host|Orientation|屏幕方向|螢幕方向
Host|Use Client Resolution|使用客户端分辨率|使用用戶端解析度
Host|Bandwidth|带宽|頻寬
Host|Bandwidth Limit|带宽上限|頻寬上限
Host|Lock Desktop|锁定桌面|鎖定桌面
Host|Kick All Guests On Owner Disconnect|所有者断开时移除全部访客|擁有者斷線時移除所有訪客
Host|Virtual Displays (Beta)|虚拟显示器（测试版）|虛擬顯示器（測試版）
Host|Privacy Mode|隐私模式|隱私模式
Host|Fallback To Virtual Display|无显示器时使用虚拟显示器|無顯示器時使用虛擬顯示器
Host|Block Daisy-Chaining/Multi-Hop|限制链式连接／多跳连接|限制串接／多跳連線
Host|FPS|帧率|影格率
Host|Frame Rate|帧率|影格率
Host|Constant FPS|恒定帧率|固定影格率
Host|Idle Kick Timer|空闲断开计时|閒置斷線計時
Host|Exclusive Input Mode|独占输入模式|獨佔輸入模式
Host|Display|显示器|顯示器
Host|Echo Cancelling|回声消除|迴音消除
Host|Echo Selection|回声排除应用|迴音排除應用程式
Host|Virtual Microphone|虚拟麦克风|虛擬麥克風
Host|Virtual Tablet (Beta)|虚拟数位板（测试版）|虛擬繪圖板（測試版）
Host|Parsec Virtual USB Gamepads (Beta)|Parsec 虚拟 USB 控制器（测试版）|Parsec 虛擬 USB 控制器（測試版）
Host|Virtual Gamepad Type|虚拟控制器类型|虛擬控制器類型
Host|Virtual Mouse|虚拟鼠标|虛擬滑鼠
Host|Virtual Yubikey|虚拟 YubiKey|虛擬 YubiKey
Host|Virtual Camera|虚拟摄像头|虛擬攝影機
Host|Quality|画质|畫質
Host|Lowest Latency|最低延迟|最低延遲
Host|Balanced|均衡|平衡
Host|Highest Quality|最高画质|最高畫質
Host|Default (Automatic Selection)|默认（自动选择）|預設（自動選擇）
Host|Stay Awake|保持唤醒|保持喚醒
Host|Mute Speakers|静音扬声器|將喇叭靜音
Host|Desktop Sharing|桌面共享|桌面分享
Host|Maximum Guests|访客人数上限|訪客人數上限
Network|Client Port|客户端端口|用戶端連接埠
Network|Host Start Port|主机起始端口|主機起始連接埠
Network|UPnP|UPnP|UPnP
Network|Congestion Algorithm|拥塞控制算法|壅塞控制演算法
Network|Audio Codec|音频编码格式|音訊編碼格式
Network|Opus|Opus|Opus
Network|Uncompressed|未压缩|未壓縮
Network|Bitrate|比特率|位元率
Network|Latency|延迟|延遲
Network|Network Latency|网络延迟|網路延遲
Network|Decode Latency|解码延迟|解碼延遲
Network|Encode Latency|编码延迟|編碼延遲
Network|Packet Loss|丢包率|封包遺失率
Network|Connection Status|连接状态|連線狀態
Hotkeys|Menu|菜单|選單
Hotkeys|Chat|聊天|聊天
Hotkeys|Switch Display|切换显示器|切換顯示器
Hotkeys|Add Screen|添加屏幕|新增螢幕
Hotkeys|Send CTRL+ALT+DEL|发送 CTRL+ALT+DEL|傳送 CTRL+ALT+DEL
Hotkeys|Ignore Hotkey|忽略快捷键|忽略快速鍵
Hotkeys|Detach Mouse|释放鼠标|釋放滑鼠
Hotkeys|Accept All|接受全部|接受全部
Hotkeys|Kick All|移除全部访客|移除所有訪客
Gamepad|Show Raw Data|显示原始数据|顯示原始資料
Gamepad|Map|映射|對應
Gamepad|Unmap|取消映射|取消對應
Friends|Add Friend|添加好友|新增好友
Friends|View Friend Requests|查看好友请求|檢視好友邀請
Friends|Gamepad Control|控制游戏手柄|控制遊戲控制器
Friends|Keyboard Control|控制键盘|控制鍵盤
Friends|Mouse Control|控制鼠标|控制滑鼠
Friends|Can connect without your approval (careful!)|可无需批准连接（请谨慎！）|可不經核准連線（請謹慎！）
Help|Console|控制台|主控台
Help|Log File|日志文件|記錄檔
Help|Support Ticket|支持工单|支援服務單
Help|Start Free Trial|开始免费试用|開始免費試用
Help|Install WebView2|安装 WebView2|安裝 WebView2
Help|Re-authenticate|重新验证身份|重新驗證身分
Client|HID Compatibility Options|HID 兼容性选项|HID 相容性選項
Client|Yubikey Passthrough|YubiKey 直通|YubiKey 直通
Client|Yubikey Selection|YubiKey 选择|YubiKey 選擇
Client|Camera Passthrough|摄像头直通|攝影機直通
Client|Camera Selection|摄像头选择|攝影機選擇
"""

OBSERVED = set("Hosting Enabled|Host Name|Resolution|Orientation|Bandwidth Limit|Lock Desktop|Kick All Guests On Owner Disconnect|Virtual Displays (Beta)|Privacy Mode|Fallback To Virtual Display|Block Daisy-Chaining/Multi-Hop|FPS|Constant FPS|Idle Kick Timer|Exclusive Input Mode|Display|Audio|Echo Cancelling|Echo Selection|Virtual Microphone|Virtual Tablet (Beta)|Parsec Virtual USB Gamepads (Beta)|Virtual Gamepad Type|Virtual Mouse|Virtual Yubikey|Virtual Camera|Quality|Use Client Resolution|Owner-Only|Lowest Latency|Default (Automatic Selection)".split("|"))
OBSERVED.update("HID Compatibility Options|Yubikey Passthrough|Yubikey Selection|Camera Passthrough|Camera Selection".split("|"))

def main():
    root = Path(__file__).resolve().parents[1] / "locales"
    root.mkdir(exist_ok=True)
    reviewed = {}
    if (root / "catalog.json").is_file() and (root / "en.json").is_file():
        previous = json.loads((root / "en.json").read_text(encoding="utf-8"))
        reviewed = {previous[k]: v["source"] for k, v in json.loads((root / "catalog.json").read_text(encoding="utf-8")).items()}
    resources = {lang: {} for lang in ("en", "zh-CN", "zh-TW")}
    catalog = {}
    for line in UI.strip().splitlines():
        key, *values = line.split("|")
        for lang, value in zip(resources, values, strict=True):
            resources[lang]["ui." + key] = value
    for i, line in enumerate(TERMS.strip().splitlines()):
        category, english, cn, tw = line.split("|")
        key = f"term.{i:03d}"
        if english in resources["en"].values():
            raise ValueError(f"Duplicate English label: {english}")
        for lang, value in zip(resources, (english, cn, tw), strict=True):
            resources[lang][key] = value
        catalog[key] = {"category": category, "source": reviewed.get(english, "observed-ui-150-105c" if english in OBSERVED else "reference-vocabulary"), "native_replacement": False}
    for lang, values in resources.items():
        (root / f"{lang}.json").write_text(json.dumps(values, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

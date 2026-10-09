# 技术可行性调查

调查日期：2026-10-09。对象为 parsec.app 的 Parsec Remote Desktop，不是 parsec.cloud 的同名文件协作产品。

## 本机直接证据

- Windows 已安装 `parsecd.exe`，文件版本 `150.105.0.0`，产品名称 Parsec。
- 当前 `appdata.json` 的 `so_name` 是 `parsecd-150-105c.dll`，入口 `wx_main`。仅读取这两个字段；不读取 user.bin、连接日志或浏览器存储。
- 加载器和已验证版本 DLL 的 Authenticode 均为 Valid，签发主体 Unity Technologies SF。
- DLL SHA256：`dbd59739cfb84a239860a30480b91281f0ebd316dfb5bf58bd4539e82c92c425`。
- DLL 导入 USER32、GDI32、D3D11、D3D12 等原生接口。PE 资源只有图标、版本和 manifest；没有独立语言字符串表。英文 UI 标签嵌入已签名 DLL。此结论仅限检查的版本。
- 安装目录未发现 `.asar`、可扩展语言包或独立 UI 翻译 JSON。
- 真实窗口 UI Automation 文档地址为 `https://builds.parsec.app/webview/release-ui/index.html`。主机设置存在标题、表格行、开关、组合框等可访问元素。本机使用 WebView2 新界面，不是 Electron。
- 实测 UI 标签包括 Hosting Enabled、Host Name、Bandwidth Limit、Virtual Displays (Beta)、Quality 等；界面页脚显示 libmatoya。
- UIA 的 Value/Toggle/Invoke 是值修改或动作接口，不是修改按钮标题的翻译 API。不能把更改控件值当成更改界面语言。

## 官方及平台资料

- [Windows 客户端](https://support.parsec.app/hc/en-us/articles/32381199341716-Parsec-App-for-Windows)：确认原生应用、便携版及配置位置。字典的补充标签来源之一。
- [macOS 客户端](https://support.parsec.app/hc/en-us/articles/32381394408596-Parsec-App-for-macOS)：确认平台客户端及设置分类。本环境无 macOS，未检查其应用包、签名、AX 树或运行行为。
- [高级配置](https://support.parsec.app/hc/en-us/articles/32381443626516-All-Advanced-Configuration-Options)：列出 `client_web_ui` 新界面开关；未找到受支持的 zh-CN/zh-TW 语言配置。未文档化功能不能视为存在。
- [Microsoft UI Automation patterns](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-control-patterns-overview)：说明读取属性与调用模式的能力边界。
- [Parsec 的 libmatoya 项目](https://github.com/parsec-cloud/libmatoya)：提供原生跨平台窗口和渲染库；结合本机证据推断旧界面使用自绘技术。未获得 Parsec 闭源 UI 的完整源代码。

## 技术路线决定

| 路线 | 结果 | 理由 |
| --- | --- | --- |
| A 语言资源替换 | 禁用 | 未发现受支持的语言扩展。补丁签名 DLL 会破坏签名；修改 WebView 缓存不可靠且会被更新覆盖。 |
| B 原窗口无侵入替换文字 | 禁用 | UIA 可读取新 UI，但没有设置静态文字的标准接口。旧 UI 和 macOS AX 未验证。 |
| C 独立中文辅助界面 | 实现目标 | 在自己的窗口中翻译公开 UI 标签，按需读取当前设置行；通过明确导航动作定位官方页。官方窗口仍保持英文。 |

不会使用截图 OCR、覆盖字幕、DLL 注入、签名重写、调试端口或流协议修改。不会改写 Parsec 配置、账户文件、安装资源，也不会自动重启 Parsec。

真实 GUI 验证中发现 UIA Invoke 调用可能在导航后不返回。因此读取／导航放在按需启动的本工具隔离进程中，18 秒超时后只终止该辅助进程，绝不终止 Parsec。超时提示导航结果未确认，必须重新读取；不记录成功。没有常驻监控或后台服务。

## 实际覆盖与版本门槛

**原生界面文字替换覆盖率为 0%。本项目不能声称完整汉化。** 辅助界面包含双语术语与在经过兼容性验证的 Windows WebView2 上按需读取的已知设置标题/值。只匹配字典标签，不收集账号、主机名、分享链接、密码或未知动态文本。

首次支持的读取适配器严格限制为 `150-105c`，UI 页面结构也必须通过验证。更新后重新检测并拒绝未知版本的实时读取与导航。离线术语查询仍可使用。字典条目数不是原生 UI 的覆盖率；实时面板另外报告当前页面的已翻译设置标题数/已观察标题数。

Windows 安装器和 macOS 包使用本项目自己的代码；不包含 Parsec 专有文件。macOS 首版只提供安装检测、术语、工具语言切换和打开官方客户端；实时 AX 适配器禁用，原因在界面展示。打包成功不等于已验证 Parsec 集成、串流性能或 macOS 实机使用。

## 验证边界

需要分别记录单元测试、真实 UI 读取、GUI、安装/卸载、构建和 CI 结果。不能把合成数据或辅助窗口的语言变化作为 Parsec 原生界面汉化前后对比。公开截图只拍本项目窗口；不发布含用户标识的 Parsec 截图。

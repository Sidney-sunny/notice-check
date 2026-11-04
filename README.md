# 报名通知不漏项

`notice-check` 是用于竞赛报名通知提取与复核的结构化Skill，适用于支持本地技能与相应读取工具的Codex环境。项目围绕阶段、范围、原文依据、变更和缺项组织信息；默认不代办报名或发送消息。

## 使用
读取 `notice-check/SKILL.md` 并提供通知正文、文件、截图或网址。项目安装可使用 `notice-check/scripts/install_skill.ps1`，安装目标为所选项目的 `.agents/skills/notice-check`；已有同名技能时安装器拒绝覆盖。安装后在相应项目调用 `$notice-check`。

## 文件
- `assets`：输出模板与历史模拟示例。
- `examples`：重点模拟案例。
- `references`：范围、字段和结果结构规则。
- `scripts`：可选检查与安装脚本，检查脚本使用Python标准库。
- `resources/tests`：8组基础测试，其中C01至C07为模拟或故障情境，C08为真实截图。
- `resources/real-tests`：3个真实材料验证情境，部分复用来源；不是独立人工评审。
- `resources/recording-inputs`：真实录屏输入，不是预设输出。

## 结果边界与AI披露
核心流程由宿主模型执行，读取能力依宿主环境。来源不可读时如实记录，不从摘要补全。结构检查不证明全部事实正确，不提供总体准确率或节时比例。Skill、脚本、测试整理及文字由团队在Codex辅助下完善。第三方通知的权利归原权利人，保留原始来源，不作为团队原创内容申报。

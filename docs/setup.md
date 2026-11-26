# 发布 Enterprise 共享 Codex Cloud Environment

目标是由维护者给工作区发布一套 `market-feedback-pilot` 环境。获准成员各自新建 Codex 任务，继承同一仓库和 v2 规则配置。当前仓库提供配置清单和可运行的验收脚本，实际 Enterprise 发布与双账号共享尚待目标工作区验证。

## 配置工作区权限

请管理员在 **Admin Console → Permissions & roles** 检查试点账号。

| 角色 | 权限与职责 |
| --- | --- |
| A · 维护者 | `Use Codex in the cloud` 和 `Manage workspace environments`。负责创建、发布、更新及回退环境。 |
| B · 普通市场成员 | `Use Codex in the cloud`，可以使用共享环境执行任务。由管理员核对 B 的环境管理权限，试点普通成员不授予该权限。 |

两人需进入同一个 Enterprise 工作区，并使用工作区允许的 GitHub 连接。对其他私有项目，仓库访问仍需各自授权。[OpenAI 权限说明](https://learn.chatgpt.com/docs/enterprise/roles-and-workspace-permissions#review-codex-cloud-access-and-environment-administration)

## 创建、准备和发布

A 在网页或桌面打开 **Settings → Codex Cloud → Environments → Create environment**。也可以在新任务中打开 **Work in → Cloud → Select environment → Create environment**。选择仓库后进入准备对话。

| 配置项 | 本项目填写 |
| --- | --- |
| 环境名称 | `market-feedback-pilot` |
| Repository | `peterljlj/market-feedback-cloud-demo`，演示分支 `main` |
| 运行依赖 | Python 3 标准库。项目根目录包含 `feedback_check.py`，无需启动其他服务。 |
| Environment variables → Manage | 在环境设置中保存 `FEEDBACK_RULES_FILE=rules/v2.json`，这是共同的分类规则路径。 |
| 网络 | 遵守工作区网络设置并允许使用 GitHub。本演示无需 VPN 或 HTTP secrets。 |
| Privacy → Who can use | 选择目标 Enterprise 工作区，并核对实际可用范围。 |
| 配置清单 | [market-feedback-pilot.json](../cloud/market-feedback-pilot.json) 用于审阅和仓库验收，发布操作通过 Codex 界面完成。 |

在准备阶段运行以下命令，检查原有单元测试及 v2 的样例结果。

```sh
python3 -m unittest -v
python3 scripts/check_team_cloud_environment.py --prepare
```

核对仓库、变量和共享范围后点击 **Publish**，确认已发布。已经发布的环境可以在编辑页更新共享范围。[OpenAI 创建和发布说明](https://learn.chatgpt.com/docs/environments/cloud-environments#create-and-publish-an-environment) · [共享范围说明](https://learn.chatgpt.com/docs/environments/cloud-environments#share-within-an-enterprise-workspace)

## 用两个账号验收已发布的环境

1. A 和 B 分别登录，切换到同一 Enterprise 工作区。在新任务里从 **Work in → Cloud** 选择同一个已发布环境。
2. 两人在仓库根目录直接运行下列命令，让验收读取新任务从发布配置继承的变量。

   ```sh
   python3 scripts/check_team_cloud_environment.py
   ```

3. 两份输出均应为 `check: PASS` 和 `scope: active task configuration`。确认实际 Git 提交相同，规则指纹为 `0728e7536859`，三地合计 45 条。兼容性应为英国 2 条、新加坡 2 条、澳大利亚 5 条。
4. 每人记录实际工作区、环境名称、发布版本或时间和输出。A 验证维护权限，B 验证可启动任务。两人的结果相符后，才算完成共享环境验收。[验收记录表](validation.md#enterprise-共享验收)

市场负责人在支持项目 Skill 的客户端选中 `check-market-feedback`，例如说「检查 `samples/uk.csv`、`samples/sg.csv`、`samples/au.csv` 的现有标签，按市场列出需要复核的 ID 和匹配词」。v2 下预期英国、新加坡各 2 条，澳洲 5 条 `LABEL_MISMATCH`。改查同一批的 `*-revised.csv`，应无剩余兼容性提示。A、B 分别记录 Skill 是否可见、实际运行命令和结果。可选 Agent 角色的发现与调用另行记录。

## 更新、回退和扩员

- **发布新规则。** 澳洲市场负责人提案，区域负责人审批业务口径，维护者提交 GitHub 并记录提交。在 **Settings → Codex Cloud → Environments → Edit** 更新并 **Republish**，从新任务验收。已有任务保留自己的工作状态。
- **回退演练。** 将同一个环境的变量改为 `rules/v1.json`，重新发布后从新任务直接运行 `python3 verify_environment.py --expect v1`。预期环境检查通过，三地修订表的 9 条新标签被拦截。用旧标注表运行 `feedback_review.py` 可复现这 9 条类别缺口。演练完恢复 v2。
- **环境在选择器里不可见。** 检查登录的工作区、共享范围、发布状态及成员的 Cloud 使用权限。能看到环境但打不开项目时，再检查 GitHub 连接和仓库访问。
- **验收退出 2。** 检查发布配置中的 v2 变量是否正确、任务是否来自正确的环境。修正后重新发布，再开新任务验收。
- **先五人，再扩员。** 双账号入口验收后，按五人分工完成一次交接。扩大到 30–50 人前，测实际同时启动的任务数、成功率、排队、配额和首次交付用时。[业务流程](../README.md#enterprise-如何用同一个环境和-skill)

使用当前账号录制时，A 和 B 各自配置同一 GitHub 仓库。A 以维护者身份切到 v2 并发出通知。B 在自己的环境启用 v2，用同一条命令重新筛查新加坡原始 CSV，展示标签不匹配。[两个账号的录制顺序](../README.md#用两个账号录制一次规则更新接力)

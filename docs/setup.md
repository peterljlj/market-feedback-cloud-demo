# Codex Cloud 试点配置和验收

本仓库的代码和 9 条样例供 Plus、Business 和 Enterprise 共用。Cloud 访问取决于账号资格、产品开放和工作区设置。[套餐说明](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)

## 通用配置

| 项目 | 填写内容 |
| --- | --- |
| 环境名称 | `market-feedback-pilot` |
| 仓库与引用 | `peterljlj/market-feedback-cloud-demo` 的 `main`，两人实际验收时核对同一 Git 提交 |
| 运行依赖 | Python 3 标准库，无额外依赖或启动服务 |
| Environment variables | `FEEDBACK_RULES_FILE=rules/v2.json`，在环境配置自身的变量中保存 |
| 网络 | 使用工作区允许的 GitHub 连接。本演示不需要 VPN 或 HTTP secrets。接入内网库存系统时另行确认网络和数据权限。 |
| 配置文件 | [market-feedback-pilot.json](../cloud/market-feedback-pilot.json)，供审核与仓库脚本读取。发布和共享范围在 Codex 界面设置。 |

## 现在就能做的 Plus / Business 路径

1. 在有 Codex Cloud 的账号里新开任务，使用 **Work in → Cloud**，选择公开演示仓库。进入项目根目录运行下列命令。Plus 或 Business 都能用同一份代码执行。

   ```sh
   python3 -m unittest -v
   python3 scripts/check_team_cloud_environment.py --prepare
   ```

2. 如果要演示个人环境复用，从 **Settings → Codex Cloud → Environments → Create environment** 创建环境，按上表填好仓库和变量，保留个人范围 **Only me**，点 **Publish**。另开一个新聊天并选中这个环境，直接运行末尾的验收命令。
3. Business 中由同事用自己的账号启动另一个任务，并检出相同提交。各自运行准备检查，比较提交、规则指纹、输入指纹和输出。要演示个人环境，两人可分别按第 2 步配置。
4. 业务交接可由 A 充当区域负责人，B 检查澳洲样例并交付 v2 结果、两条待复核记录和跟进角色，A 合并三地批次并检查重复记录。用于实际工作时，共享结果可放在团队批准的位置，虚构展示样例可以放在 GitHub。

## Enterprise 工作区共享路径

1. 管理员在 **Permissions & roles** 给维护者和普通成员开通 `Use Codex in the cloud`，给维护者开通 `Manage workspace environments`。管理员同时核对工作区网络策略与成员可用范围。
2. 维护者用同一份仓库、规则和变量创建环境。在 **Privacy → Who can use** 选择目标 Enterprise 工作区并 **Publish**。配置中的访问范围、管理权限及可用网络策略取决于目标工作区。
3. 两人用各自账号进入同一工作区。分别在环境选择器选择同一已发布环境，各自启动新任务并运行验收命令。由操作者记录实际发布版本、环境名和 Git 提交，核对规则指纹及结果。
4. 维护者更新规则或配置后重新发布，成员从新任务取得更新。回退演练可将变量设为 `rules/v1.json` 后重新发布，从新任务直接运行 `python3 verify_environment.py --expect v1`。预期环境检查 `PASS`，两条新标签被拦截。演练后恢复 v2。
5. 先以两位成员验证共享入口，再由维护者、三地负责人和区域负责人完成五人演练。要扩到 30–50 人，再测同时间窗口实际任务数、完成率、排队、配额和上手耗时。[OpenAI 共享环境及角色说明](https://learn.chatgpt.com/docs/environments/cloud-environments#share-within-an-enterprise-workspace)

## 发布后的验收命令

在选中的新任务直接运行，配置从已发布环境继承。

```sh
python3 scripts/check_team_cloud_environment.py
```

通过时输出 `check: PASS`、`scope: active task configuration`、Git 提交及三地结果。预期规则指纹 `0728e7536859`、澳洲输入指纹 `3fc638ba555e`，9 条记录进入复核，其中两条为澳洲补充装兼容性。若变量缺少或仍指向 v1，检查会退出 2。平台是否共享成功还要由两个账号从环境选择器核对同一发布版本。

| 权限或步骤 | 遇到问题时先检查 |
| --- | --- |
| 同事看不到共享环境 | Enterprise 工作区、环境发布状态与共享范围；成员是否获准使用 Codex Cloud |
| 仓库不可选 | GitHub 连接与工作区仓库策略。对于后续私有项目，再检查成员自己的仓库权限。 |
| 找不到 Skill / Agent | 在目标客户端实测发现和调用。仓库包含 `check-market-feedback` Skill 文件与两份可选 Agent 配置。 |

文件结构保留 [环境配置](../cloud/market-feedback-pilot.json)、[执行和验收脚本](../scripts/)、[自动测试](../tests/) 与 [实跑证据](evidence/demo-run.json)。需要验证 v1 和 v2 对同一输入的行为时，可执行 `python3 scripts/run_business_acceptance.py --account A`。账号标签由操作者填写。

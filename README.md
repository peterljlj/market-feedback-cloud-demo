# Codex Cloud 团队协作试点

英国、新加坡和澳洲分别整理市场反馈。团队要统一分类后交一份区域简报。这个演示用 9 条虚构反馈，检验三地使用同一规则时能否得到可核对的结果，以及规则升级后如何让同事拿到新版本。

[下载 Word 展示说明](https://raw.githubusercontent.com/peterljlj/market-feedback-cloud-demo/main/docs/cloud-collaboration.docx) · [配置和操作](docs/setup.md) · [实跑输出](docs/evidence/demo-run.json)

## 按账号选择演示路径

| 账号 | 现在能做什么 | 如何演示 |
| --- | --- | --- |
| Plus 个人账号 | 有资格并已开放 Codex Cloud 时，可以运行仓库中的样例并发布个人环境供自己复用。 | 从自己的 Cloud 任务运行准备检查，再从个人命名环境开一个新任务验证 v2 配置。 |
| Business 工作区 | 同事共享 GitHub 中的代码、文档、规则和 Skill，各自运行 Cloud 任务。个人命名环境可由各账号分别配置。 | 两位同事用自己的账号选同一 Git 提交复跑，比较规则指纹、输入指纹和结果，完成一次交接。 |
| Enterprise 工作区 | 授权维护者可向工作区发布同一环境，授权成员从统一入口各自启动任务。管理员可按角色管理使用和维护权限，并配置网络等组织策略。 | A 发布一次 v2。A、B 分别从同一发布版本开新任务，直接验收生效的设置并记录结果。 |

| 所有路径共用 | 发布时按账号设置 |
| --- | --- |
| 同一仓库、Python、CSV、规则及校验脚本。环境变量都用 `FEEDBACK_RULES_FILE=rules/v2.json`。 | Plus / Business 选择个人范围 `Only me`。Enterprise 可以选择目标工作区，并由管理员分别授权使用和管理。GitHub 公开范围和 Codex 环境使用范围分别设置。 |

分享环境让成员获得准备好的配置。每个任务仍有自己的工作目录和聊天，成果通过 GitHub 或团队记录交接。[OpenAI 套餐说明](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan) · [Cloud 环境共享说明](https://learn.chatgpt.com/docs/environments/cloud-environments#share-within-an-enterprise-workspace)

## 一次协作会产出什么

| 人员 | 操作与交接 |
| --- | --- |
| 规则维护者 | 审核新标签，发布规则和 Git 版本；Enterprise 下同时发布共享环境配置。 |
| 英国、新加坡、澳洲各一位市场负责人 | 在自己的任务检查本地 CSV，提交规则和输入指纹、状态、需要跟进的问题。 |
| 区域负责人 | 用同一版本复核三份输出并检查跨批次重复 ID。提交简报并分派后续核实。 |

澳洲有两条反馈分别涉及补充装装不上和密封失败。v1 会拦下修订样例中的两条新标签，v2 允许两条记录进入人工复核。英国的门店可得性与新加坡的售罄线索交当地核实。样例只有反馈文字，实际库存仍需从库存系统确认。

| v2 市场汇总 | 一般包装 | 香味 | 购买可得性 | 补充装兼容性 | 合计 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 英国 | 1 | 1 | 1 | 0 | 3 |
| 新加坡 | 1 | 1 | 1 | 0 | 3 |
| 澳洲 | 0 | 1 | 0 | 2 | 3 |
| **合计** | **2** | **3** | **2** | **2** | **9** |

## 快速复跑

在有 Python 3 的 Cloud 任务或本地终端进入仓库根目录。

```sh
python3 scripts/check_team_cloud_environment.py --prepare
```

准备检查使用仓库中配置的 v2，预期为 `PASS` 和 9 条 `READY_FOR_REVIEW`。若已发布个人或共享环境，在新任务去掉 `--prepare` 直接运行，验证任务从环境设置继承的规则值。准备检查的通过只证明仓库代码和规则可运行。

当前已有一次 Cloud 任务的命令实跑和 5 项单元测试。Plus 个人环境、Business 第二账号、Enterprise 共享发布与多人并发需分别实测。建议先做两账号验收，再跑完整的五人交接。30–50 人属于后续扩容目标。[分阶段验收](docs/setup.md)

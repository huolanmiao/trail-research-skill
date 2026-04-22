# Contributing to trail-research-skill

感谢你对本项目感兴趣。下面是贡献流程和几条硬性要求。

## 前提：阅读并接受项目条款

在提交任何贡献前，请确认你已经完整阅读并接受：

- [LICENSE](LICENSE)（Apache-2.0，代码）
- [LICENSE-docs](LICENSE-docs)（CC BY-NC-SA 4.0，文档和资源）
- [DISCLAIMER.md](DISCLAIMER.md)（户外活动免责声明）
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)（Contributor Covenant）

## 贡献方式

### Issue（问题反馈 / 功能建议）

在提 Issue 前请先搜索已有 Issue 避免重复。推荐使用模板：

- **Bug report**：复现步骤、期望行为、实际行为、环境（OS / Node / Python / Agent 名称及版本）
- **Feature request**：使用场景、动机、是否愿意自己实现

### Pull Request

1. **Fork** 本仓库并基于 `master` 创建 feature 分支：`git checkout -b feat/your-feature`
2. **写代码并自测**：`scripts/` 下 Python 改动需本地跑通至少一次完整流程
3. **提交（签名）**：见下面 DCO 部分
4. **开 PR**：说明改动动机、影响范围、测试过的场景

### DCO（Developer Certificate of Origin）

本项目采用 [Developer Certificate of Origin 1.1](https://developercertificate.org/)
管理贡献版权。**每一个 commit 必须 `--signoff`**，表示你确认自己有权贡献这段代码：

```bash
git commit --signoff -m "feat: 你的改动"
```

这会在 commit message 末尾追加：

```
Signed-off-by: Your Name <your-real-email@example.com>
```

没有 `Signed-off-by` 的 PR 会被请求补 signoff 后再合并。

你签名即表示你**同意**：

> 1. The contribution was created in whole or in part by me and I have
>    the right to submit it under the open source license indicated in
>    the file; or
>
> 2. The contribution is based upon previous work that, to the best of
>    my knowledge, is covered under an appropriate open source license
>    and I have the right under that license to submit that work with
>    modifications; or
>
> 3. The contribution was provided directly to me by some other person
>    who certified (1), (2) or (3) and I have not modified it.
>
> 4. I understand and agree that this project and the contribution are
>    public and that a record of the contribution (including all
>    personal information I submit with it) is maintained indefinitely
>    and may be redistributed consistent with this project.

## 不接受的贡献

以下类型的 PR 会被直接拒绝：

- 含有商业推广链接或二维码
- 含有他人未授权的个人信息（姓名、手机、微信、邮箱）
- 对 `SKILL.md` 或 `scripts/` 中安全相关逻辑的修改未附带测试和 rationale
- 引入 GPL 族许可证的依赖（与 Apache-2.0 不兼容）
- 将协会 / 机构内部文档作为示例直接纳入仓库

## 协会相关内容贡献

如果你是北京大学学生徒步越野协会的现任或往届成员，想补充/修订协会相关内容
（`references/handbook.md`、`references/leader-handbook-full.md`、`assets/`），请额外在 PR 中：

1. 说明你的协会身份和任职时间
2. 声明你所提交内容的版权归属与授权范围
3. 若涉及敏感内部信息（内部共享链接、领队联系方式、未公开活动流程等），请先联系维护者商议是否适合开源

## 代码风格

- Python：遵循 PEP 8，4 空格缩进，必要时用 `ruff` / `black` 格式化
- Markdown：一级标题用 `#`，列表用 `-`，代码块指定语言
- 文件编码：UTF-8（不带 BOM），行尾 LF

## 发布与版本

- 使用 [Semantic Versioning](https://semver.org/)：`MAJOR.MINOR.PATCH`
- 重要改动需在 `CHANGELOG.md`（如有）中记录

## 联系方式

- Bug / Feature：开 Issue
- 安全问题：见 [SECURITY.md](SECURITY.md)
- 协会相关事务：维护者会在 Issue 中协助转达

---

感谢你的贡献 🏔️

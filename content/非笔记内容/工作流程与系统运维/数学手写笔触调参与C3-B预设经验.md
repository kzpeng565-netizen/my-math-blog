---
title: MathInk Forge 数学手写笔触调参与 C3-B 预设经验
date: 2026-08-25
tags:
  - MathInk-Forge
  - 手写笔
  - 压感调参
  - 工作流
---

# MathInk Forge 数学手写笔触调参与 C3-B 预设经验

## 结果摘要

在 Huawei MatePad BAH3-W09、第一代 M-Pencil、HarmonyOS 3 与 Huawei WebView 114 上，经过两轮真实数学笔记采样、离线同轨迹对照和多轮真机试写，最终选择 **C3-B** 作为黑、蓝、红三支正式笔的共同模板。

最终模板兼顾三件事：轻笔能画出约 1 px 的图形细线；上下标和小尺度转折能跟随笔尖；中压到重压不会突然膨胀。已有笔迹使用各自保存时的样式快照，不会被新预设追溯改写。

## 最终 C3-B 参数

| 参数 | 数值 |
| --- | ---: |
| Size | 2.6 |
| Pressure enabled | true |
| Input minimum / maximum | 0.07 / 0.95 |
| Output minimum / maximum | 0.03 / 0.89 |
| Curve | Soft |
| Gamma | 2.35 |
| Fallback pressure | 0.50 |
| Thinning | 0.75 |
| Smoothing | 0.38 |
| Streamline | 0.14 |
| Start / End taper | 0 / 0 |

三支正式笔只改变颜色：

- Black formula：`#1a1a1a`
- Blue text：`#1971c2`
- Red annotation：`#e03131`

## 真实输入数据给出的边界

参考抄写轮收到 482 次 `pointerdown`、482 次 `pointerup`、0 次 cancel，6058 个正压力样本；压力 P05/P50/P95 为 0.226/0.650/0.913。数据说明设备压力范围是连续且可用的，问题不在“没有压感”，而在压力映射、轨迹保留与笔形参数。

M-Pencil 的 `pointerup` 会报告压力 0。若把这个 0 直接映射为 fallback 0.5，笔画末端会突然变粗变圆。正确做法是：零压力抬笔坐标仍然保留，但端点压力沿用最后一次正接触压力。这样能产生自然笔锋，又不会用固定长 taper 吞掉数学点、短横和短撇。

## 两个最重要的根因

### 1. 最细线宽由 Output minimum 与 Thinning 共同决定

旧版 size 2.8、output minimum 0.30、thinning 0.35 的理论最细直径仍约 2.4 px。即使用户尽量轻压，也不可能得到真正的细线。调轻笔时不能只减小 size；需要同时降低 output minimum，并提高 thinning，让轻压和正常压力之间形成足够动态范围。

最终 C3 系列使用 size 2.6、output minimum 0.03、thinning 0.75。轻笔可落到约 0.8–1.0 px，正常书写仍保持约 3 px，重压仍有清晰加粗。

### 2. 小字细节不能靠降低 Smoothing 单独解决

生产路径曾保留 1.4 屏幕 px 以上的点，而诊断重放和性能门槛已经使用 0.35 px。这会直接丢掉上标、下标、小圆和短钩中小于 1.4 px 的方向变化。生产门限统一为 0.35 屏幕 px 后，小尺度轨迹才真正进入笔形引擎。

保留更多 coalesced 样本并不等于每个样本都重建昂贵轮廓。湿墨仍限制为每个动画帧最多重建一次，因此 5000 点长笔画的确定性向量工作量仍下降 96.31%。

## 为什么最终从 Candidate 3 调到 C3-B

Candidate 3 已经解决轻笔和轨迹细节，但用户认为中压到重压仍略微增长过快。目标是只减缓压力曲线上半段，尽量不改变已经满意的轻压到中压。

原 Candidate 3 使用 Medium、gamma 1.10、output maximum 0.92。C3-B 改为 Soft、gamma 2.35、output maximum 0.89，其余参数完全不变。两者的映射对比如下：

| Raw pressure | Candidate 3 | C3-B |
| ---: | ---: | ---: |
| 0.226（P05） | 0.088 | 0.090 |
| 0.400 | 0.281 | 0.299 |
| 0.650（P50） | 0.660 | 0.673 |
| 0.800 | 0.845 | 0.832 |
| 0.913（P95） | 0.915 | 0.886 |

可以看到，轻压与中压几乎不变；从 0.8 开始增长变缓，P95 输出下降约 0.029。这个变化量足以改善重压突增，又不会把整支笔重新调一遍。

## 推荐的调参顺序

1. **先确认输入完整性**：比较实际落笔、pointerdown、created stroke 和 saved stroke；丢事件时调笔形无效。
2. **再确认轨迹门限**：小字动作已进入 raw/coalesced，但成品缺转折时，检查采样距离和 streamline。
3. **先定正常线宽**：用 size 决定中压正文的总体粗细。
4. **再定轻笔下限**：联合调整 output minimum 与 thinning；不要只减 size。
5. **最后调压力形状**：轻到中满意、只有中到重过快时，用曲线、gamma 和 output maximum 微调上半段。
6. **一次只动一个目标层级**：轨迹、线宽、压力曲线和端点不要同时大改，否则无法判断主观变化来自哪里。

## 后续微调规则

- 轻笔偶尔看不见：先把 output minimum 从 0.03 增至 0.04，每次只加 0.01。
- 正文整体偏粗或偏细：先调整 size，每次 0.05–0.10；不要先改变整条压力曲线。
- 中重压仍增长过快：优先把 output maximum 从 0.89 降至 0.88，或把 gamma 从 2.35 增至 2.40；一次只改一项。
- 中重压反应太迟：反向做小步调整，不要直接回到 Medium 曲线。
- 小字轮廓太毛：先把 smoothing 从 0.38 增至 0.40；若笔尖动作被拉圆，再退回。
- 上下标轨迹仍被整理：小步降低 streamline，但不建议低于 0.10，以免放大设备抖动。
- 不把固定长 taper 设为默认：5–20 px 短笔很多，taper 容易让点和短标注发虚。

## 预设编辑与恢复

Pen Box 的快速浮层适合改颜色和 size；画笔管理器可以编辑完整参数：压力开关、Input/Output、Curve、Gamma、Thinning、Smoothing、Streamline、Start taper 和 End taper。每支笔保存完整样式快照，因此黑、蓝、红可以从同一模板出发后独立微调。

历次 14 支测试笔已经整理成不含 API key 或其他插件设置的可导入 JSON：

`D:\MathInk-Forge-Project\artifacts\backups\tested-pen-archive-20260825\tested-pen-presets.json`

最终部署前的完整插件三件套和 `data.json` 位于：

`D:\MathInk-Forge-Project\artifacts\backups\tablet-pre-final-c3b-20260825-1315\`

最终已部署三件套快照位于：

`D:\MathInk-Forge-Project\artifacts\deployed-c3b-final-20260825-1322\`

## 验证记录

- 40 个测试文件、305 项测试全部通过。
- TypeScript typecheck、ESLint、生产构建通过。
- 快速输入门槛通过：正常 60/60，过载哨兵 27/60，0.5×/1×/2×/4× 采样门限均为 0.350 屏幕 px。
- 平板 `main.js` SHA-256：`58CEA7740AAEFF34D9A178CFD477962979CA338048125DF33D32C9F4F6BFE0BF`。
- 正式预设写入前后，`Handwriting note 2.ink.md` SHA-256 均为 `3387EFF8130D74AF5617FF3BC0A20A5AE2F5B1D002F9AFF90A8CF3110C157C5A`。

本文只记录参数、统计和方法，不包含用户手写笔记正文或截图。

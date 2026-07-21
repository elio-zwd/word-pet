# Pink Star — Codex Pet 动作包

这是 `word-pet` 仓库中的独立 Codex 宠物资源包，由用户提供的参考图制作。

## 目录内容

- `pet.json`：Codex v2 宠物清单
- `spritesheet.webp`：Codex v2 动作图集，1536×2288，8×11
- `spritesheet-v1.png`：兼容 8×9 上传格式，1536×1872
- `actions/*.gif`：各状态动作预览
- `source/character-cutout.png`：透明背景角色素材

## 动作映射

| 行 | 状态 | 使用帧数 |
|---:|---|---:|
| 0 | idle 待机 | 6 + 1 个 v2 中性帧 |
| 1 | running-right 向右移动 | 8 |
| 2 | running-left 向左移动 | 8 |
| 3 | waving 挥手 | 4 |
| 4 | jumping 跳跃 | 5 |
| 5 | failed / blocked 失败或阻塞 | 8 |
| 6 | waiting / needs-input 等待输入 | 6 |
| 7 | working 工作中 | 6 |
| 8 | review / ready 检查完成 | 6 |
| 9–10 | 16 个注视方向 | 16 |

## 使用

Codex v2 使用本目录下的 `pet.json` 与 `spritesheet.webp`。需要 8×9 格式时使用 `spritesheet-v1.png`。

主分支合并后的图集地址：

```text
https://raw.githubusercontent.com/elio-zwd/word-pet/main/codex-pets/pink-star/spritesheet.webp
```

## 制作说明

动作由单张参考图通过位移、旋转、缩放、翻转和状态提示合成，并非逐帧手绘。

参考图可能涉及第三方角色形象，仅建议个人使用；公开分发或商业使用前请确认相应权利。

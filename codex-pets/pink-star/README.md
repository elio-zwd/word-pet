# Pink Star — Codex Pet 动作包

这是 `word-pet` 仓库中的独立 Codex 宠物资源包，形象与配色参考用户提供的粉色圆形角色图片，并使用 Pillow 矢量绘制生成完整动作图集。

## 目录内容

- `pet.json`：Codex v2 宠物清单
- `spritesheet.png`：Codex v2 动作图集，1536×2288，8×11
- `spritesheet-v1.png`：兼容 8×9 上传格式，1536×1872
- `actions/*.gif`：10 组动作预览
- `build_pet.py`：可复现的动作包生成脚本
- `validation.json`：尺寸、网格与动作校验信息

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

Codex v2 使用本目录下的 `pet.json` 与 `spritesheet.png`。需要 8×9 格式时使用 `spritesheet-v1.png`。

主分支合并后的图集地址：

```text
https://raw.githubusercontent.com/elio-zwd/word-pet/main/codex-pets/pink-star/spritesheet.png
```

安装深链模板：

```text
codex://pets/install?name=Pink%20Star&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Felio-zwd%2Fword-pet%2Fmain%2Fcodex-pets%2Fpink-star%2Fspritesheet.png&description=Pink%20Star%20animated%20pet&spriteVersionNumber=2
```

## 重新生成

```bash
python -m pip install pillow
python codex-pets/pink-star/build_pet.py
```

GitHub Actions 会重新生成图集、GIF 预览并校验尺寸和透明背景。

## 说明

当前仓库版采用简化矢量风格，动作由位移、旋转、压缩、拉伸、朝向变化与状态提示组合生成。

参考图可能涉及第三方角色形象，仅建议个人使用；公开分发或商业使用前请确认相应权利。

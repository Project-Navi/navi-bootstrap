---
name: dev-nboot
description: Render a pack to a scratch directory and show the diff. Use when iterating on pack or engine changes to verify output before committing.
disable-model-invocation: true
---

# dev-nboot

Fast inner loop for pack or engine changes. Renders to a scratch directory under `/tmp/nboot-scratch-*` and shows the diff.

## Steps

1. Ask the user which pack to exercise (or use `base` as default).
2. Run the cycle:

   ```bash
   scratch=/tmp/nboot-scratch-$(date +%s)
   uv run nboot new "$scratch"
   uv run nboot apply --spec nboot-spec.json --pack "$PACK" --target "$scratch"
   uv run nboot diff  --spec nboot-spec.json --pack "$PACK" --target "$scratch"
   ```

3. Summarise the diff output. Flag any unexpected file additions, removals, or empty renders.

## When this skill helps

- After editing any `packs/<pack-name>/**` file
- After changing `engine.py`, `manifest.py`, `spec.py`, `resolve.py`, `validate.py`, or `hooks.py`
- Before opening a PR that touches templates or the engine

## Cleanup

Scratch directories are safe to delete:

```bash
rm -rf /tmp/nboot-scratch-*
```

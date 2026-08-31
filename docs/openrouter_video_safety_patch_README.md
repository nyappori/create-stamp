# OpenRouter Video Safety Patch

Unexpected billing was observed while `OPENROUTER_MODEL=bytedance/seedance-2.0:free` was configured.

OpenRouter's public model page says the `:free` variant costs $0, but the dedicated video model endpoint currently exposes canonical model slugs such as `bytedance/seedance-2.0` rather than the `:free` slug. This patch therefore uses a conservative fail-closed policy.

## Use

Copy `scripts/openrouter_seedance_batch_safe.py` into the existing project.

Then run a preflight / batch command normally:

```bat
py scripts/openrouter_seedance_batch_safe.py --only-ids 01 --out-dir ./out_safe_test
```

With the current API behavior, if `bytedance/seedance-2.0:free` is not present EXACTLY in `/api/v1/videos/models`, it stops before submitting anything.

Do NOT use `--allow-paid` unless paid generation is intentional.

## Why

The video status API exposes `usage.cost` after completion. The safe script logs that value and immediately stops the batch if it is non-zero.

## What to inspect in OpenRouter

Go to Logs or Activity and inspect one of the already generated videos. Check:
- actual model slug shown
- cost
- generation ID

If the requested slug was `bytedance/seedance-2.0:free` but the charged generation shows the canonical paid model, report it to OpenRouter as a billing/routing issue.

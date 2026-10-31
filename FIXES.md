# Bug fixes: training, environment, evaluation (2026-10-31)

Every change in the code is tagged with a `# FIX:` comment. To see them all, run this from the repo folder (works in PowerShell, cmd and bash):

```bash
git grep -n "# FIX:"
```

Paths below are relative to `Development/TrainingCode/`.

## Why FNR/FPR stayed high

1. **No model ever trained** (most important). Every agent's `trainingSingleEpisodes()` (the method `driver_v2.py` calls) ended with `if terminalState: break` / `if not terminalState: continue`. Both left the loop before the replay-buffer append and `trainNetwork()`, so all saved checkpoints were untrained networks.
2. **FNR/FPR had no effect on what the agent saw.** The env returned the true state as the observation, and the IDS alert state was never reset.
3. **Honeypot and critical-node checks were off by one**, and the critical node was hardcoded in `reset()`.
4. **Evaluation measured something else.** It used the randomized adaptive env, fixed FNR/FPR/attack rate, ran the episodes twice, and averaged a running counter. That's how DSP could reach 1.01.

## Fixes by file

### Environment: `NetworkHoneypotEnv_base_v4.py` (and the same fixes in `A2C_Subnet/NetworkHoneypotEnv_AdaptiveTraining_AC.py`)
| What | Before | After |
|---|---|---|
| Observation | true `_state` | `_alerted_state` (IDS view with FNR/FPR noise); true state stays hidden |
| Alert state on reset | never cleared | cleared in `_reset()` |
| Initial foothold | not marked | marked in true state; alerted with probability `1 - FNR` |
| Critical node | `reset()` forced `[5]`; checked `_state[5]` (0-based) | constructor value is kept; default `DEFAULT_NICR_NODES = [6]` (1-based ID, the same node as the old `_state[5]`) |
| Node numbering | actions 1-based, `_state[i]` checks 0-based, node K never checked | everything uses 1-based node IDs (`list(ntpg.keys())[id-1]`), matching the logging/visualizer code |
| Step order | checked for a catch **before** applying the new action and moving the attacker, so the reward arrived one step late | deploy honeypots → attacker moves → check → reward |
| What counts as a catch | any honeypot node already marked compromised | only the node the attacker **just entered** |
| `is_honeypot()` | compared IP keys with node IDs, so it was always False and the 0.5 weight never applied | compares node IDs, so the 0.5 weight now applies |
| All-zero route weights | `random.choices` would crash | falls back to a uniform choice |

Adaptive env only:
- Action space was subnet IDs 1–4 (marked "MUST CHANGE"), but the IDs were checked as node IDs. It now picks nodes, which is what `inference_v6_adaptive.py` expects (it maps nodes to subnets itself) and matches the actor's output size.
- `generate_random_ntpg()` overwrote the random start node with `keys[2]`. The new NTPG is now generated first, then the attacker is placed on it.

### DDQN agents: `ddqn_agent_headless_v2.py`, `MatrixTest3/ddqn_agent_3x_simple_state_fnrfpr.py`, `..._fnrfpr_v2.py`, `..._fnrfpr_v3.py`, `MatrixTest3/ddqn_agent_3x_multi_input_fnrfpr.py`
- `trainingSingleEpisodes()`: store every transition, train, and advance `currentState`; then check the checkpoint step and the terminal state. The 3-input agents store `(obs, epss, ntpg, action, reward, next_obs, done)`, the format their `trainNetwork()` reads.
- `trainNetwork()`: Q-targets were written at `outputNetwork[index, action]`, where `action` is a tuple of node IDs, so the wrong Q-values were updated. Added `action_to_index()` and use it there.
- 3-input agents: no bootstrapping past a terminal state (`y = reward if terminated`).
- `fit(..., epochs=200)` → `epochs=1` per step. 200 epochs on every minibatch overfits it and is very slow.
- `ddqn_agent_headless_v2.py`: removed the `if action[0] >= totalpermutation: continue` check, which compared a node ID against the action count.

### A2C agents: `PPO/a2c.py`, `PPO/a2c_3input.py`, `A2C_Subnet/a2c_adaptive.py`
- Same loop fix as the DDQN agents.
- `trainNetwork()` rewritten as a one-step advantage actor-critic update (GradientTape) on the transition just taken. The old version:
  - fitted the actor to its own previous probabilities and the critic to the raw reward
  - passed the EPSS/NTPG inputs as `predict()`'s `batch_size` argument (it only "worked" because it never ran)
- `actionDimension` is now `len(env.action_space())`. It was a float from `/`.
- `a2c_adaptive.py`:
  - `selectAction` / `selectActionEval` / `selectActionInference` now build the input from the current observation. They used an input frozen at `__init__`, so the policy ignored the state.
  - EPSS/NTPG planes are rebuilt after every reset, because the env draws a new NTPG each episode.

### SARSA: `sarsa/sarsa_agent.py`, `sarsa/sarsa_agent_3input.py`
- Removed `reward += 1`. It turned a win (1) into 2, so `reward == 1` never counted wins.

### Evaluation: `evaluation_headless_v2.py`
- Evaluates with the **same env class** as the agent's training env. It used to import the A2C_Subnet adaptive env, so DDQN/SARSA/A2C were all scored on a new random graph every episode.
- Uses the training env's honeypot count, FNR, FPR, attack rate and critical node. These were hardcoded to 2 / 0.25 / 0.2 / 0.9 / random.
- Runs the episodes **once**. They used to run twice into the same counters while dividing by 50.
- Win = final reward is 1 (caught in a honeypot). `episode_reward > 0` counted any catch after about 10 steps as a loss.
- DSP = wins / episodes (the last running value). It used to average the running values, which understated DSP and produced the 1.01.
- Evaluates the greedy policy: epsilon is set to 0 during evaluation and the agents' random warm-up branch is skipped.

### Driver: `driver_v2.py`
- Single-run mode passed a random NTPG key (an IP) as the critical node. It now uses the env default (node ID 6, the node your earlier runs actually used).
- Multi-run mode called the env without the critical-node argument, which raised a TypeError. That argument is now optional.
- Result files were saved as `output_dsp_trainingtime/DDQN_3_INPUT_v2result_...txt` (folder and file name joined without `/`). They now go inside `output_dsp_trainingtime/<model>/`.
- Every prompt can now be passed as a command-line option, so training can run unattended on a server. Anything left out is still asked. Example:
  ```bash
  python Development/TrainingCode/driver_v2.py --fnr 0.2 --fpr 0.14 --attack-rate 0.8 --ntpg ntpg_inf --model-file ddqn3v2 --model 2 --input-type 2 --training 1 --episodes 20000 --decoys 2
  ```

## Round 2 (same day, after the first full training run)

The first full DDQN 3-input v2 run trained, but DSP stayed at 0.36–0.52, below the random policy, and the process grew to 24.7 GB of RAM by step 19,000. Causes and fixes:

### Agents
| What | Files | Before | After |
|---|---|---|---|
| Q-network output | the 5 DDQN agents, `sarsa/sarsa_agent_3input.py` | `softmax`: outputs in 0..1 summing to 1, so the -1 for losing could not be learned | `linear` |
| DDQN loss | the 5 DDQN agents | custom `ddqn_loss_fn` reading a global `actionsAppend` list that grew by 100 entries per step and was never cleared | `'mse'` (the target vector already equals the prediction except at the taken action); `actionsAppend.append` removed |
| Memory leak / speed | all DDQN, SARSA, A2C agents | `model.predict()` / `model.fit()` on every step (leaks memory in TF 2.13 and is slow) | `predict_on_batch()` / `train_on_batch()` |
| DDQN exploration | `driver_v2.py`, DDQN `selectAction()` | started at 0.1 and decayed ×0.999 per step to ~0; `ddqn_agent_headless_v2.py` never decayed | starts at 1.0 (`ddqn_epsilon`), decays ×0.999 per step to a floor of 0.05. SARSA and A2C keep 0.1 |
| Action count | DDQN agents, `sarsa_agent_3input.py`, `driver_v2.py` | `C(K, M)` from a formula | `len(env.action_space())` (needed because of the env change below) |

### Evaluation: `evaluation_headless_v2.py`
- DSP was passed from `evaluate()` to `retrieveDSPdict()` through a file `dsp_globalcounter.tmp` in the working directory. Two runs started from the same folder overwrote and deleted each other's file: one crashed (`FileNotFoundError`), and a run could record another run's DSP. It's now kept in memory.

### Driver: `driver_v2.py`
- New `--max-steps` option: stop after the evaluation at that step (e.g. `--max-steps 30000`, the last checkpoint of the earlier runs).

### Environment: `NetworkHoneypotEnv_base_v4.py`
In `ntpg_inf.csv`, nodes with no outgoing edges are written as self-loops (node IDs 1, 7 and 8, e.g. `192.168.9.2 -> 192.168.9.2`). The old start-node choice put the attacker on node 1 or 7 about 80% of the time. From there it could only "re-enter" its own node every step, so any honeypot placed on it was a catch. That alone gave a random policy ~0.87 DSP.

| What | Before | After |
|---|---|---|
| Self-loops | counted as a move into the same node | ignored; on a dead-end node the attacker stays put |
| Attacker start | node IDs 1, 2, 7 weighted 0.00834 / 0.00338 / 0.00612 | random non-critical node with a real outgoing edge |
| Honeypot on the critical node | allowed (a free win whenever the attacker reached it) | not offered; actions on `ntpg_inf` go from 45 to 36 |

Not changed: the adaptive env in `A2C_Subnet/` (model 8) generates its own random graphs and still has its old start/self-loop behavior.

## What this changes in your results
- Old results in `output_dsp_trainingtime/` came from untrained models and the broken evaluation. Don't compare new runs against them as if they were the same experiment.
- Models saved before round 2 have 45 outputs and won't load into the new 36-action env. Retrain.
- **Baselines to beat** on `ntpg_inf` (2 honeypots, attack rate 0.8, 2000 episodes per setting, measured with the round-2 env):

  | FNR / FPR | 0.05 / 0.02 | 0.1 / 0.06 | 0.15 / 0.1 | 0.2 / 0.14 |
  |---|---|---|---|---|
  | random honeypots each step | 0.393 | 0.401 | 0.383 | 0.379 |
  | heuristic: likeliest next hops of the latest alert | 0.764 | 0.746 | 0.731 | 0.752 |

  A trained model should land clearly above random, ideally near or above the heuristic.
- FNR/FPR now change what the agent sees, so DSP should vary with them once a model learns from the observations.

## Not verified
- Not run with TensorFlow / tf_agents (they aren't installed on this machine). Checked: every changed file parses, and the env was smoke-tested with stubbed tf_agents on real NTPG data. Run a short training (for example 250 steps) on your Ubuntu VM to confirm.
- Not changed: `evaluation_v2.py`, the demo/legacy agents, the ProductionCode copies, and `A2C_Subnet/misc.py` (`create_environment_from_baseEnv` passes `[5]`, which now means node ID 5; inference doesn't use the critical node).

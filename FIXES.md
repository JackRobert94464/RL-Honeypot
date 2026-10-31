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

## What this changes in your results
- Old results in `output_dsp_trainingtime/` came from untrained models and the broken evaluation. Don't compare new runs against them; retrain.
- **Baseline to beat:** a smoke test of the fixed env on `ntpg_inf` (2 honeypots, attack rate 0.8, 2000 episodes) gave a **random** honeypot policy about **0.87 DSP**, nearly the same at FNR/FPR 0.05/0.02, 0.2/0.14 and 0.5/0.5. That's because honeypots can be reshuffled every step for free. A trained model is only useful if it clearly beats this. Consider adding a cost for moving honeypots or keeping them fixed per episode if you want FNR/FPR to matter more.
- With the fixed env, FNR/FPR now actually change what the agent sees, so DSP should vary with them once a model learns from the observations.

## Not verified
- Not run with TensorFlow / tf_agents (they aren't installed on this machine). Checked: every changed file parses, and the env was smoke-tested with stubbed tf_agents on real NTPG data. Run a short training (for example 250 steps) on your Ubuntu VM to confirm.
- Not changed: `evaluation_v2.py`, the demo/legacy agents, the ProductionCode copies, and `A2C_Subnet/misc.py` (`create_environment_from_baseEnv` passes `[5]`, which now means node ID 5; inference doesn't use the critical node).

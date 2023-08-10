"""
Short introduction to the package.

## Abstract base class
Uses the PettingZoo Parallel API. All agents act synchronously, with actions, 
observations, returns and dones passed as dictionaries keyed by agent names. 
The code can be found in `multiagentgymnax/multi_agent_env.py`

The class follows an identical structure to that of `gymnax` with one execption. 
The class is instatiated with `num_agents`, defining the number of agents within the environment.

## Environment loop
Below is an example of a simple environment loop, using random actions.

"""

import jax
import jax.numpy as jnp
from smax import make
from smax.environments.mini_smac.heuristic_enemy import create_heuristic_policy
from smax.viz.visualizer import Visualizer, MiniSMACVisualizer
import os
os.environ["TF_CUDNN_DETERMINISTIC"] = "1"
# Parameters + random keys
max_steps = 5
key = jax.random.PRNGKey(1)
key, key_r, key_a = jax.random.split(key, 3)

# Instantiate environment
with jax.disable_jit(False):
    env = make("HeuristicEnemyMiniSMAC", enemy_shoots=True)
    # env = make("MiniSMAC")
    obs, state = env.reset(key_r)
    print("list of agents in environment", env.agents)

    # Sample random actions
    key_a = jax.random.split(key_a, env.num_agents)
    actions = {
        agent: env.action_space(agent).sample(key_a[i])
        for i, agent in enumerate(env.agents)
    }
    print("example action dict", actions)

    policy = create_heuristic_policy(env, 0)
    state_seq = []
    returns = {a: 0 for a in env.agents}
    for i in range(max_steps):
        # Iterate random keys and sample actions
        key, key_s, key_seq = jax.random.split(key, 3)
        key_a = jax.random.split(key_seq, env.num_agents)
        actions = {
            agent: policy(key_a[i], obs[agent]) for i, agent in enumerate(env.agents)
        }
        # actions = {agent: env.action_space(agent).sample(key_a[i]) for i, agent in enumerate(env.agents)}
        state_seq.append((key_seq, state, actions))
        # Step environment
        obs, state, rewards, dones, infos = env.step(key_s, state, actions)
        returns = {a: returns[a] + rewards[a] for a in env.agents}
        if dones["__all__"]:
            print(f"Returns: {returns}")

print(f"Returns: {returns}")
viz = MiniSMACVisualizer(env, state_seq)

viz.animate(view=False, save_fname="output.gif")

from random import randint
import sys, inspect
from policies import *

# Generate x amount of seeds for each configuration
HARDSEEDS = [13, 87, 95, 10, 42]
seeds = []

if len(sys.argv) > 1:
    len = int(sys.argv[1])
    new_seeds = []
    for i in range(len):
        seeds.append(randint(0, 1000))
else:
    seeds = HARDSEEDS

# Get all policies under "policies" module
def find_subclasses(module, clazz, blacklist=[]):
    return [
        cls
            for name, cls in inspect.getmembers(module)
                if inspect.isclass(cls) and name not in blacklist
                and issubclass(cls, clazz)
    ]
    
blacklist = ['MCTS', 'PlayerInput', 'Policy'] # Policies NOT to run!!
policy_classes = find_subclasses(sys.modules['policies'], Policy, blacklist)

# Function to run a match between two policies given a seed
def run_match(policy1, policy2, seed):
    print(f"Running match between {policy1.__name__} and {policy2.__name__} with seed {seed}")
    # Run the game
    env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
    env.reset(seed=seed)
    env.render()
    cards_age = {}
    for i in range(env.num_agents):
        cards_age_key = f"player_{i}"
        cards_age[cards_age_key] = [0, 0, 0, 0, 0]
    
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        card_age = cards_age[agent]
        if termination or truncation:
            action = None
            print("Game over")
            print("""
                             ...,?77??!~~~~!???77?<~.... 
                        ..?7`                           `7!.. 
                    .,=`          ..~7^`   I                  ?1. 
       ........  ..^            ?`  ..?7!1 .               ...??7 
      .        .7`        .,777.. .I.    . .!          .,7! 
      ..     .?         .^      .l   ?i. . .`       .,^ 
       b    .!        .= .?7???7~.     .>r .      .= 
       .,.?4         , .^         1        `     4... 
        J   ^         ,            5       `         ?<. 
       .%.7;         .`     .,     .;                   .=. 
       .+^ .,       .%      MML     F       .,             ?, 
        P   ,,      J      .MMN     F        6               4. 
        l    d,    ,       .MMM!   .t        ..               ,, 
        ,    JMa..`         MMM`   .         .!                .; 
         r   .M#            .M#   .%  .      .~                 ., 
       dMMMNJ..!                 .P7!  .>    .         .         ,, 
       .WMMMMMm  ?^..       ..,?! ..    ..   ,  Z7`        `?^..  ,, 
          ?THB3       ?77?!        .Yr  .   .!   ?,              ?^C 
            ?,                   .,^.` .%  .^      5. 
              7,          .....?7     .^  ,`        ?. 
                `<.                 .= .`'           1 
                ....dn... ... ...,7..J=!7,           ., 
             ..=     G.,7  ..,o..  .?    J.           F 
           .J.  .^ ,,,t  ,^        ?^.  .^  `?~.      F 
          r %J. $    5r J             ,r.1      .=.  .% 
          r .77=?4.    ``,     l ., 1  .. <.       4., 
          .$..    .X..   .n..  ., J. r .`  J.       `' 
        .?`  .5        `` .%   .% .' L.'    t 
        ,. ..1JL          .,   J .$.?`      . 
                1.          .=` ` .J7??7<.. .; 
                 JS..    ..^      L        7.: 
                   `> ..       J.  4. 
                    +   r `t   r ~=..G. 
                    =   $  ,.  J 
                    2   r   t  .; 
              .,7!  r   t`7~..  j.. 
              j   7~L...$=.?7r   r ;?1. 
               8.      .=    j ..,^   .. 
              r        G              . 
            .,7,        j,           .>=. 
         .J??,  `T....... %             .. 
      ..^     <.  ~.    ,.             .D 
    .?`        1   L     .7.........?Ti..l 
   ,`           L  .    .%    .`!       `j, 
 .^             .  ..   .`   .^  .?7!?7+. 1 
.`              .  .`..`7.  .^  ,`      .i.; 
.7<..........~<<3?7!`    4. r  `          G% 
                          J.` .!           % 
                            JiJ           .` 
                              .1.         J 
                                 ?1.     .'         
                                     7<..%
""")
        else:
            mask = observation["action_mask"]
            obs = observation["observation"]
            if agent == "player_0":
                policy = policy1(env, agent, mask, obs, card_age) 
                # get policy name and print it
                print(f"Policy {policy1.__name__} is playing against {policy2.__name__}")
            else:
                policy = policy2(env, agent, mask, obs, card_age)
                print(f"Policy {policy2.__name__} is playing against {policy1.__name__}")
            action = policy.run()
            print(f"Agent {agent} chose action {action}")
            env.action_history.append(action)
            cards_age[agent] = update_card_age(card_age, action)

            # print the hanabi score
            print(f"Hanabi score: {policy.calculate_score()}")

        env.step(action)

# Get each pair combination of agents (policies)
for i in range(len(policy_classes)):
    for j in range(len(policy_classes)):
        for seed in seeds:
            run_match(policy_classes[i], policy_classes[j], seed)


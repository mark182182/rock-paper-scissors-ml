# This entrypoint file to be used in development. Start by reading README.md
from RPS import player
from RPS_game import abbey, kris, mrugesh, play, quincy, random_player
from shared import Config

# print("-- Starting exploration --")
# play(player, random_player, 1000)
# play(player, abbey, 1000)
# play(player, kris, 1000)
# play(player, random_player, 1000)
# play(player, mrugesh, 1000)
# play(player, abbey, 1000)
# play(player, quincy, 1000)
# print("Done")

Config.SHOULD_READ_EXPLORATION_FROM_JSON = True

Config.EXPLORATION_ENABLED = False

print("-- Starting exploitation --")
print("Playing against Kris")
play(player, kris, 1000)
print("Playing against Mrugesh")
play(player, mrugesh, 1000)
print("Playing against Abbey")
play(player, abbey, 1000)
print("Playing against Quincy")
play(player, quincy, 1000)

# Uncomment line below to play interactively against a bot:
# play(human, abbey, 20, verbose=True)

# Uncomment line below to play against a bot that plays randomly:
# play(human, random_player, 1000)


# Uncomment line below to run unit tests automatically
# main(module='test_module', exit=False)

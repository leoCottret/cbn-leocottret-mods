# TLDR 
- This script is used to test martial arts balance by stimulating key inputs and reading data from the save file (cf video)

# Original PR content

#### Summary
SUMMARY: Balance "Add script to tests the balance of martial arts"


#### Purpose of change
Is the AutoIt version of #1921 (Bright Night PR).
The cpp version was a start but it didn't take into account some martial arts buffs. Also some combat techniques needed to be trigger manually (eg counter attacks). This wasn't ideal.
Also, I felt that the cpp tests couldn't be reliable until we had a way to compare them to some functional tests that just extract the damage done to monsters in-game (through the save file).

#### Describe the solution
Create a script that stimulate key inputs through the game, and extract the impact of those keys through the save file.
**The script does support mods (that adds and/or modify weapons and/or martial arts)**
A demo:

https://user-images.githubusercontent.com/71428793/193895103-15e9e4f9-31c5-4259-9b0b-10cbdbdb5a91.mp4


Explanation:
- 0:00 Create walls to counter knockback effects from player/monster
- 0:04 Create roof to protect from rain
- 0:06 Set player stats
- 0:07 Select martial art, quicksave, verify the right one is selected
- 0:10 Place dirt in front and wait 15 minutes to reset warmth
- 0:14 Reset hit points, pain and stamina
- 0:16 Spawn stacks of armor set on the ground. Since this part is a bit long, I spawn a lot of them then I can just equip them. I keep track of set numbers, and respawn some when there's no more of them
- 0:22 Equip a set
- 0:22 Spawn the tested weapon, equip it, quicksave, verify it's equipped
- 0:27 Reset player needs
- 0:28 (Re)set player skills
- 0:29 Spawn lava where the monster will be. The monster doesn't take damage since it's spawned through the debug menu (I guess, I just verified it didn't take damage), and everything it will drop on death, including its corpse, will be instantly deleted.
- 0:30 Spawn the tested monster
- 0:32 Hit him 3 times (3 fightCycle()), reset player hit points, pain and stamina, repeat
 (do the part below every ~36 times we tried to hit the monster)
- 0:55 Quicksave, get the total damage done since the last save, then kill it
- 0:58 Place dirt and wait 15 minutes to reset warmth
- (Then usually, destroy all items on player, do 0:14 and restart from 0:22)
- 1:02 This is just me holding the escape key to interrupt the script so the video doesn't become too heavy

At the end the average damage is calculated, and you get a markdown table that can be copy pasted as is.
Cf Additional context

#### Describe alternatives you've considered
Just create a POC and go back to cpp tests. But I wanted to see how far this concept could go.


#### Testing
I tested the script often through all its developpement

I also integrated many internal tests to see if everything is working properly each time the script is started:
- An automatic pause if the game is not the focused window anymore, then an automatic switch back to it after a few seconds (prevent pop ups and the like to mess up with the tests)
- Error Message if a file can't be loaded
- EM if the instructions about monster health have not been followed correctly
- EM if a weapon from a martial art can't be found in weapon files
- EM if a weight or a volume unit can't be converted by the script
- EM if the selected martial art is not the right one
- EM if a fight cycle method doesn't exist
- EM if an copy-from weapon linked to a martial art compatible weapon can't be found in weapon files
- EM if a weapon ends up with 0 attack cost
- A way to brute force the items around you if you didn't equip the weapon to be tested (can theoritically happen on some weapons). Then EM if it can't find it
- And other misc EM/systems to prevent problems occuring

I also got the script running for 16 hours straight without problem.

#### Additional context
The instructions to use the script yourself are in the script (for Linux users, you may manage to run it through WINE although I didn't test it)

This is an example of the formatted results you get without modifications (except keeping the top 3 weapons):
# NEW TESTS STARTING AT - 04/10/2022 17:50:36
Fight cycle method: Wait then hit, Iterations: 80, Fight cycles: 3
## STATS: 12, SKILLS: 5, M: Kevlar hulk
| Martial Art Name                | Weapon                          | Avg dmg |
|---------------------------------|---------------------------------|---------|
| Barbaran Montante               | battle axe                      | 40.87 |
| Barbaran Montante               | mace                            | 36.85 |
| Barbaran Montante               | war hammer                      | 36.47 |
## STATS: 18, SKILLS: 9, M: Kevlar hulk
| Martial Art Name                | Weapon                          | Avg dmg |
|---------------------------------|---------------------------------|---------|
| Barbaran Montante               | war hammer                      | 93.81 |
| Barbaran Montante               | battle axe                      | 80.64 |
| Barbaran Montante               | morningstar                     | 74.95 |
|                                 |                                 |         |
## STATS: 12, SKILLS: 5, M: zombie hulk
| Martial Art Name                | Weapon                          | Avg dmg |
|---------------------------------|---------------------------------|---------|
| Fior Di Battaglia               | fire axe                        | 81.83 |
| Fior Di Battaglia               | battle axe                      | 69.33 |
| Fior Di Battaglia               | lobotomizer                     | 65.27 |
|                                 |                                 |         |
## STATS: 18, SKILLS: 9, M: zombie hulk
| Martial Art Name                | Weapon                          | Avg dmg |
|---------------------------------|---------------------------------|---------|
| Fior Di Battaglia               | fire axe                        | 92.45 |
| Barbaran Montante               | war hammer                      | 91.21 |
| Fior Di Battaglia               | battle axe                      | 82.41 |
|                                 |                                 |       |

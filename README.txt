Group members: William Klunder, Connor Lowe

This assignment tasked us with using a hierarchical task network in order
to come up with a plan for producing certain items using crafting recipes
from Minecraft. This program uses crafting.json in order to extract the 
recipes.


Heuristics:
In order to get a solution quickly and prevent infinite looping from occuring,
we set up a few functions that can prune search branches in the task network.

The first heuristic we came up with was preventing the depth of task networks from 
going too deep, so we set a check that ends the branch if the depth is above 100.

The second heuristic was to prune the branch if a tool was being crafted
more than once (such as crafting a wooden axe if one was already crafted).

The final heuristic was to prevent any item from being crafted if there was already
more than 35 of that item in the state, to prevent the same items being recrafted many times.
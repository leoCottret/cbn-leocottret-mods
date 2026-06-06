local mod = game.mod_runtime[game.current_mod]
gdebug.log_info("The_Milky_Way: preload online")

-- executed when a player interacts with a npc (with a bucket in his inventory yadiyada), then the milking activity starts
game.add_hook("on_try_npc_interaction", function(params)
  if mod and mod.on_try_npc_interaction then
    return mod.on_try_npc_interaction(params)
  end
end)

-- executed every turn, to know if player is milking or not, and call end_milk
gapi.add_on_every_x_hook(TimeDuration.from_turns(1), function(...)
  if mod.on_tick_milking then mod.on_tick_milking(...) end
end)
local mod = game.mod_runtime[game.current_mod]
gdebug.log_info("XE038: preload online.")

game.add_hook("on_character_effect", function(params)
	if mod and mod.on_character_effect then
		return mod.on_character_effect(params)
	end
end)

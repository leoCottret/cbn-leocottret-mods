local mod = game.mod_runtime[game.current_mod]

-- reduce effect duration when a real monster spawns by this amount
local real_spawns_reduction = { 5, 20, 40, 80, 100, 120, 200, 500 }
-- monsters that can spawn depending on effect intensity: be careful that they are not from an in-repo mod (and thus not "pure" vanilla)
local real_spawns = {
  { "mon_blob_small" }, -- 0
  { "mon_zombie", "mon_kreck", "mon_blood_sacrifice", "mon_shadow", "mon_shadow_snake", "mon_twisted_body", "mon_vortex", "mon_zombie_hollow", "mon_blob"  }, -- 375
  { "mon_hunting_horror", "mon_mi_go", "mon_zombie_tough", "mon_spawn_raptor", "mon_blob_large", "mon_zombear", "mon_zombie_gasbag" }, -- 750
  { "mon_gozu", "mon_flesh_angel", "mon_zombie_brute", "mon_skeleton_brute", "mon_zombie_smoker_evolved_toxic", "mon_zombie_brute_ninja" }, -- 1125
  { "mon_homunculus", "mon_mi_go_guard", "mon_mi_go_surgeon", "mon_mi_go_slaver", "mon_zombie_smoker_evolved_grappler", "mon_zombie_bio_op" }, -- 1500
  { "mon_mothman", "mon_hound_tindalos", "mon_mi_go_myrmidon", "mon_mi_go_scout", "mon_zombie_bio_op2" }, -- 1875
  { "mon_dog_thing", "mon_zombie_hulk", "mon_zombie_soldier_acid_3", "mon_zombie_kevlar_2", "mon_skeleton_hulk", "mon_zombie_nemesis", "mon_zombie_brute_grappler" },-- 2250
  { "mon_zombie_master", "mon_flaming_eye", "xe038_mon_zombie_kevlar_3", "mon_jabberwock" } -- 2625
}

--------------------------------------------------------------------------
------------------------ MAIN on_character_effect ------------------------
--------------------------------------------------------------------------
function mod.on_character_effect(params) -- effect, char
  -- local player = gapi.get_avatar() PS: I could easily spawn hallucinations for just the player, but I think the concept of "reality disruption" affecting even the NPCs is even better
  local xe038_reality_disruption_effect = EffectTypeId.new("xe038_zombie_hulk_flaming_eye_reality_disruption_effect")
  -- we don't want potential other effects that use EFFECT_LUA_ON_TICK
  if not params.char:has_effect(xe038_reality_disruption_effect) then return end

  if math.random(0, 5) == 0 then -- 16% of the time, we spawn something
    -- we want to avoid monsters spawning too close, but too far makes their spawn useless (many monsters are near-sighted?)
    local char_pos = params.char:get_pos_ms()
    local dx, dy = math.random() < 0.5 and math.random(-25, -10) or math.random(10, 25), math.random() < 0.5 and math.random(-25, -10) or math.random(10, 25)
    -- weird hack due to tripoint migration, monster pos, with the clean way it would be incompatible with stable I think
    local m_pos = char_pos
    m_pos.x, m_pos.y, m_pos.z = char_pos.x + dx, char_pos.y + dy, char_pos.z

    if math.random(0,10) < 10 then -- 91% of the time, hallu
      gapi.spawn_hallucination(m_pos)
    else -- 9%, it's real! -> so it's roughly a 1.4% chance of spawning a real monster, but it happens every turn!
      local char_effect = params.char:get_effect(xe038_reality_disruption_effect)
      local char_danger_level = (char_effect:get_intensity() // 375) + 1 -- lua = array indices start at 1 = psychopaths; And // = integer division operator
      local monster_id = real_spawns[char_danger_level][math.random(#real_spawns[char_danger_level])]
      local monster = gapi.place_monster_at(MonsterTypeId.new(monster_id), m_pos)
      if monster then
        monster.faction = MonsterFactionIntId.new(MonsterFactionId.new("zombie")) -- we don't want all of them fighting each other, do your job and attack the player >:(
        -- remove duration from character to avoid spawning too many high tier monsters
        -- PS: setting a negative duration increases the timer, but with the 2(ish)% probability of spawning a monster, + the time reduction being very low for low levels, the effect is insignificant
        char_effect:set_duration(char_effect:get_duration()-TimeDuration.from_seconds(real_spawns_reduction[char_danger_level]), true) -- idk what this true is, but set duration wants a boolean as second value, so I'm giving it one
      else
        gdebug.log_info("XE038 WARNING: could not spawn " .. monster_id)
      end
    end
  end
end

-- PS: if we allow monsters too (could be possible with an other hook), I'm concerned about the hulk flaming eye spawning a massive amount of monsters by attacking random things

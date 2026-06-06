-- MOD OPTIONS
local CORPORATE_MILK = false -- Change false to true to get a buisness like milking, like you would do to a coworker or client
local MILK_ACTIVITY_MARGIN = 1.2 -- In case you don't get milk when you milk a NPC, increase this value (eg: 1.4, or even 10 if nothing works, but milking will be near instant)
-- END MOD OPTIONS

local mod = game.mod_runtime[game.current_mod]    

-- All constants declared here for optimisation
local milkMutationId = MutationBranchId.new("TMW_PROLACTIN_AMPLIFICATION") -- type: MutationBranchId
local milkCharacterActivityId = ActivityTypeId.new("TMW_ACT_MILK_CHARACTER")
local milkRawId, bucketId = ItypeId.new("milk_raw"), ItypeId.new("bucket")
local speedSkillId = SkillId.new("speech")
local milkedId = MoraleTypeDataId.new("tmw_morale_milked")

local NPC_milk_quantity = 20
local g, s, l = gapi.add_msg, string.format, locale.gettext -- Compress those function names a bit for readibility (we use all 3 for each message print)


-- Get the container that will be filled with the milk
local function get_target_container(player, NPC)
    -- 1 - Get containers with enough space to get the whole milk batch
    local items = player:all_items(false)
    if not items then return end -- Leaving it here but since player has a bucket this can theoritically never be true
    local valid_containers = {}
    for _, item in ipairs(items) do
      -- we ignore items with rotten in the name by default, thus we ignore rotten milk
      if item:remaining_capacity_for_id(milkRawId, true) >= NPC_milk_quantity and not item:display_name(1):find("(rotten)", 1, true) then -- PS: item:display_name(1):find("in the name") -> number, item:display_name(1):find("not in the name") -> nil
        table.insert(valid_containers, item)
      end
    end

    if #valid_containers == 0 then
        return
    end

    -- 2 - If a container already has milk, use it
    local target_container = nil
    for _, container in ipairs(valid_containers) do
      if container:has_item_with_id(milkRawId) then
        target_container = container
        break
      end
    end

    -- 3 - If no container has milk, pick the one with the largest capacity
    if not target_container then
      local max_capacity = -1
      for _, container in ipairs(valid_containers) do
        local capacity = container:remaining_capacity_for_id(milkRawId, true)
        if capacity > max_capacity then
          max_capacity = capacity
          target_container = container
        end
      end
    end

    return target_container
end


-- Print the "cannot milk but player probably tried" message to the sidebar
local function print_cannot_milk_but_tried_message(NPC, target_container_name) -- Milked NPC, name of container that will be filled with milk
  if CORPORATE_MILK then
    g(5, s(l("%s cannot be milked again for the time being."), NPC:get_name()))
  else
    local r = math.random(0, 3)
    if r == 0 then
      g(5, s(l("As you begin pressing a nipple, a muffled sound comes from %s's mouth."), NPC:get_name()))
    elseif r == 1 then
      g(5, s(l("As your hand approaches %s, they dodge it with a swift movement."),  NPC:get_name()))
    elseif r == 1 then
      g(5, s(l("You eagerly put your %s on the ground, but %s stops your momentum: they just cannot do it anymore."), target_container_name,  NPC:get_name()))
    elseif r == 2 then
      g(5, s(l("%s thanks you for your enthusiasm, but their body isn't an infinite well."),  NPC:get_name()))
    else
      g(5, s(l("%s looks at your bucket, confused, and shakes their head from side to side."),  NPC:get_name()))
    end

    local r2 = math.random(0, 3)
    if r2 == 0 then
      NPC:say("I think you've had enough for now, friend.")
    elseif r2 == 1 then
      NPC:say("All good things must come to an end, friend.")
    elseif r2 == 2 then
      NPC:say("Please, there will be more soon enough, friend.")
    else
      NPC:say("Let's not go overboard, friend.")
    end
  end
end

-- Print the milking message to the sidebar, added as a function because the randomized message
local function print_milk_message(NPC, target_container_name) -- Milked NPC, name of container that will be filled with milk
  if CORPORATE_MILK then
    g(0, s(l("You milk %s into the %s."), NPC:get_name(), target_container_name))
  else
    local r = math.random(0, 3)
    if r == 0 then
      g(0, s(l("You gently milk %s into the %s."), NPC:get_name(), target_container_name))
    elseif r == 1 then
      g(0, s(l("You tenderly milk %s into the %s."), NPC:get_name(), target_container_name))
    elseif r == 2 then
      g(0, s(l("You delicately milk %s into the %s."), NPC:get_name(), target_container_name))
    else
      g(0, s(l("You carefully milk %s into the %s."), NPC:get_name(), target_container_name))
    end
  end
end


-- Print the milking message to the sidebar, added as a function because the randomized message
local function print_high_success_milk(NPC, rb) -- Milked NPC, relation bonus
  if CORPORATE_MILK then
    if rb == 1 then
      g(0, s(l("You did pretty well.")))
    elseif rb == 2 then
      g(0, s(l("You did very good.")))
    elseif rb == 3 then
      g(0, s(l("You handled that with impressive skill.")))
    else
      g(0, s(l("Outstanding! That couldn't have gone better.")))
    end
  else
    if rb == 1 then
      g(0, s(l("This skinship brings you closer."), NPC:get_name()))
      NPC:say("Thanks. I really enjoyed it.")
    elseif rb == 2 then
      g(0, s(l("You are such a skilled milker, that they cannot help making satisfactory mooing sounds."), NPC:get_name()))
      NPC:say("Mooh...mmh...uh...mOoh...*sigh*. Thank you. For everything.")
    elseif rb == 3 then
      g(0, s(l("You milk %s like a virtuoso playing a masterpiece. They seem elated."), NPC:get_name(), NPC:get_name()))
      NPC:say("I didn't believe I could ever feel such bliss. Thank you. So, very much.")
    else
      g(0, s(l("%s looks up, a single tear rolling down their cheek. They look enthralled by the beauty of this doomed world."), NPC:get_name()))
      NPC:say("It's as if my body and soul were gently cradled by the Divine. I could see the stars and feel everything, everywhere, all at once. I understand now... The Milky Way...")
    end
  end

end

-- Process high success milk result and call print high success milk function
local function process_high_success_milk(NPC, roll_milk) -- Milked NPC, milk success roll, should we use his/her, and he/she
  -- Logic for relation increase
  -- Min: player starts with around 10 dex, 0 speech, no Prolactin Amplification = [10, 110] -> ~10% chance for relation increase (above 100)
  -- Max: 20 dex, 10 speech, PA (+20) = [50, 150] -> ~50% chance for relation increase (dex could become even higher, especially with mods but eh)
  -- Max2: and 10% chance to reach peak, divine milking. Seems ok.
  local rb = 0
  if roll_milk < 120 then
    rb = 1
  elseif roll_milk < 130 then
    rb = 2
  elseif roll_milk < 140 then
    rb = 3
  else
    rb = 5 -- not a mistake, like this mod
  end

  print_high_success_milk(NPC, rb)
  
  local o = NPC.op_of_u
  NPC.op_of_u = o.new(o.trust + rb, o.fear - rb, o.value + rb, o.anger - rb, o.owed) -- trust fear value anger owed
  return rb * 2 -- TIMES 2! Wouldn't you be elated too (...be honest with yourself)
end


-- Spawn monster around player, in one neat function
local function spawn_monster_around_player(player, monster_id, mn, md) -- player obj, monster id to spawn, minimum distance from player, maximum distance
  local char_pos = player:get_pos_ms()
  local dx, dy = math.random() < 0.5 and math.random(-md, -mn) or math.random(mn, md), math.random() < 0.5 and math.random(-md, -mn) or math.random(mn, md)
  local m_pos = char_pos
  m_pos.x, m_pos.y, m_pos.z = char_pos.x + dx, char_pos.y + dy, char_pos.z
  local monster = gapi.place_monster_at(MonsterTypeId.new(monster_id), m_pos)
  if not monster then
    gdebug.log_info("TMW WARNING: could not spawn " .. monster_id)
  end
end

-- Process low success milk result and call spawn_monster_around_player function to spaw zombie cow
local function process_low_success_milk(player, NPC) -- player obj, milked NPC, should we use his/her, and he/she
  if CORPORATE_MILK then
    g(1, s(l("You're inexperienced, and %s is having a rough time."), NPC:get_name())) -- 2 = mixed
  else
    local r = math.random(0, 4)
    if r == 0 then
      g(1, s(l("Nervous, you maintain awkward eye contact the entire time. Maybe that wasn’t such a good idea.")))
      NPC:say("...")
    elseif r == 1 then
      g(1, s(l("Your hands are stiff, and %s winces in pain."), NPC:get_name()))
      NPC:say("Mmmh!.....Ouch.....Aow.....")
    elseif r == 2 then
      g(1, s(l("You try telling little jokes to put %s at ease, but each one only brings a forced smile. The result... is disastrous."), NPC:get_name()))
    elseif r == 3 then
      g(1, s(l("You make a horn sound while pressing %s's chest. They stare at you in silent despair."), NPC:get_name()))
      NPC:say("...Really?")
    else
      g(1, s(l("Even basic agricultural equipment would have done a better job. %s looks uneasy."), NPC:get_name()))
    end
  end

  g(1, s(l("You have a bad feeling, as if you angered a powerful entity."))) -- 1 = bad cf MsgType

  -- Spawn a zombie cow far from the player
  spawn_monster_around_player(player, "mon_zow", 25, 40) -- do note, this function can be reused in other scripts

end



-- Finish milking the NPC after the activity ended, finally :,)
local function end_milking() -- character (Character!)

    local player = gapi.get_avatar()

    -- get NPC being milked from storage
    local NPCs = gapi:get_all_npcs()
    local NPC = nil
    for _, npc_candidate in ipairs(NPCs) do
        if tostring(npc_candidate:getID()) == player:get_value("tmw_milked_npc", "") then
          NPC = npc_candidate
        end
    end
    if not NPCs then
      gdebug.log_warn(s("TMW: ERROR We were milking a NPC, but he disappeared... where did he go :/?"))
      return
    end

    -- get container again, in case some weird shinanigans made it unavailable
    local target_container = get_target_container(player, NPC)

    if target_container then
        player:practice(speedSkillId, 25, 15, false) -- Practice speech because they talk during the deed
        target_container:add_item_with_id(milkRawId, NPC_milk_quantity)
        -- Roll a number between 0 and 100, add speaking skill + dexterity + 20 if PA mutation, anything above 100 will increase NPC "relation" with the player
        local roll_milk = player:get_skill_level(speedSkillId) + player:get_dex() + math.random(0, 100)
        if player:has_trait(milkMutationId) then -- who better than cows to know how to milk?
          roll_milk = roll_milk + 20
        end

        local milk_morale = 5 -- morale result for milking activity

        -- critical failure! You angered The Cow-God, spawn 1 zombie cow far from the player and morale malus for NPC. I didn't implement relation malus, not sure if that's a good idea
        -- 13 should only be rolled by low dexterity and low speech players
        -- eg: 10 dex and 0 speaking = 2.9% chance, and since milking trains speaking (speech) it will soon be 0
        if roll_milk <= 13 then
          process_low_success_milk(player, NPC)
          milk_morale = -milk_morale
        -- critical success! Add relation bonus with NPC
        elseif roll_milk > 100 then
          milk_morale = milk_morale + process_high_success_milk(NPC, roll_milk)
        end

        -- Add milked morale, used to check if NPC has been milked recently, and grant a slight benefit if a player milk himself through a NPC
        NPC:add_morale(milkedId, milk_morale, milk_morale, TimeDuration.from_hours(24), TimeDuration.from_hours(24), true, nil)
    else
      gdebug.log_warn("TMW: ERROR No container found for milk after being milked effect is removed. Maybe the container had magic, autofilling liquid?")
    end

    return 

end


--------------------------------------------------------------------------
-- MAIN on_try_npc_interaction
--------------------------------------------------------------------------
function mod.on_try_npc_interaction(params) -- npc (NPC)
    local player = gapi.get_avatar()
    -- The proper way to milk a NPC is with a bucket, otherwise we stop here
    -- If NPC doesn't have a prolactine mutation, we stop here too, of course
    if not player:has_item_with_id(bucketId, true) or not params.npc:has_trait(milkMutationId) then return end
    -- local his_or_her = NPC.male and locale.gettext("his") or locale.gettext("her") -- leaving this here for posterity, but apparently they and their can be used in english, all the better!
    local NPC = params.npc
    local milked_recently = false
    
    local target_container = get_target_container(player, NPC)

    -- 4 - check if npc has been milked recently
    if NPC:get_morale(milkedId) > 0 then -- get_morale returns the current morale value for this morale type, default 0
      milked_recently = true
    end
    
    -- If NPC COULD been milked, player is talking to a NPC with the right mutation and a bucket in his inventory, make the message more visible
    if not target_container and not milked_recently then
        g(4, s(l("You could milk %s, but you don't have a container with enough space left"), NPC:get_name()))
    -- If player has a bucket and a container with enough capacity to fill a milk batch, we assume he wanted to milk the NPC
    elseif target_container and milked_recently then
      g(5, s(l("You already milked %s recently."), NPC:get_name()))
      if math.random(0, 2) == 0 then
        print_cannot_milk_but_tried_message(NPC, target_container:get_type():obj():get_name(1))
      end

    -- 5 - Milk!
    elseif target_container then
        -- We need to access an item name with item:get_type() -> ItypeId -> obj() -> ItypeRaw -> get_name(number) (number define if plural or not)
        print_milk_message(NPC, target_container:get_type():obj():get_name(1)) 
        
        -- From cpp code for cow -> time_duration::from_minutes( milkable_ammo->second / 2 ) -> so here it's 10 min
        -- ACT_MILK searches for a monster (and thus infinitely milk the NPC), and displays "milk an animal" so I had to create a new activity
        -- If the player interrupts the activity, the script DOES NOT stop here, so everything below will be instantly executed
        -- My solution: add a dummy effect "being milked" on the NPC, the trigger an other hook when the effect is finished
        player:assign_activity(milkCharacterActivityId, 60000, 1, 1, "")
        -- It REALLY bugged my mind, but mods are supposed to store data in game objects (?), like the player, an ebook tablet, a NPC, whatever you want
        -- Well I want the player. If the player controls an other NPC, the new storage will be in the new NPC, all good
        player:set_value("tmw_milked_npc", tostring(NPC:getID()))

        -- Logic here: we estimate a time a bit before when the player stops milking activity
        -- Then from on_tick_milking we stop the milking when this time is reached
        -- In seconds (60), assuming 10 min (10), % with the current player speed, leave 20% error margin
        -- This is the weakest part of the script, but now players can change MILK_ACTIVITY_MARGIN if needed so eh
        local estimated_end_activity_seconds = math.floor( (60 * 10 * (100 / player:get_speed())) / MILK_ACTIVITY_MARGIN )
        local end_milk_activity_at = gapi:current_turn() + TimeDuration.from_seconds(estimated_end_activity_seconds)
        player:set_value("end_milk_activity_at", tostring(end_milk_activity_at:to_turn()))

        -- gdebug.log_info("get speed ", tostring(player:get_speed()))
        -- gdebug.log_info("TMW: Start milking activity: end_milk_activity_at " .. tostring(end_milk_activity_at:to_turn()) .. " current_turn " 
        --    .. tostring((gapi:current_turn()):to_turn()) .. " estimated time " .. tostring(estimated_end_activity_seconds))
        
        return false -- on_TRY_npc_interaction + return false = no NPC menu! We do not want a pop up to appear for successful milking
    end

    return -- if NPC has been milked, assuming the player just wants to talk

end



--------------------------------------------------------------------------
-- MAIN 2 add_on_every_x_hook
--------------------------------------------------------------------------
function mod.on_tick_milking()
  local player = gapi:get_avatar()
  local end_milk_activity_at = tonumber(player:get_value("end_milk_activity_at"))
  local current_turn = (gapi:current_turn()):to_turn()
  -- gdebug.log_info("TMW: on_tick_milking executed: end_milk_activity_at " .. tostring(end_milk_activity_at) .. " current_turn " .. tostring(current_turn))
  if end_milk_activity_at then
    if current_turn > end_milk_activity_at then
      player:set_value("end_milk_activity_at", "")
      if player:has_activity(milkCharacterActivityId) then
        player:cancel_activity()
      end
        end_milking()
    -- player probably interrupted the activaty, silent reset
    elseif not player:has_activity(milkCharacterActivityId) then
      -- gdebug.log_info("TMW: INFO assuming player interrupted milking")
      player:set_value("end_milk_activity_at", "")
    end
  end
end

-- Overview of how the script works, for my poor self in the future
-- on_try_npc_interaction is executed when a player examine a NPC
-- If the player has a bucket in his inventory, a container with enough space (can be the bucket), and the NPC has the Prolactin Amplification mutation, start milking it
--   We also print the "start milking" neutral message, and store the time when the milking activity should stop (end_milk_activity_at)
-- on_tick_milking is executed every turns (the reference on performance in BN told me it wasn't a problem for performance, and I guess it's ok for a turn based game)
--   We check if a end_milk_activity_at value has been stored. If yes, we check if the current time is greater than end_milk_activity_at, if yes, we execute end_milking
-- end_milking is where most of the milking logic happens. We get the milked NPC (stored in the player), train speaking skill
--   We calculate roll_milk, low roll milk = bad message + spawn zombie cow + low moral (for NPC), high = good message + relation increase with player + higher moral (for NPC)
-- TESTS: Test the script after modifications: low/mid/high roll_milk success, for CORPORATE_MILK true and false (on top of the changes, obviously)

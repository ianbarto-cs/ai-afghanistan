#!/usr/bin/env python3
"""
Afghanistan War — Text-Based Interactive Adventure Game
--------------------------------------------------------
Author: ChatGPT (GPT-5)
Version: 1.1 (with comprehensive documentation)

OVERVIEW
--------
This is a console-based, text-driven war adventure game set in Afghanistan.
The player takes on the role of a soldier (chosen from several military specialties)
and experiences multiple missions that combine story, decision-making, and combat.

The game features:
- Role selection (Soldier, Sniper, Medic, Engineer, Intelligence Officer)
- Branching mission encounters with random outcomes
- Combat system (3 HP, 10% instant-death, tactical choices)
- Inventory and loot mechanics
- A final extraction outcome with random probabilities
- Extensive documentation for readability and maintainability

To play:
Run this file in a terminal or IDE console with Python 3.8+.
"""

import random
import sys
import time

# ============================================================
# 🧭 UTILITY HELPERS
# ============================================================

def slow_print(text: str, delay: float = 0.01):
    """
    Prints text to the console one character at a time for dramatic effect.
    
    Parameters:
        text (str): The text string to print slowly.
        delay (float): Delay between characters (in seconds). 
                       Set to 0 for instant printing.
    
    Gameplay role:
        Used throughout the game for immersion — it gives narrative moments 
        a cinematic pacing rather than dumping text instantly.
    """
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if delay:
            time.sleep(delay)
    print()

def choose(prompt: str, options: list[str]) -> int:
    """
    Displays a list of numbered options and waits for a valid player choice.
    
    Parameters:
        prompt (str): The question or description shown before the choices.
        options (list[str]): List of choice descriptions.
    
    Returns:
        int: The zero-based index of the selected option.
    
    Gameplay role:
        This is the central input system for all decision-making — 
        combat actions, mission paths, and strategy choices all use it.
    """
    while True:
        slow_print(prompt)
        for i, opt in enumerate(options, 1):
            slow_print(f"  {i}. {opt}")
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                return idx - 1
        slow_print("Please enter a valid option number.")

def roll(pct: float) -> bool:
    """
    Simulates a random percentage chance.
    
    Parameters:
        pct (float): Probability (0-100) of returning True.
    
    Returns:
        bool: True if the roll succeeds, False otherwise.
    
    Gameplay role:
        Core randomization mechanic for combat outcomes, 
        stealth success, headshots, etc.
    """
    return random.random() < (pct / 100.0)

def divider():
    """Prints a horizontal divider line to separate sections for readability."""
    slow_print("-" * 60)

# ============================================================
# ⚙️ ROLE & GAME DATA DEFINITIONS
# ============================================================

# Each role has a unique description, inventory, and attributes
ROLES = {
    "Soldier": {
        "desc": "All-rounder. Balanced in combat and survival.",
        "inventory": ["Standard Rifle", "Combat Knife"],
        "accuracy_bonus": 0,
        "special": "Steady: small chance to dodge incoming fire."
    },
    "Sniper": {
        "desc": "Long-range specialist. Very accurate at range.",
        "inventory": ["Sniper Rifle", "Camouflage"],
        "accuracy_bonus": 15,
        "special": "One-time guaranteed long-range shot (high accuracy)."
    },
    "Medic": {
        "desc": "Healer. Can heal themselves once per mission.",
        "inventory": ["Pistol", "Medical Kit"],
        "accuracy_bonus": -5,
        "special": "Field Heal: restore 1 HP once per mission."
    },
    "Engineer": {
        "desc": "Handles traps and gadgets. Can disable explosives.",
        "inventory": ["Pistol", "Toolkit"],
        "accuracy_bonus": -2,
        "special": "Disarm: chance to avoid traps and ambushes."
    },
    "Intelligence Officer": {
        "desc": "Information & stealth expert. Gains intel before risky choices.",
        "inventory": ["Silenced Pistol", "Encrypted Radio"],
        "accuracy_bonus": -1,
        "special": "Intel: occasional hints about the safest route."
    },
}

# List of possible mission encounter identifiers
ENCOUNTERS = [
    "village_checkpoint",
    "mountain_pass",
    "abandoned_base",
    "night_raze",
    "convoy_ambush"
]

# ============================================================
# 🎖️ PLAYER CLASS
# ============================================================

class Player:
    """
    Represents the player's state, including role, health, inventory, 
    and combat-related statistics.

    Attributes:
        name (str): Player's chosen name.
        role (str): Role identifier (e.g., 'Medic').
        hp (int): Current health points (3 max).
        inventory (list[str]): List of items currently held.
        accuracy_bonus (int): Modifies shooting success rate.
        special (str): Description of the role's special ability.
        mission_heals (int): Remaining self-heals (for Medics only).
        sniper_special_used (bool): Tracks if Sniper's one-time shot is used.
        alive (bool): Player's survival status.
        missions_completed (int): Number of completed missions.
    """
    def __init__(self, name: str, role_name: str):
        role_info = ROLES[role_name]
        self.name = name
        self.role = role_name
        self.hp = 3
        self.inventory = list(role_info["inventory"])
        self.accuracy_bonus = role_info["accuracy_bonus"]
        self.special = role_info["special"]
        self.mission_heals = 1 if role_name == "Medic" else 0
        self.sniper_special_used = False
        self.alive = True
        self.missions_completed = 0

    def show_status(self):
        """Displays the player's name, role, HP, and current inventory."""
        slow_print(f"{self.name} the {self.role} — HP: {self.hp} — Inventory: {self.inventory}")

    def take_damage(self, amount: int = 1):
        """
        Reduces player's HP and checks for death.
        """
        self.hp -= amount
        slow_print(f"You take {amount} damage. HP is now {self.hp}.")
        if self.hp <= 0:
            self.alive = False

    def heal(self, amount: int = 1):
        """
        Restores HP up to a maximum of 3.
        """
        self.hp = min(3, self.hp + amount)
        slow_print(f"You heal {amount} point(s). HP is now {self.hp}.")

# ============================================================
# 🪖 GAME FLOW FUNCTIONS
# ============================================================

def intro():
    """
    Displays the introduction and rules to the player.
    Sets the tone and explains key mechanics before role selection.
    """
    divider()
    slow_print("WELCOME: Afghanistan — Text War Adventure")
    slow_print("You will make choices, fight, loot, and try to survive the war.")
    slow_print("Rules snapshot:")
    slow_print(" - You start with 3 HP. Each hit = -1 HP. 0 HP = death.")
    slow_print(" - Each combat has a 10% chance of instant fatal headshot.")
    slow_print(" - If you survive all missions, you may or may not make it home.")
    slow_print(" - Choose your path carefully; every decision can save or end you.")
    divider()

def pick_role() -> str:
    """
    Lets the player choose a role from the ROLES dictionary.

    Returns:
        str: The chosen role name.
    """
    slow_print("Choose your role:")
    role_names = list(ROLES.keys())
    for i, rn in enumerate(role_names, 1):
        slow_print(f"{i}. {rn} — {ROLES[rn]['desc']}")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(role_names):
            return role_names[int(choice) - 1]
        slow_print("Invalid choice. Enter the number of your desired role.")

def role_intro(player: Player):
    """
    Summarizes the player's chosen role, inventory, and special ability.
    """
    divider()
    slow_print(f"You are {player.name}, a {player.role}. {ROLES[player.role]['desc']}")
    slow_print(f"Starting inventory: {', '.join(player.inventory)}")
    slow_print(f"Special: {player.special}")
    divider()


# ============================================================
# 🧨 ENCOUNTER LOGIC
# ============================================================

def encounter_menu(player: Player, encounter_id: str) -> bool:
    """
    Dispatch function that routes the player to the proper mission encounter.

    Parameters:
        player (Player): The player object, containing all status data.
        encounter_id (str): A string ID representing which encounter is triggered.

    Returns:
        bool: True if mission successful or survived, False if failed or player died.

    Gameplay role:
        Central mission dispatcher — picks the encounter function that matches the ID.
    """
    slow_print(f"Mission: {encounter_id.replace('_', ' ').title()}")
    
    # Special perk: Intelligence Officer sometimes gets a hint.
    if player.role == "Intelligence Officer" and roll(40):
        slow_print("[Intel] Your recon suggests the left route may be less guarded.")

    # Match encounter_id with the proper handler
    if encounter_id == "village_checkpoint":
        return village_checkpoint(player)
    elif encounter_id == "mountain_pass":
        return mountain_pass(player)
    elif encounter_id == "abandoned_base":
        return abandoned_base(player)
    elif encounter_id == "night_raze":
        return night_raze(player)
    elif encounter_id == "convoy_ambush":
        return convoy_ambush(player)
    else:
        slow_print("Unknown mission type encountered — skipping...")
        return True


# ============================================================
# 🏘️ INDIVIDUAL ENCOUNTERS
# ============================================================

def village_checkpoint(player: Player) -> bool:
    """
    Encounter: Village Checkpoint
    Scenario:
        Player approaches a hostile checkpoint. Can attempt diplomacy, stealth, or force.

    Returns:
        bool: True if the player survives; False if dies in combat.
    """
    slow_print("You approach a small village checkpoint controlled by local militia.")
    opts = [
        "Try to talk your way through (stealth or diplomacy).",
        "Take the fields around the checkpoint (possible ambush).",
        "Force entry with weapons (high risk)."
    ]
    choice = choose("How do you proceed?", opts)

    if choice == 0:
        # Diplomacy path
        if player.role == "Intelligence Officer" or roll(65):
            slow_print("You negotiate successfully and pass safely. You find a med pack on the ground.")
            player.inventory.append("Med Pack")
            return True
        else:
            slow_print("The militia grows suspicious. Weapons are raised.")
            return combat_encounter(player, difficulty=1)

    elif choice == 1:
        # Stealthy field path
        slow_print("You move through the tall fields — the wind hides your movement.")
        if roll(40):
            slow_print("Ambush! Hidden fighters open fire from the bushes.")
            return combat_encounter(player, difficulty=2)
        else:
            slow_print("You sneak through unnoticed and loot some spare ammo.")
            player.inventory.append("Ammo")
            return True

    else:
        # Aggressive approach
        slow_print("You open fire and storm the checkpoint!")
        return combat_encounter(player, difficulty=3)


def mountain_pass(player: Player) -> bool:
    """
    Encounter: Mountain Pass
    Scenario:
        A narrow path through mountains where snipers and traps are common.

    Returns:
        bool: True if player survives the crossing.
    """
    slow_print("You face a narrow mountain pass — a perfect ambush site.")
    opts = [
        "Move quickly and stay low.",
        "Use a drone or radio to scout ahead.",
        "Let the Engineer inspect for traps."
    ]
    choice = choose("Your strategy?", opts)

    if choice == 0:
        if player.role == "Sniper" and roll(50):
            slow_print("Your sharp eyes spot movement before danger arises. You cross safely.")
            return True
        if roll(30):
            slow_print("A sniper opens fire — you scramble for cover!")
       # ============================================================
# 🧨 ENCOUNTER LOGIC
# ============================================================
# (Each encounter has its own function, documented in full in the next message)     return combat_encounter(player, difficulty=2)
        slow_print("You slip past quietly and find ration packs.")
        player.inventory.append("Rations")
        return True

    elif choice == 1:
        if "Encrypted Radio" in player.inventory or player.role == "Intelligence Officer":
            slow_print("Your scout relays sniper positions. You avoid danger.")
            return True
        else:
            slow_print("No drone available. The noise alerts nearby fighters.")
            return combat_encounter(player, difficulty=2)

    else:
        if player.role == "Engineer" and roll(70):
            slow_print("You successfully disarm a buried IED. Team morale rises.")
            player.inventory.append("IED Components")
            return True
        elif roll(40):
            slow_print("A trap triggers — partial explosion injures you.")
            player.take_damage(1)
            return player.alive
        slow_print("You cautiously neutralize the traps and move forward.")
        return True


def abandoned_base(player: Player) -> bool:
    """
    Encounter: Abandoned Base
    Scenario:
        Opportunity for loot or unexpected hostiles hiding in the ruins.
    """
    slow_print("You arrive at an abandoned base. Silence hides danger.")
    opts = [
        "Search the main building.",
        "Check perimeter and move on.",
        "Camp overnight in the base."
    ]
    choice = choose("Your action?", opts)

    if choice == 0:
        if roll(50):
            slow_print("You find a weapons cache — upgraded rifle acquired.")
            player.inventory.append("Assault Rifle")
            return True
        else:
            slow_print("Hostile survivors emerge from the shadows!")
            return combat_encounter(player, difficulty=3)

    elif choice == 1:
        slow_print("Perimeter sweep yields a few supplies.")
        player.inventory.append("Handful of Ammo")
        return True

    else:
        slow_print("You camp for the night... footsteps echo nearby.")
        return combat_encounter(player, difficulty=2)


def night_raze(player: Player) -> bool:
    """
    Encounter: Night Raid
    Scenario:
        Player must choose between stealth, waiting, or full-on assault.

    Returns:
        bool: True if mission success, False if failed or death.
    """
    slow_print("Night operation: enemy compound targeted for destruction.")
    opts = [
        "Lead a frontal assault.",
        "Send a stealth team.",
        "Hold and wait for reinforcements."
    ]
    choice = choose("Your approach?", opts)

    if choice == 0:
        return combat_encounter(player, difficulty=3)
    elif choice == 1:
        if player.role in ("Sniper", "Intelligence Officer") or roll(55):
            slow_print("Stealth team succeeds — high-value target captured.")
            player.inventory.append("Intel Documents")
            return True
        else:
            slow_print("Stealth fails; firefight breaks out.")
            return combat_encounter(player, difficulty=3)
    else:
        slow_print("You wait for reinforcements under cover.")
        if roll(50):
            slow_print("Reinforcements arrive; mission success with minimal casualties.")
            return True
        else:
            slow_print("Enemies spot your position before backup arrives!")
            return combat_encounter(player, difficulty=2)


def convoy_ambush(player: Player) -> bool:
    """
    Encounter: Convoy Ambush
    Scenario:
        Protect a convoy under heavy fire or call air support.

    Returns:
        bool: True if survived, False otherwise.
    """
    slow_print("Your supply convoy is under ambush in a narrow valley.")
    opts = [
        "Rush to defend the convoy.",
        "Flank the attackers.",
        "Call in an airstrike."
    ]
    choice = choose("Your decision?", opts)

    if choice == 0:
        return combat_encounter(player, difficulty=3)
    elif choice == 1:
        if player.role == "Soldier" and roll(60):
            slow_print("You execute a flawless flank, neutralizing enemies.")
            player.inventory.append("Looted Supplies")
            return True
        if roll(40):
            slow_print("Flank fails — enemy fire grazes you.")
            player.take_damage(1)
            return player.alive
        slow_print("Flank works, but you sustain minor wounds.")
        player.take_damage(1)
        return player.alive
    else:
        if "Encrypted Radio" in player.inventory or player.role == "Intelligence Officer":
            slow_print("Airstrike called successfully. Enemies eliminated.")
            return True
        slow_print("No communication gear — failed call costs you precious time.")
        return combat_encounter(player, difficulty=2)

# ============================================================
# ⚔️ COMBAT SYSTEM
# ============================================================

def combat_encounter(player: Player, difficulty: int = 2) -> bool:
    """
    Handles combat between the player and a generic enemy.

    Parameters:
        player (Player): The current player object.
        difficulty (int): 1 (easy), 2 (medium), 3 (hard). 
                          Affects accuracy and damage chances.

    Returns:
        bool: True if player survives; False if killed.

    Gameplay role:
        Central battle mechanic with random chance, player tactics, 
        and use of items or role-specific skills.
    """
    divider()
    slow_print("⚔️ Combat initiated!")

    # Instant death check — 10% chance as per system design
    if roll(10):
        slow_print("A single, well-placed shot ends everything. Instant fatality.")
        player.alive = False
        return False

    enemy_hp = difficulty  # basic enemy HP scaling with difficulty
    rounds = 0

    # Main combat loop
    while enemy_hp > 0 and player.alive:
        rounds += 1
        slow_print(f"--- Combat Round {rounds} ---")
        player.show_status()

        # Available player combat actions
        actions = [
            "Shoot left", "Shoot center", "Shoot right",
            "Take cover", "Attempt to flee", "Use special/item"
        ]
        action = choose("Your move:", actions)

        # Attempt to flee the fight
        if action == 4:
            if roll(30 - difficulty * 5):  # harder to flee on higher difficulty
                slow_print("You successfully retreat from the fight.")
                return True
            else:
                slow_print("Failed to flee! You’re caught in the open!")
                if roll(10 + difficulty * 10):
                    slow_print("Enemy fires a critical shot while you escape!")
                    player.take_damage(1)
                continue

        # Use role ability or inventory item
        if action == 5:
            used = False

            # Medic's special heal
            if player.role == "Medic" and player.mission_heals > 0:
                slow_print("You use your medical kit to heal yourself mid-fight.")
                player.heal(1)
                player.mission_heals -= 1
                used = True

            # Sniper’s guaranteed shot (one use)
            elif player.role == "Sniper" and not player.sniper_special_used:
                slow_print("You steady your breath and land a perfect headshot.")
                enemy_hp = 0
                player.sniper_special_used = True
                used = True

            # General item usage
            elif "Med Pack" in player.inventory:
                slow_print("You quickly use a Med Pack.")
                player.heal(1)
                player.inventory.remove("Med Pack")
                used = True

            elif "Assault Rifle" in player.inventory and roll(60):
                slow_print("You fire a controlled burst with your upgraded rifle!")
                enemy_hp = 0
                used = True

            if used:
                # Enemy may counterattack before dying
                if enemy_hp > 0 and roll(40 + difficulty * 10):
                    slow_print("Enemy retaliates before going down!")
                    player.take_damage(1)
                continue
            else:
                slow_print("No useful action taken — enemy fires!")
        
        # Defensive action: Take cover
        if action == 3:
            slow_print("You dive behind cover.")
            if roll(20 + difficulty * 10):
                slow_print("You return fire from cover and hit the enemy!")
                enemy_hp -= 1
            if roll(30 + difficulty * 20):
                slow_print("Enemy lands a glancing shot through cover.")
                player.take_damage(1)
            continue

        # Shooting logic
        base_hit_chance = 50 + player.accuracy_bonus - difficulty * 5
        if action == 1: base_hit_chance += 5  # aiming center is best
        elif action == 0: base_hit_chance -= 5
        elif action == 2: base_hit_chance -= 2

        if roll(max(5, min(95, base_hit_chance))):
            slow_print("You hit your target!")
            dmg = 1
            if "Assault Rifle" in player.inventory and roll(40):
                dmg = 2
            enemy_hp -= dmg
            slow_print(f"You dealt {dmg} damage. Enemy HP: {enemy_hp}")
        else:
            slow_print("You miss your shot.")

        # Enemy counterattack
        if enemy_hp > 0:
            enemy_acc = 40 + difficulty * 15
            if player.role == "Soldier" and roll(20):
                slow_print("You duck just in time — no damage taken.")
            elif roll(enemy_acc):
                if roll(3):  # ~3% mid-fight headshot chance
                    slow_print("Critical hit! A lethal headshot ends it instantly.")
                    player.alive = False
                    return False
                slow_print("Enemy bullet hits you.")
                player.take_damage(1)
            else:
                slow_print("Enemy misses their shot.")

    # Post-combat: player survived
    if player.alive:
        slow_print("Enemy neutralized. You survived the battle.")
        # Loot random item with some probability
        if roll(50 + difficulty * 10):
            loot = random.choice(["Ammo", "Med Pack", "Intel Documents", "Assault Rifle", "Rations"])
            slow_print(f"You scavenge: {loot}")
            player.inventory.append(loot)
        return True
    return False

# ============================================================
# 🏁 MISSION SEQUENCE & FINAL RESOLUTION
# ============================================================

def play_mission_sequence(player: Player, missions: int = 3) -> bool:
    """
    Runs a sequence of missions (encounters) for the player.
    
    Parameters:
        player (Player): The player object.
        missions (int): Number of missions to attempt.
    
    Returns:
        bool: True if player survives all missions, False if dead during any mission.
    
    Gameplay role:
        Handles looping through missions, randomly selecting encounters, 
        and updating player state after each.
    """
    for i in range(1, missions + 1):
        divider()
        slow_print(f"=== Mission {i} of {missions} ===")
        encounter = random.choice(ENCOUNTERS)
        success = encounter_menu(player, encounter)

        if not player.alive:
            slow_print("You have fallen during this mission.")
            return False

        if success:
            slow_print("Mission accomplished.")
            player.missions_completed += 1
        else:
            if player.alive:
                slow_print("Mission had complications, but you push on.")
            else:
                return False

        # Small post-mission healing for Medics
        if player.role == "Medic" and roll(30):
            slow_print("You stabilize minor wounds during rest.")
            player.heal(1)

    return player.alive

def final_resolution(player: Player) -> bool:
    """
    Determines final extraction outcome after all missions completed.
    
    Probabilities:
        - 10% instant death
        - 45% make it home safely
        - 45% die from sustained injuries

    Returns:
        bool: True if player survives and makes it home, False otherwise.
    """
    divider()
    slow_print("All missions complete. Extraction begins...")

    roll_val = random.randint(1, 100)

    if roll_val <= 10:
        slow_print("Tragic luck: a sudden fatal shot ends your journey.")
        player.alive = False
        return False
    elif roll_val <= 55:  # 45% chance
        slow_print("Against the odds, you make it home safely.")
        return True
    else:
        slow_print("Wounds take their toll during extraction. You succumb.")
        player.alive = False
        return False

def summary(player: Player):
    """
    Prints a summary of the player's campaign, inventory, and survival status.
    """
    divider()
    slow_print("=== CAMPAIGN SUMMARY ===")
    slow_print(f"Name: {player.name}")
    slow_print(f"Role: {player.role}")
    slow_print(f"Missions completed: {player.missions_completed}")
    slow_print(f"Final HP: {max(0, player.hp)}")
    slow_print(f"Inventory remaining: {player.inventory}")
    if player.alive:
        slow_print("Status: SURVIVED")
    else:
        slow_print("Status: DECEASED")
    divider()
    slow_print("Thank you for playing Afghanistan War — Text Adventure!")

# ============================================================
# 🎮 MAIN GAME LOOP
# ============================================================

def main():
    """
    Main function that runs the game loop:
        1. Introduction
        2. Role selection
        3. Mission sequence
        4. Final extraction
        5. Summary

    Handles user inputs and exceptions gracefully.
    """
    random.seed()  # Initialize RNG
    intro()

    # Get player name
    name = input("Enter your name, soldier: ").strip() or "Player"

    # Select role
    role = pick_role()
    player = Player(name, role)
    role_intro(player)

    # Determine number of missions
    slow_print("How many missions would you like to attempt? (1-10 recommended, default 3)")
    while True:
        m_input = input("> ").strip()
        if m_input == "":
            missions = 3
            break
        if m_input.isdigit() and 1 <= int(m_input) <= 10:
            missions = int(m_input)
            break
        slow_print("Please enter a number between 1 and 10.")

    slow_print(f"Starting {missions} missions. Good luck, {player.name}.")
    
    # Run mission sequence
    survived_missions = play_mission_sequence(player, missions=missions)

    if not survived_missions or not player.alive:
        slow_print("GAME OVER — you did not survive the campaign.")
        summary(player)
        return

    # Final extraction outcome
    survived_home = final_resolution(player)
    if survived_home:
        slow_print("CONGRATULATIONS — you made it home alive!")
    else:
        slow_print("You did not survive the extraction. Your service is remembered.")

    # Print campaign summary
    summary(player)

# ============================================================
# ✅ ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        slow_print("\nGame interrupted. Goodbye, soldier.")


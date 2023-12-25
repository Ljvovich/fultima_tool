crisis_ability = """this monster has no crisis ability
        """
loot = "there is no loot specified for "
int_error = """
    Check following values. 
    They must me integers, no non-numeric chars allowed:
        Creature Lvl
        Initiative
        Max HP
        Max MP
        Inventory Points
        Defense and Magic Defense Values
    
"""
affinity_collision = """
    Current affinities doesn't match with origin.
    Copy current affinities to the new creature?
"""
superiority_hit = """Gain superiority, when:
    • Whenever you deal damage and at least target is Vulnerable           
    • Whenever you suffer damage, if you are Immune or Absorb
    • Whenever you roll a critical success
    • Whenever you roll a fumble, the opposing team gains 1 Superiority Point. 
"""
help_label = """
    File→New Creature to create a new creature   
            The Set Defense block allows you to set a defense (or magic defense) formula           
                    Choose a stat it will derive from and value (i.e., dexterity 5 for DEX+5 or insight -3 for INS-3)                   
                    Use const for constant values (like in DEF:11 for Bronze Plate)
                    We recommend putting values granted by shields in the bonus field instead of value.
            
            The Affinities icons are clickable
            
            Avoid the same names within one block (like Attacks, Spells, and Named Abilities)
            
            Inventory & Loot: Zenit and Inventory points must be integers.           
                    Each click on add for Zenit in Inv. Points will increase current value
                    Inventory is a list, so each "Add" just add new Instance of inputted item
            
            Click Create to save .json file with your creature
            
    
    Show/hide→Loot allows you to show or hide the Loot tab.
    
    Show/hide→Help to show this tab (opening a new creature will automatically hide Help)
    
    Show/hide→Superiority to spawn a new superiority track (there could be multiple superiority tracks)

    File→Open Creature to open a creature created with New Creature, or use  File→From Fultimator to load JSON from fultimator (https://fabula-ultima-helper.web.app)   
            Multi-select are allowed.   
            If you are using Fultimator, please note that rare equipment will be duplicated in both loot and abilities if there is any effect on them. Otherwise, they are just loot.


    Creature Tab 
   
            The gear icon near the stat block allows you to set additional offsets to current stats (like buffs or debuffs)    
                    You can check current offsets by hovering at corresponding stat 
                    (*Note that the current offset includes those that are caused by status effects)  
                    Use a new offset with the opposite value to cancel the previous
   
            HP: You cannot use HEAL to set a value over the maximum, but you can set it manually by clicking on the current value   
                    The same works for MP (use to recover MP)
   
            Gear at the Resist & Defense block allows you to change the defense formula or set a bonus/penalty.
   
            The shield icon sets guard state (see Rulebook, p. 70)
                    If you increase the resistance granted from guard to Immunity or Absorption, it will not reset after canceling the guard state
   
            To add a picture, put a file named [creature name placeholder].png in the 'images' folder in the root folder of the application.
                    Image could be resized (keeping ratio) to 200 x 200 if any of the dimensions are bigger than 200   
                    The file name is case-sensitive           
   
            Loot button: move all zenits, Inventory points and the content of the loot window to the loot tab
                    loot window is modifiable  manually
   
            Clone opens a new tab with a copy of the current creature. Copping affinities is optional, but all other buffs and current HP and MP are copied. 
                    If loot content was modified manually (not by a Loot Button) loot of a copied creature would match the original one.   
                    Otherwise, loot window would be empty
   
            Remove Button closes current Creature
"""

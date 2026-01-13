# ==============================================================================
# IMAGINARY SUBMOD - Events & Labels
# ==============================================================================
# This file contains Ren'Py labels and events for the submod:
#   - Pack selection topic (Misc menu)
#   - Category selection flow
#   - Pack selection flow
#   - Restore all defaults
#   - Confirmation dialogs
# ==============================================================================


# ==============================================================================
# PACK SELECTION TOPIC
# Registered in the Misc menu for the player to access
# ==============================================================================

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="eb_skin_select",
            category=["misc"],
            prompt="Customize visuals (Box)",
            pool=True,
            unlocked=True
        ),
        restartBlacklist=True,
        markSeen=True
    )


# ==============================================================================
# SECTION SELECTION
# Main menu showing sections (Monika, Accessories, Room, Games)
# ==============================================================================

label eb_skin_select:
    show monika at t11
    
    python:
        import store.eb_skins as skins
        
        # Define sections and their categories
        _sections = {
            "monika": {
                "name": "Monika",
                "categories": ["eyes", "eyebrows", "mouth", "nose", "blush", "arms", "torso"]
            },
            "accessories": {
                "name": "Accessories",
                "categories": ["mug", "hotchoc_mug", "promisering", "quetzal", "quetzal_mid", "roses"]
            },
            "room": {
                "name": "Room",
                "categories": ["calendar"]
            },
            "games": {
                "name": "Games",
                "categories": ["nou", "chess", "pong"]
            }
        }
        
        # Build section menu items
        # Shows * if any category in section has a custom pack
        _menu_items = []
        for _section_key in ["monika", "accessories", "room", "games"]:
            _section = _sections[_section_key]
            _has_custom = False
            for _cat in _section["categories"]:
                if skins.get_selected_pack(_cat):
                    _has_custom = True
                    break
            
            if _has_custom:
                _item_text = "{} *".format(_section["name"])
            else:
                _item_text = _section["name"]
            _menu_items.append((_item_text, _section_key))
        
        # Add utility options
        _menu_items.append(("Restore All Defaults", "restore"))
        _menu_items.append(("Nevermind", "cancel"))
    
    call screen eb_select_menu("Welcome!", _menu_items)
    
    if _return == "cancel" or _return is None:
        return
    
    elif _return == "restore":
        jump eb_restore_all
    
    else:
        # Selected a section, show categories in that section
        $ _eb_sel_section = _return
        $ _eb_section_data = _sections[_eb_sel_section]
        jump eb_section_categories


# ==============================================================================
# CATEGORY SELECTION (within a section)
# Shows categories for the selected section
# ==============================================================================

label eb_section_categories:
    python:
        import store.eb_skins as skins
        
        _title = _eb_section_data["name"]
        _categories = _eb_section_data["categories"]
        
        # Build menu items for this section
        _menu_items = []
        for _cat in _categories:
            _cat_info = skins.CATEGORIES.get(_cat, {})
            _display = _cat_info.get("display_name", _cat.title())
            _current = skins.get_selected_pack(_cat)
            if _current:
                _item_text = "{} *".format(_display)
            else:
                _item_text = _display
            _menu_items.append((_item_text, _cat))
        
        _menu_items.append(("<<< Go Back", "GO_BACK"))
    
    call screen eb_select_menu(_title, _menu_items)
    
    if _return == "GO_BACK" or _return is None:
        jump eb_skin_select
    
    else:
        $ _eb_sel_category = _return
        jump eb_skin_select_category


# ==============================================================================
# RESTORE ALL DEFAULTS
# Resets all packs to MAS originals (recommended before uninstall)
# ==============================================================================

label eb_restore_all:
    "Restore all visual elements to MAS defaults?"
    "This is recommended before uninstalling."
    
    menu:
        "Yes, restore everything":
            python:
                import store.eb_skins as skins
                
                _restored_count = 0
                _categories = [
                    "eyes", "eyebrows", "mouth", "nose", "blush",
                    "arms", "torso",
                    "mug", "hotchoc_mug", "calendar", "promisering", 
                    "nou", "chess", "pong", "quetzal", "quetzal_mid", "roses"
                ]
                
                for _cat in _categories:
                    if eb_restore_mas_defaults(_cat):
                        _restored_count += 1
                    skins.set_selected_pack(_cat, None)
            
            "Restored [_restored_count] categories to defaults."
            "Restart required to apply changes."
            
            menu:
                "Restart now":
                    return "quit"
                
                "Later":
                    pass
        
        "Cancel":
            pass
    
    jump eb_skin_select


# ==============================================================================
# PACK SELECTION (for specific category)
# Shows available packs for the selected category
# ==============================================================================

label eb_skin_select_category:
    python:
        import store.eb_skins as skins
        
        _packs = ["default"] + skins.detect_packs(_eb_sel_category)
        _current = skins.get_selected_pack(_eb_sel_category)
        
        # Get display name for title
        _cat_info = skins.CATEGORIES.get(_eb_sel_category, {})
        _cat_display = _cat_info.get("display_name", _eb_sel_category.title())
        _title = "Select {} Pack".format(_cat_display)
        
        # Build menu items
        # Shows [X] next to currently selected pack
        _menu_items = []
        for _p in _packs:
            if _p == "default":
                _label = "Default (MAS Original)"
            else:
                _label = _p
            
            _is_selected = (_p == _current) or (_p == "default" and _current is None)
            if _is_selected:
                _label = "[[X] " + _label  # [[ escapes to literal [
            
            _menu_items.append((_label, _p, _is_selected))
        
        _menu_items.append(("<<< Go Back", "GO_BACK", False))
    
    call screen eb_select_menu(_title, _menu_items)
    
    $ _selected = _return
    
    if _selected == "GO_BACK":
        jump eb_section_categories
    
    if _selected:
        jump eb_skin_apply
    else:
        jump eb_section_categories


# ==============================================================================
# APPLY PACK
# Validates and applies the selected pack
# ==============================================================================

label eb_skin_apply:
    python:
        import store.eb_skins as skins
        
        # "default" in menu = None in persistent
        if _selected == "default":
            _new_pack = None
        else:
            _new_pack = _selected
        
        _old_pack = skins.get_selected_pack(_eb_sel_category)
        _changed = (_new_pack != _old_pack)
    
    if not _changed:
        "No changes made."
        jump eb_skin_select
    
    # Check if pack has all required files
    if _new_pack:
        python:
            _missing = skins.get_missing_files(_eb_sel_category, _new_pack)
            _missing_count = len(_missing)
        
        if _missing_count > 0:
            "This pack is incomplete. Missing [_missing_count] files."
            menu:
                "Complete it with default files":
                    python:
                        _copied = skins.copy_missing_files(_eb_sel_category, _new_pack)
                    "Copied [_copied] files."
                
                "Cancel":
                    jump eb_section_categories
    
    # Save the selection
    $ skins.set_selected_pack(_eb_sel_category, _new_pack)
    
    # Restore original files if selecting default (for file-copy categories)
    if not _new_pack and _eb_sel_category in ["eyes", "eyebrows", "mouth", "nose", "blush", "arms", "torso", "mug", "hotchoc_mug", "calendar", "promisering", "nou", "chess", "pong", "quetzal", "quetzal_mid", "roses"]:
        python:
            _restored = eb_restore_mas_defaults(_eb_sel_category)
        if _restored:
            "Restored original files from backup."
        else:
            "No backup found, but setting has been reset."
    
    if _new_pack:
        "Selected '[_new_pack]'."
    else:
        "Restored to default style."
    
    "Restart required to apply changes."
    
    menu:
        "Restart now":
            return "quit"
        
        "Later":
            pass
    
    jump eb_section_categories


# ==============================================================================
# RESTART CONFIRMATION DIALOG
# Used when applying skins via eb_apply_skins()
# ==============================================================================

label eb_restart_dialog:
    show monika at t11
    m 1eua "Do you want to apply the skin changes?"
    m 1eub "I need to restart for the changes to take effect."
    
    menu:
        "Yes, restart now":
            m 1hua "Alright! See you in a moment~"
            return "quit"
        
        "No, I'll do it later":
            m 1eka "Okay, just remember that you need to restart to see the changes."
            return


# ==============================================================================
# INCOMPLETE PACKS DIALOG
# Shown when selected packs are missing files
# ==============================================================================

label eb_incomplete_packs_dialog:
    show monika at t11
    m 1ekc "Hmm, it looks like some packs are incomplete..."
    
    python:
        incomplete_list = store._eb_incomplete_packs
        for cat, pack, count in incomplete_list:
            renpy.say(m, "The pack '[pack]' in '[cat]' is missing [count] files.")
    
    m 1eua "Do you want me to complete the missing files using the defaults?"
    m 3eub "That way the pack will work correctly."
    
    menu:
        "Yes, complete the packs":
            python:
                import store.eb_skins as skins
                total_copied = 0
                for cat, pack, count in incomplete_list:
                    copied = skins.copy_missing_files(cat, pack)
                    total_copied += copied
            
            m 1hua "Done! Copied [total_copied] files."
            m 1eub "Now I need to restart to apply the changes."
            
            menu:
                "Restart now":
                    m 1hua "See you in a moment~!"
                    return "quit"
                
                "I'll do it later":
                    m 1eka "Okay, restart when you're ready."
                    return
        
        "No, cancel":
            m 1eka "Understood. The incomplete packs won't work until they have all the files."
            return

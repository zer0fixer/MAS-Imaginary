# ==============================================================================
# EMERALD BOX - Functions
# ==============================================================================
# This file contains all Python functions for the submod, organized in sections:
#   1. PARTICLE SYSTEM - Core particle creation, animation, and management
#   2. PARTICLE SETTINGS - UI control functions for settings screen
#   3. PARTICLE LAYER - Display layer management (front/behind Monika)
#   4. GAME HOOKS - Disable particles during games
#   5. SKIN PACK STORE - Category definitions and pack detection
#   6. SKIN PACK FILE OPERATIONS - Copy/backup files to MAS locations
#   7. SKIN PACK SELECTION - Pack selection with validation
# ==============================================================================


# ==============================================================================
# SECTION 1: PARTICLE SYSTEM
# Core particle creation, animation, and lifecycle management
# ==============================================================================

init python:
    import random
    import math
    
    # Global particle system variables
    eb_sprite_manager = None
    eb_particle_list = []
    
    # Pre-calculated angles for floating mode (8 directions, optimized)
    PRESET_ANGLES = [(math.cos(i * 0.785398), math.sin(i * 0.785398)) for i in range(8)]
    
    
    def eb_get_particle_path(particle_id):
        """
        Build the correct path to a particle image.
        
        IN:
            particle_id - Particle image ID (0, 1, etc.)
            
        RETURNS:
            string - Normalized path to the image
        """
        particle_type = persistent._eb_particle_type
        base_path = store.eb_folders.PARTICLE_TYPE_PATHS.get(
            particle_type, 
            store.eb_folders.EB_PARTICLES_DUST
        )
        return base_path + "/%s.png" % particle_id
    
    
    def eb_create_particles(amount=None):
        """
        Create the particle system with specified amount.
        
        IN:
            amount - Number of particles to create (Default: uses persistent setting)
        """
        global eb_sprite_manager, eb_particle_list
        
        if amount is None:
            amount = persistent._eb_particle_count
        
        # Destroy existing particles first
        eb_destroy_particles()
        
        eb_sprite_manager = SpriteManager(update=eb_update_particles)
        eb_particle_list = []
        
        for i in range(amount):
            eb_create_single_particle()
    
    
    def eb_create_single_particle():
        """
        Create a single particle with random properties.
        Supports both floating (random movement) and falling (top to bottom) modes.
        """
        global eb_sprite_manager, eb_particle_list
        
        if eb_sprite_manager is None:
            return
        
        # Get movement mode for current particle type
        particle_type = persistent._eb_particle_type
        movement_mode = store.eb.PARTICLE_MOVEMENT_MODES.get(particle_type, "floating")
        
        # Random properties
        rand_alpha = random.uniform(0.0, 0.5)
        rand_zoom = random.uniform(0.3, 0.7)
        rand_img = renpy.random.choice((0, 1))
        
        # Create displayable with Transform
        img_path = eb_get_particle_path(rand_img)
        t = Transform(img_path, alpha=rand_alpha, zoom=rand_zoom)
        
        # Create sprite in SpriteManager
        particle = eb_sprite_manager.create(t)
        particle.img_path = img_path  # Cache path to avoid recalculating each frame
        particle.alpha = rand_alpha
        particle.zoom = rand_zoom
        particle.movement_mode = movement_mode
        
        if movement_mode == "falling":
            # Falling mode: spawn distributed across screen initially
            particle.speed = random.uniform(0.5, 1.5)  # Faster for falling
            particle.x = renpy.random.randint(0, config.screen_width)
            # On first creation, distribute across entire screen height
            # On respawn, will start above screen (handled in reposition)
            particle.y = renpy.random.randint(0, config.screen_height)
            
            # Wind effect (horizontal drift)
            particle.wind = random.uniform(-0.3, 0.3)
            
            # Falling direction (mostly down with some horizontal)
            particle.dx = particle.wind
            particle.dy = particle.speed
            
            # For falling, start visible
            particle.alpha = random.uniform(0.3, 0.6)
            particle.fadein = False
            particle.fadeout = False
        else:
            # Floating mode: random movement (optimized with preset angles)
            particle.speed = random.uniform(0.03, 0.15)
            
            # Random starting position (avoiding edges)
            particle.x = renpy.random.randint(100, config.screen_width - 100)
            particle.y = renpy.random.randint(100, config.screen_height - 100)
            
            # Direction using pre-calculated angles (8 directions)
            angle_idx = renpy.random.randint(0, 7)
            particle.dx = PRESET_ANGLES[angle_idx][0] * particle.speed
            particle.dy = PRESET_ANGLES[angle_idx][1] * particle.speed
            
            # Fade in/out control
            if rand_alpha < 0.25:
                particle.fadein = True
                particle.fadeout = False
            else:
                particle.fadein = False
                particle.fadeout = True
        
        eb_particle_list.append(particle)
    
    
    def eb_update_particles(st):
        """
        Update function called every frame.
        Animates particles with movement and fade effects.
        Handles both floating and falling modes.
        
        IN:
            st - Animation time (provided by Ren'Py)
            
        RETURNS:
            float - Time until next update (0 = immediate)
        """
        global eb_particle_list
        
        for particle in eb_particle_list:
            # Move particle using pre-computed direction
            particle.x += particle.dx
            particle.y += particle.dy
            
            # Check movement mode
            if getattr(particle, 'movement_mode', 'floating') == "falling":
                # Falling mode: respawn at top when going off screen
                if particle.y > config.screen_height + 50:
                    eb_reposition_particle(particle)
                # Also respawn if too far left/right
                elif particle.x < -50 or particle.x > config.screen_width + 50:
                    eb_reposition_particle(particle)
            else:
                # Floating mode: fade in/out control
                if particle.fadein:
                    particle.alpha += 0.003  # Optimized: was 0.0006
                    if particle.alpha >= 0.5:
                        particle.fadein = False
                        particle.fadeout = True
                        
                elif particle.fadeout:
                    particle.alpha -= 0.003  # Optimized: was 0.0006
                    if particle.alpha <= 0.0:
                        # Reposition particle when fully faded
                        eb_reposition_particle(particle)
            
            # Update displayable with new alpha (using cached path)
            t = Transform(particle.img_path, alpha=max(0.0, particle.alpha), zoom=particle.zoom)
            particle.set_child(t)
        
        return 0.016  # ~60 FPS fixed interval (optimized from 0)
    
    
    def eb_reposition_particle(particle):
        """
        Reposition a particle after it completes its cycle.
        Handles both floating (fade out) and falling (off screen) modes.
        
        IN:
            particle - The particle to reposition
        """
        movement_mode = getattr(particle, 'movement_mode', 'floating')
        
        if movement_mode == "falling":
            # Falling mode: respawn at top
            particle.x = renpy.random.randint(0, config.screen_width)
            particle.y = renpy.random.randint(-100, -20)  # Above screen
            
            # New speed and wind
            particle.speed = random.uniform(0.5, 1.5)
            particle.wind = random.uniform(-0.3, 0.3)
            particle.dx = particle.wind
            particle.dy = particle.speed
            
            # Reset zoom for variation
            particle.zoom = random.uniform(0.3, 0.7)
            particle.alpha = random.uniform(0.3, 0.6)
        else:
            # Floating mode: original behavior (optimized with preset angles)
            # New random position
            particle.x = renpy.random.randint(100, config.screen_width - 100)
            particle.y = renpy.random.randint(100, config.screen_height - 100)
            
            # New speed and direction using pre-calculated angles (8 directions)
            particle.speed = random.uniform(0.03, 0.15)
            angle_idx = renpy.random.randint(0, 7)
            particle.dx = PRESET_ANGLES[angle_idx][0] * particle.speed
            particle.dy = PRESET_ANGLES[angle_idx][1] * particle.speed
            
            # Reset fade
            particle.alpha = 0.0
            particle.fadein = True
            particle.fadeout = False
    
    
    def eb_destroy_particles():
        """
        Destroy the particle system and free memory.
        """
        global eb_sprite_manager, eb_particle_list
        
        if eb_sprite_manager is not None:
            del eb_sprite_manager
            eb_sprite_manager = None
        
        eb_particle_list = []
    
    
    def eb_reload_particles():
        """
        Reload particles with current settings.
        Called when user changes type or amount.
        """
        # Hide current particles first
        eb_hide_particles()
        
        # Create new particle system
        eb_create_particles()
        
        # Show the new particles
        if persistent._eb_particles_enabled:
            eb_show_particles()


# ==============================================================================
# SECTION 2: PARTICLE SETTINGS
# UI control functions for the settings screen
# ==============================================================================

init python:
    
    def eb_on_particles_toggle():
        """Handle particles toggle. Called after ToggleField changes the value."""
        global eb_sprite_manager, eb_particle_list
        
        if persistent._eb_particles_enabled:
            # Now enabled - create and show particles
            eb_create_particles()
            eb_show_particles()
        else:
            # Now disabled - make all particles invisible first
            if eb_particle_list:
                for particle in eb_particle_list:
                    try:
                        # Set alpha to 0 to make invisible
                        t = Transform(particle.img_path, alpha=0.0, zoom=particle.zoom)
                        particle.set_child(t)
                    except:
                        pass
            
            # Force redraw with invisible particles
            if eb_sprite_manager is not None:
                try:
                    eb_sprite_manager.redraw(0)
                except:
                    pass
                del eb_sprite_manager
                eb_sprite_manager = None
            
            eb_particle_list = []
            
            # Hide from layer
            try:
                renpy.hide("eb_particles_obj", layer="master")
            except:
                pass
            
        renpy.restart_interaction()
    
    def eb_next_type():
        """Change to the next particle type."""
        types = store.eb.PARTICLE_TYPES
        current_idx = types.index(persistent._eb_particle_type)
        next_idx = (current_idx + 1) % len(types)
        persistent._eb_particle_type = types[next_idx]
        eb_reload_particles()
    
    def eb_prev_type():
        """Change to the previous particle type."""
        types = store.eb.PARTICLE_TYPES
        current_idx = types.index(persistent._eb_particle_type)
        prev_idx = (current_idx - 1) % len(types)
        persistent._eb_particle_type = types[prev_idx]
        eb_reload_particles()
    
    def eb_increase_count():
        """Increase particle count by 5."""
        if persistent._eb_particle_count < 30:
            persistent._eb_particle_count += 5
            eb_reload_particles()
    
    def eb_decrease_count():
        """Decrease particle count by 5."""
        if persistent._eb_particle_count > 5:
            persistent._eb_particle_count -= 5
            eb_reload_particles()
    
    def eb_next_layer():
        """Move to next layer (back → middle → front)."""
        layer_order = ["back", "middle", "front"]
        current = persistent._eb_particle_layer
        try:
            current_idx = layer_order.index(current)
            next_idx = (current_idx + 1) % len(layer_order)
        except ValueError:
            next_idx = 1  # Default to middle
        
        persistent._eb_particle_layer = layer_order[next_idx]
        eb_refresh_particle_layer()
        renpy.restart_interaction()
    
    def eb_prev_layer():
        """Move to previous layer (front → middle → back)."""
        layer_order = ["back", "middle", "front"]
        current = persistent._eb_particle_layer
        try:
            current_idx = layer_order.index(current)
            prev_idx = (current_idx - 1) % len(layer_order)
        except ValueError:
            prev_idx = 1  # Default to middle
        
        persistent._eb_particle_layer = layer_order[prev_idx]
        eb_refresh_particle_layer()
        renpy.restart_interaction()


# ==============================================================================
# SECTION 3: PARTICLE LAYER MANAGEMENT
# Controls which layer particles display on (front/behind Monika)
# ==============================================================================

init python:
    
    def eb_show_particles(with_transition=False):
        """
        Show particles on the correct layer based on settings.
        
        IN:
            with_transition - If True, use dissolve fade-in effect
        """
        if not eb_sprite_manager:
            return
        
        # Determine zorder based on layer setting
        if persistent._eb_particle_layer == "back":
            zorder = 1
            behind = None
        elif persistent._eb_particle_layer == "middle":
            zorder = 7
            behind = ["monika"]
        else:  # front
            zorder = 15
            behind = None
        
        # Show on master layer
        if behind:
            renpy.show(
                "eb_particles_obj", 
                what=eb_sprite_manager, 
                layer="master",
                zorder=zorder,
                behind=behind
            )
        else:
            renpy.show(
                "eb_particles_obj", 
                what=eb_sprite_manager, 
                layer="master",
                zorder=zorder
            )
        
        # Apply dissolve only if requested (first show)
        if with_transition:
            renpy.with_statement(Dissolve(1.0))
    
    def eb_hide_particles():
        """Hide particles from all possible layers."""
        # Hide screen version (Back/Front)
        for layer in ["master", "front", "transient", "screens", "overlay"]:
            try:
                renpy.hide_screen("eb_particles_screen", layer=layer)
            except:
                pass
        
        # Hide object version (Middle)
        try:
            renpy.hide("eb_particles_obj", layer="master")
        except:
            pass

    def eb_refresh_particle_layer():
        """Refresh particles on correct layer after layer change."""
        eb_hide_particles()
        if persistent._eb_particles_enabled:
            eb_show_particles()


# ==============================================================================
# SECTION 4: GAME HOOKS
# Temporarily disable particles during minigames to avoid interference
# ==============================================================================

init python:
    import store.mas_submod_utils as msu
    
    def _eb_disable_for_game():
        """Temporarily disable particles for games."""
        persistent._eb_temp_disabled = True
    
    def _eb_enable_after_game():
        """Re-enable particles after games."""
        persistent._eb_temp_disabled = False
    
    @msu.functionplugin("game_chess")
    def _eb_hook_chess():
        _eb_disable_for_game()
    
    @msu.functionplugin("game_pong")
    def _eb_hook_pong():
        _eb_disable_for_game()
    
    @msu.functionplugin("mas_piano_start")
    def _eb_hook_piano():
        _eb_disable_for_game()
    
    @msu.functionplugin("mas_hangman")
    def _eb_hook_hangman():
        _eb_disable_for_game()
    
    @msu.functionplugin("mas_nou")
    def _eb_hook_nou():
        _eb_disable_for_game()
    
    @msu.functionplugin("ch30_loop")
    def _eb_hook_loop():
        _eb_enable_after_game()


# ==============================================================================
# SECTION 5: SKIN PACK STORE
# Category definitions and pack detection
# ==============================================================================

init -990 python in eb_skins:
    import os
    import shutil
    import store
    
    # Base path for custom packs
    CUSTOM_PATH = "mod_assets/monika/custom/"
    
    # Pack category definitions
    # Each category has: path, persistent_key, display_name, mas_path
    CATEGORIES = {
        # Monika face parts (all share /f/ folder, use backup_key to group)
        "eyes": {
            "path": CUSTOM_PATH + "eyes/",
            "persistent_key": "_eb_eyes_pack",
            "display_name": "Eyes",
            "mas_path": "mod_assets/monika/f/",
            "file_prefixes": ["face-eyes-", "face-leaning-def-eyes-"],
            "backup_key": "face"  # Shared backup for all face parts
        },
        "eyebrows": {
            "path": CUSTOM_PATH + "eyebrows/",
            "persistent_key": "_eb_eyebrows_pack",
            "display_name": "Eyebrows",
            "mas_path": "mod_assets/monika/f/",
            "file_prefixes": ["face-eyebrows-", "face-leaning-def-eyebrows-"],
            "backup_key": "face"
        },
        "mouth": {
            "path": CUSTOM_PATH + "mouth/",
            "persistent_key": "_eb_mouth_pack",
            "display_name": "Mouth",
            "mas_path": "mod_assets/monika/f/",
            "file_prefixes": ["face-mouth-", "face-leaning-def-mouth-"],
            "backup_key": "face"
        },
        "nose": {
            "path": CUSTOM_PATH + "nose/",
            "persistent_key": "_eb_nose_pack",
            "display_name": "Nose",
            "mas_path": "mod_assets/monika/f/",
            "file_prefixes": ["face-nose-", "face-leaning-def-nose-"],
            "backup_key": "face"
        },
        "blush": {
            "path": CUSTOM_PATH + "blush/",
            "persistent_key": "_eb_blush_pack",
            "display_name": "Blush",
            "mas_path": "mod_assets/monika/f/",
            "file_prefixes": ["face-blush-", "face-leaning-def-blush-"],
            "backup_key": "face"
        },
        
        # Monika body parts (share /b/ folder)
        "arms": {
            "path": CUSTOM_PATH + "arms/",
            "persistent_key": "_eb_arms_pack",
            "display_name": "Arms & Hands",
            "mas_path": "mod_assets/monika/b/",
            "file_prefix": "arms-",
            "backup_key": "body"  # Shared backup for body parts
        },
        "torso": {
            "path": CUSTOM_PATH + "torso/",
            "persistent_key": "_eb_torso_pack",
            "display_name": "Torso & Head",
            "mas_path": "mod_assets/monika/b/",
            "file_prefix": "body-",
            "backup_key": "body"
        },
        
        # Accessories
        "mug": {
            "path": CUSTOM_PATH + "mug/",
            "persistent_key": "_eb_mug_pack",
            "display_name": "Coffee Mug",
            "mas_path": "mod_assets/monika/a/mug/"
        },
        "hotchoc_mug": {
            "path": CUSTOM_PATH + "hotchoc_mug/",
            "persistent_key": "_eb_hotchoc_pack",
            "display_name": "Hot Chocolate Mug",
            "mas_path": "mod_assets/monika/a/hotchoc_mug/"
        },
        "promisering": {
            "path": CUSTOM_PATH + "promisering/",
            "persistent_key": "_eb_promisering_pack",
            "display_name": "Promise Ring",
            "mas_path": "mod_assets/monika/a/promisering/"
        },
        "quetzal": {
            "path": CUSTOM_PATH + "quetzal/",
            "persistent_key": "_eb_quetzal_pack",
            "display_name": "Quetzal Plushie",
            "mas_path": "mod_assets/monika/a/quetzalplushie/"
        },
        "quetzal_mid": {
            "path": CUSTOM_PATH + "quetzal_mid/",
            "persistent_key": "_eb_quetzal_mid_pack",
            "display_name": "Quetzal Mid",
            "mas_path": "mod_assets/monika/a/quetzalplushie_mid/"
        },
        "roses": {
            "path": CUSTOM_PATH + "roses/",
            "persistent_key": "_eb_roses_pack",
            "display_name": "Roses",
            "mas_path": "mod_assets/monika/a/roses/"
        },
        
        # Room elements
        "calendar": {
            "path": CUSTOM_PATH + "calendar/",
            "persistent_key": "_eb_calendar_pack",
            "display_name": "Calendar",
            "mas_path": "mod_assets/calendar/"
        },
        
        # Games
        "nou": {
            "path": CUSTOM_PATH + "nou/",
            "persistent_key": "_eb_nou_pack",
            "display_name": "NOU Cards",
            "mas_path": "mod_assets/games/nou/"
        },
        "chess": {
            "path": CUSTOM_PATH + "chess/",
            "persistent_key": "_eb_chess_pack",
            "display_name": "Chess",
            "mas_path": "mod_assets/games/chess/"
        },
        "pong": {
            "path": CUSTOM_PATH + "pong/",
            "persistent_key": "_eb_pong_pack",
            "display_name": "Pong",
            "mas_path": "mod_assets/games/pong/"
        }
    }
    
    
    def get_file_prefixes(cat_info):
        """
        Get list of file prefixes for a category.
        Supports both 'file_prefix' (string) and 'file_prefixes' (list).
        """
        if "file_prefixes" in cat_info:
            return cat_info["file_prefixes"]
        elif "file_prefix" in cat_info:
            return [cat_info["file_prefix"]]
        return []
    
    
    def matches_prefix(filename, prefixes):
        """Check if filename starts with any of the prefixes."""
        for prefix in prefixes:
            if filename.startswith(prefix):
                return True
        return False
    
    
    def get_full_path(relative_path):
        """Convert relative game path to full filesystem path."""
        return os.path.join(renpy.config.basedir, "game", relative_path)
    
    
    def detect_packs(category):
        """
        Detect available packs for a category.
        
        IN:
            category - Category key (face, mug, etc.)
            
        RETURNS:
            list - Pack names (folder names)
        """
        if category not in CATEGORIES:
            return []
        
        cat_path = get_full_path(CATEGORIES[category]["path"])
        packs = []
        
        if os.path.exists(cat_path):
            for folder in os.listdir(cat_path):
                # Skip backup folders
                if folder.startswith("_backup"):
                    continue
                
                folder_path = os.path.join(cat_path, folder)
                if os.path.isdir(folder_path):
                    packs.append(folder)
        
        return sorted(packs)
    
    
    def get_pack_files(category, pack_name):
        """
        Get list of files in a pack.
        Respects file_prefix filter for categories like arms/torso.
        
        IN:
            category - Category key
            pack_name - Pack folder name
            
        RETURNS:
            list - Filenames in the pack
        """
        if category not in CATEGORIES or not pack_name:
            return []
        
        cat_info = CATEGORIES[category]
        pack_path = get_full_path(cat_info["path"] + pack_name + "/")
        prefixes = get_file_prefixes(cat_info)
        files = []
        
        if os.path.exists(pack_path):
            # For categories with file prefixes, only list root files matching prefixes
            if prefixes:
                for f in os.listdir(pack_path):
                    full_path = os.path.join(pack_path, f)
                    if os.path.isfile(full_path) and matches_prefix(f, prefixes):
                        files.append(f)
            else:
                # For other categories, walk recursively
                for root, dirs, filenames in os.walk(pack_path):
                    for f in filenames:
                        rel_path = os.path.relpath(os.path.join(root, f), pack_path)
                        files.append(rel_path.replace("\\", "/"))
        
        return files
    
    
    def get_default_files(category):
        """
        Get list of files in the default MAS path for a category.
        Respects file prefixes for categories like face parts, arms/torso.
        
        IN:
            category - Category key
            
        RETURNS:
            list - Filenames in default MAS path
        """
        if category not in CATEGORIES:
            return []
        
        cat_info = CATEGORIES[category]
        default_path = get_full_path(cat_info["mas_path"])
        prefixes = get_file_prefixes(cat_info)
        files = []
        
        if os.path.exists(default_path):
            # For categories with file prefixes, only list root files matching prefixes
            if prefixes:
                for f in os.listdir(default_path):
                    full_path = os.path.join(default_path, f)
                    if os.path.isfile(full_path) and matches_prefix(f, prefixes):
                        files.append(f)
            else:
                # For other categories, walk recursively
                for root, dirs, filenames in os.walk(default_path):
                    for f in filenames:
                        rel_path = os.path.relpath(os.path.join(root, f), default_path)
                        files.append(rel_path.replace("\\", "/"))
        
        return files
    
    
    def get_missing_files(category, pack_name):
        """
        Get files that exist in default but not in pack.
        
        IN:
            category - Category key
            pack_name - Pack folder name
            
        RETURNS:
            list - Missing filenames
        """
        pack_files = set(get_pack_files(category, pack_name))
        default_files = set(get_default_files(category))
        
        return list(default_files - pack_files)
    
    
    def copy_missing_files(category, pack_name):
        """
        Copy missing files from default MAS location to pack.
        
        IN:
            category - Category key
            pack_name - Pack folder name
            
        RETURNS:
            int - Number of files copied
        """
        missing = get_missing_files(category, pack_name)
        if not missing:
            return 0
        
        default_path = get_full_path(CATEGORIES[category]["mas_path"])
        pack_path = get_full_path(CATEGORIES[category]["path"] + pack_name + "/")
        
        copied = 0
        for f in missing:
            src = os.path.join(default_path, f)
            dst = os.path.join(pack_path, f)
            
            # Create directory if needed
            dst_dir = os.path.dirname(dst)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            
            try:
                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                store.mas_utils.mas_log.error(
                    "Emerald Box: Failed to copy {}: {}".format(f, e)
                )
        
        return copied
    
    
    def get_selected_pack(category):
        """Get currently selected pack for a category (None = default)."""
        if category not in CATEGORIES:
            return None
        key = CATEGORIES[category]["persistent_key"]
        return getattr(store.persistent, key, None)
    
    
    def set_selected_pack(category, pack_name):
        """Set selected pack for a category (None = default)."""
        if category not in CATEGORIES:
            return
        key = CATEGORIES[category]["persistent_key"]
        setattr(store.persistent, key, pack_name)


# ==============================================================================
# SECTION 6: SKIN PACK FILE OPERATIONS
# Copy pack files to MAS locations and handle backups
# ==============================================================================

init 100 python:
    import os
    import shutil
    import store.eb_skins as skins
    
    def eb_apply_file_packs():
        """
        Apply all selected packs by copying files to MAS locations.
        Called on startup. Only copies if pack was modified since last apply.
        """
        categories_to_copy = [
            "eyes", "eyebrows", "mouth", "nose", "blush",
            "arms", "torso",
            "mug", "hotchoc_mug", "calendar", "promisering", 
            "nou", "chess", "pong", "quetzal", "quetzal_mid", "roses"
        ]
        
        # Initialize applied packs cache if not exists
        if not hasattr(store, '_eb_applied_packs_cache'):
            store._eb_applied_packs_cache = {}
        
        for cat in categories_to_copy:
            pack = skins.get_selected_pack(cat)
            if pack:
                # Check if already applied with same pack (skip if no changes)
                cache_key = cat + ":" + pack
                pack_path = skins.get_full_path(skins.CATEGORIES[cat]["path"] + pack + "/")
                
                # Get pack modification time
                try:
                    pack_mtime = os.path.getmtime(pack_path)
                except:
                    pack_mtime = 0
                
                # Skip if already applied and pack not modified
                if cache_key in store._eb_applied_packs_cache:
                    if store._eb_applied_packs_cache[cache_key] >= pack_mtime:
                        continue  # Already applied, skip
                
                # Apply pack and cache timestamp
                _eb_copy_pack_to_mas(cat, pack)
                store._eb_applied_packs_cache[cache_key] = pack_mtime
    
    
    def _eb_copy_pack_to_mas(category, pack_name):
        """
        Copy pack files to MAS location, creating backup of originals.
        Handles automatic file renaming for older MAS versions.
        
        IN:
            category - Category key
            pack_name - Pack folder name
        """
        if category not in skins.CATEGORIES:
            return
        
        cat_info = skins.CATEGORIES[category]
        pack_path = skins.get_full_path(cat_info["path"] + pack_name + "/")
        mas_path = skins.get_full_path(cat_info["mas_path"])
        
        # Use backup_key if available (for shared backups like face parts, body parts)
        # All backups go to _backup_mas/ folder to keep custom/ clean
        backup_key = cat_info.get("backup_key", category)
        backup_path = skins.get_full_path(skins.CUSTOM_PATH + "_backup_mas/" + backup_key + "/")
        
        if not os.path.exists(pack_path):
            return
        
        # Detect MAS version for file naming compatibility
        mas_version = renpy.config.version
        needs_old_format = _eb_version_compare(mas_version, "0.12.16") < 0
        
        # Categories that need old format conversion (accessories)
        # Maps category key to the old format prefix name
        OLD_FORMAT_CATEGORIES = {
            "mug": "mug",
            "hotchoc_mug": "hotchoc_mug",
            "promisering": "promisering",
            "quetzal": "quetzalplushie",  # Note: folder name differs from prefix
            "quetzal_mid": "quetzalplushie_mid",
            "roses": "roses"
        }
        
        # Create backup of original MAS files (only once per backup_key)
        # For shared backups (face, body), only copy root files to avoid subfolders from outfits
        if not os.path.exists(backup_path) and os.path.exists(mas_path):
            try:
                if cat_info.get("backup_key"):
                    # Shared backup: copy only root files, not subfolders
                    os.makedirs(backup_path)
                    for f in os.listdir(mas_path):
                        src = os.path.join(mas_path, f)
                        if os.path.isfile(src):
                            dst = os.path.join(backup_path, f)
                            shutil.copy2(src, dst)
                else:
                    # Regular backup: copy entire folder tree
                    shutil.copytree(mas_path, backup_path)
            except Exception:
                pass  # Backup exists or permission issue
        
        # For old format, files go directly to /a/ not in subfolders
        if needs_old_format and category in OLD_FORMAT_CATEGORIES:
            old_acs_name = OLD_FORMAT_CATEGORIES[category]
            # Old format: files go to mod_assets/monika/a/ directly
            old_mas_path = skins.get_full_path("mod_assets/monika/a/")
            
            for root, dirs, files in os.walk(pack_path):
                for f in files:
                    if f == "preview.png":
                        continue
                    
                    src = os.path.join(root, f)
                    # Convert filename to old format
                    new_filename = _eb_convert_to_old_format(f, old_acs_name)
                    dst = os.path.join(old_mas_path, new_filename)
                    
                    try:
                        shutil.copy2(src, dst)
                    except Exception:
                        pass
        else:
            # New format: copy to subfolder as-is
            # Check if category has file prefixes filter (for face parts, arms/torso)
            prefixes = skins.get_file_prefixes(cat_info)
            
            for root, dirs, files in os.walk(pack_path):
                for f in files:
                    if f == "preview.png":
                        continue
                    
                    # Skip files that don't match the prefixes (if specified)
                    if prefixes and not skins.matches_prefix(f, prefixes):
                        continue
                    
                    src = os.path.join(root, f)
                    rel_path = os.path.relpath(src, pack_path)
                    dst = os.path.join(mas_path, rel_path)
                    
                    # Create directory if needed
                    dst_dir = os.path.dirname(dst)
                    if not os.path.exists(dst_dir):
                        try:
                            os.makedirs(dst_dir)
                        except:
                            pass
                    
                    try:
                        shutil.copy2(src, dst)
                    except Exception:
                        pass
    
    
    def _eb_version_compare(v1, v2):
        """
        Compare two version strings.
        
        RETURNS:
            -1 if v1 < v2, 0 if equal, 1 if v1 > v2
        """
        try:
            parts1 = [int(x) for x in v1.split("-")[0].split(".")]
            parts2 = [int(x) for x in v2.split("-")[0].split(".")]
            
            for i in range(max(len(parts1), len(parts2))):
                p1 = parts1[i] if i < len(parts1) else 0
                p2 = parts2[i] if i < len(parts2) else 0
                if p1 < p2:
                    return -1
                elif p1 > p2:
                    return 1
            return 0
        except:
            return 0
    
    
    def _eb_convert_to_old_format(filename, acs_name):
        """
        Convert new filename format to old format for MAS < 0.12.16.
        
        New format: "0.png" or "2-10.png" (in subfolders)
        Old format: "acs-mug-0.png" or "acs-promisering-2-10.png" (loose files)
        
        IN:
            filename - Original filename
            acs_name - Accessory name for prefix
            
        RETURNS:
            Converted filename with acs- prefix
        """
        # Remove any path components, keep only filename
        filename = os.path.basename(filename)
        
        # Add acs- prefix
        return "acs-{}-{}".format(acs_name, filename)
    
    
    def eb_restore_mas_defaults(category):
        """
        Restore original MAS files from backup.
        
        IN:
            category - Category to restore
            
        RETURNS:
            bool - True if restored, False if no backup found
        """
        if category not in skins.CATEGORIES:
            return False
        
        cat_info = skins.CATEGORIES[category]
        mas_path = skins.get_full_path(cat_info["mas_path"])
        
        # Use backup_key if available (for shared backups)
        backup_key = cat_info.get("backup_key", category)
        backup_path = skins.get_full_path(skins.CUSTOM_PATH + "_backup_mas/" + backup_key + "/")
        prefixes = skins.get_file_prefixes(cat_info)
        
        if not os.path.exists(backup_path):
            return False
        
        # Copy backup back to MAS location (only files matching prefixes if specified)
        for root, dirs, files in os.walk(backup_path):
            for f in files:
                # Skip files that don't match the prefixes (if specified)
                if prefixes and not skins.matches_prefix(f, prefixes):
                    continue
                    
                src = os.path.join(root, f)
                rel_path = os.path.relpath(src, backup_path)
                dst = os.path.join(mas_path, rel_path)
                
                try:
                    shutil.copy2(src, dst)
                except:
                    pass
        
        return True
    
    # Apply packs on startup
    eb_apply_file_packs()


# ==============================================================================
# SECTION 7: SKIN PACK SELECTION
# Pack selection with validation (used by events.rpy)
# ==============================================================================

init python:
    
    def eb_select_pack(category, pack_name):
        """
        Select a pack with validation.
        
        IN:
            category - Category key
            pack_name - Pack name or None for default
            
        RETURNS:
            tuple - (success, message)
        """
        import store.eb_skins as skins
        
        if pack_name is None:
            skins.set_selected_pack(category, None)
            return (True, "Reset to default.")
        
        # Check if pack exists
        available = skins.detect_packs(category)
        if pack_name not in available:
            return (False, "Pack '{}' not found.".format(pack_name))
        
        # Check for missing files
        missing = skins.get_missing_files(category, pack_name)
        if missing:
            store._eb_pending_pack = (category, pack_name)
            store._eb_missing_count = len(missing)
            return (False, "MISSING_FILES")
        
        skins.set_selected_pack(category, pack_name)
        return (True, "Pack '{}' selected. Restart to apply.".format(pack_name))
    
    
    def eb_complete_pack(category, pack_name):
        """
        Complete a pack by copying missing files from default.
        
        IN:
            category - Category key
            pack_name - Pack name
            
        RETURNS:
            int - Number of files copied
        """
        import store.eb_skins as skins
        return skins.copy_missing_files(category, pack_name)
    
    
    def eb_get_pack_list(category):
        """Get list of available packs including 'default'."""
        import store.eb_skins as skins
        return ["default"] + skins.detect_packs(category)
    
    
    def eb_next_pack(category):
        """Navigate to next pack for a category."""
        import store.eb_skins as skins
        
        packs = eb_get_pack_list(category)
        current = skins.get_selected_pack(category)
        
        if current is None:
            current_idx = 0
        elif current in packs:
            current_idx = packs.index(current)
        else:
            current_idx = 0
        
        next_idx = (current_idx + 1) % len(packs)
        new_pack = packs[next_idx] if next_idx > 0 else None
        skins.set_selected_pack(category, new_pack)
    
    
    def eb_prev_pack(category):
        """Navigate to previous pack for a category."""
        import store.eb_skins as skins
        
        packs = eb_get_pack_list(category)
        current = skins.get_selected_pack(category)
        
        if current is None:
            current_idx = 0
        elif current in packs:
            current_idx = packs.index(current)
        else:
            current_idx = 0
        
        prev_idx = (current_idx - 1) % len(packs)
        new_pack = packs[prev_idx] if prev_idx > 0 else None
        skins.set_selected_pack(category, new_pack)
    
    # Note: eb_apply_skins removed - packs now only apply their included files

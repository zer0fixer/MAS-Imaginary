# ==============================================================================
# EMERALD BOX - Main Configuration
# ==============================================================================
# This file contains:
#   - Submod registration
#   - Persistent variable defaults
#   - Settings screen (shown in submod settings)
#   - Selection menu screen (used for pack selection)
#   - Particle display screen
#   - Path definitions for cross-platform compatibility
#   - Particle type definitions
# ==============================================================================

# ==============================================================================
# SUBMOD REGISTRATION
# ==============================================================================

init -990 python:
    store.mas_submod_utils.Submod(
        author="ZeroFixer",
        name="Emerald Box",
        description="Customize Monika's appearance with visual packs (eyes, mouth, nose, arms, torso, accessories, games) and ambient particles (snow, sakura, leaves, and more).",
        version="1.0.0",
        settings_pane="eb_settings_pane"
    )

# ==============================================================================
# SUBMOD UPDATER (Optional - requires Submod Updater Plugin)
# ==============================================================================

init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Emerald Box",
            user_name="zer0fixer",
            repository_name="MAS-EmeraldBox",
            redirected_files=(
                "README.txt"
            )
        )

# ==============================================================================
# PERSISTENT DEFAULTS
# These values are saved between sessions. None = use default MAS assets.
# ==============================================================================

init -999:
    # --- Skin Pack Selections ---
    # Monika face parts
    default persistent._eb_eyes_pack = None
    default persistent._eb_eyebrows_pack = None
    default persistent._eb_mouth_pack = None
    default persistent._eb_nose_pack = None
    default persistent._eb_blush_pack = None
    
    # Monika body parts
    default persistent._eb_arms_pack = None
    default persistent._eb_torso_pack = None
    
    # Accessories
    default persistent._eb_mug_pack = None
    default persistent._eb_hotchoc_pack = None
    default persistent._eb_promisering_pack = None
    default persistent._eb_quetzal_pack = None
    default persistent._eb_quetzal_mid_pack = None
    default persistent._eb_roses_pack = None
    
    # Room elements
    default persistent._eb_calendar_pack = None
    
    # Games
    default persistent._eb_nou_pack = None
    default persistent._eb_chess_pack = None
    default persistent._eb_pong_pack = None
    
    # --- Particle Settings ---
    default persistent._eb_particle_type = "hearts"
    default persistent._eb_particles_enabled = True
    default persistent._eb_particle_count = 15
    default persistent._eb_temp_disabled = False
    default persistent._eb_particle_layer = "middle"  # "back", "middle", "front"

# ==============================================================================
# SETTINGS SCREEN
# Displayed in MAS Submod Settings menu
# ==============================================================================

screen eb_settings_pane():
    vbox:
        box_wrap False
        xfill True
        xmaximum 800
        spacing 5
        
        # Enable/Disable particles toggle
        hbox:
            style_prefix "check"
            box_wrap False
            
            textbutton _("{b}Enable Particles{/b}"):
                selected persistent._eb_particles_enabled
                action [
                    ToggleField(persistent, "_eb_particles_enabled"),
                    Function(eb_on_particles_toggle)
                ]
        
        # Particle type selector
        hbox:
            box_wrap False
            spacing 5
            text _("Particle Type:")
            
            textbutton _("<"):
                style "navigation_button"
                action Function(eb_prev_type)
                sensitive persistent._eb_particles_enabled
            
            python:
                _particle_display_name = store.eb.PARTICLE_TYPE_NAMES.get(
                    persistent._eb_particle_type, 
                    persistent._eb_particle_type
                )
            text "[_particle_display_name]":
                min_width 80
                text_align 0.5
            
            textbutton _(">"):
                style "navigation_button"
                action Function(eb_next_type)
                sensitive persistent._eb_particles_enabled
        
        # Particle count control
        hbox:
            box_wrap False
            spacing 5
            text _("Amount:")
            
            textbutton _("-"):
                style "navigation_button"
                action Function(eb_decrease_count)
                sensitive persistent._eb_particles_enabled and persistent._eb_particle_count > 5
            
            text "[persistent._eb_particle_count]":
                min_width 30
                text_align 0.5
            
            textbutton _("+"):
                style "navigation_button"
                action Function(eb_increase_count)
                sensitive persistent._eb_particles_enabled and persistent._eb_particle_count < 30
        
        # Layer control (front/behind Monika)
        hbox:
            box_wrap False
            spacing 5
            text _("Layer:")
            
            textbutton _("<"):
                style "navigation_button"
                action Function(eb_prev_layer)
                sensitive persistent._eb_particles_enabled
            
            python:
                _layer_names = {"back": "Far Back", "middle": "Behind", "front": "In Front"}
                _layer_display = _layer_names.get(persistent._eb_particle_layer, "Behind")
            text "[_layer_display]":
                min_width 80
                text_align 0.5
            
            textbutton _(">"):
                style "navigation_button"
                action Function(eb_next_layer)
                sensitive persistent._eb_particles_enabled
        
        null height 15
        
        # Hint for skin packs location
        text _("{size=14}Give it your special touch: Talk -> Misc -> 'Customize visuals'{/size}"):
            color "#888888"

# ==============================================================================
# GENERIC SELECTION MENU SCREEN
# Reusable screen for category and pack selection
# ==============================================================================

screen eb_select_menu(title, options):
    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        background None
        padding (20, 20)
        
        vbox:
            spacing 15
            xalign 0.5
            
            # Title bar - adapts to MAS light/dark theme
            frame:
                if store.mas_globals.dark_mode:
                    background Frame("mod_assets/buttons/generic/idle_bg_d.png", Borders(5, 5, 5, 5), tile=False)
                else:
                    background Frame("mod_assets/buttons/generic/idle_bg.png", Borders(5, 5, 5, 5), tile=False)
                padding (15, 10)
                xalign 0.45
                text title size 28 color store.mas_globals.button_text_idle_color outlines []
            
            null height 10
            
            # Scrollable option list
            viewport:
                xsize 420
                ysize 420
                mousewheel True
                scrollbars "vertical"
                xalign 0.5
                
                vbox:
                    spacing 8
                    for item in options:
                        $ _text = item[0]
                        $ _value = item[1]
                        textbutton _text:
                            style "hkb_button"
                            xsize 400
                            action Return(_value)

# ==============================================================================
# PARTICLE DISPLAY SCREEN
# Shows particles when enabled (works in any room)
# ==============================================================================

screen eb_particles_screen():
    if (
        persistent._eb_particles_enabled
        and not persistent._eb_temp_disabled
        and eb_sprite_manager is not None
    ):
        add eb_sprite_manager

# ==============================================================================
# PATH DEFINITIONS
# Cross-platform compatible path detection for submod assets
# ==============================================================================

init -995 python in eb_folders:
    import os
    import store
    
    def _normalize_path(path):
        """
        Normalize path separators for cross-platform compatibility.
        Converts backslashes to forward slashes.
        """
        return path.replace("\\", "/")

    def _join_path(*args):
        """Join path components and normalize the result."""
        return _normalize_path(os.path.join(*args))

    def find_submods_folder(base_path="."):
        """
        Find the Submods folder with case-insensitive search.
        Required for Linux/macOS where paths are case-sensitive.
        """
        try:
            for folder in os.listdir(base_path):
                if folder.lower() == "submods" and os.path.isdir(os.path.join(base_path, folder)):
                    return folder
        except Exception:
            pass
        return "Submods"

    def find_eb_folder(submods_path):
        """
        Find the Emerald Box folder with case-insensitive search.
        Required for Linux/macOS where paths are case-sensitive.
        """
        try:
            for folder in os.listdir(submods_path):
                if folder.lower() == "emeraldbox" and os.path.isdir(os.path.join(submods_path, folder)):
                    return folder
        except Exception:
            pass
        return "EmeraldBox"

    # Detect actual folder names (handles case variations)
    EB_submods_folder = find_submods_folder()
    _submods_full_path = _normalize_path(os.path.join(renpy.config.basedir, "game", EB_submods_folder))
    EB_eb_folder = find_eb_folder(_submods_full_path)

    # Build path constants
    EB_ROOT = _join_path(EB_submods_folder, EB_eb_folder)
    EB_PARTICLES = _join_path(EB_ROOT, "particles")
    
    # Particle type paths
    EB_PARTICLES_DUST = _join_path(EB_PARTICLES, "dust")
    EB_PARTICLES_HEARTS = _join_path(EB_PARTICLES, "hearts")
    EB_PARTICLES_STARS = _join_path(EB_PARTICLES, "stars")
    EB_PARTICLES_SAKURA = _join_path(EB_PARTICLES, "sakura")
    EB_PARTICLES_SNOW = _join_path(EB_PARTICLES, "snow")
    EB_PARTICLES_LEAVES = _join_path(EB_PARTICLES, "leaves")
    EB_PARTICLES_CONFETTI = _join_path(EB_PARTICLES, "confetti")
    EB_PARTICLES_BUBBLES = _join_path(EB_PARTICLES, "bubbles")
    
    # Mapping of particle types to their asset paths
    PARTICLE_TYPE_PATHS = {
        "dust": EB_PARTICLES_DUST,
        "hearts": EB_PARTICLES_HEARTS,
        "stars": EB_PARTICLES_STARS,
        "sakura": EB_PARTICLES_SAKURA,
        "snow": EB_PARTICLES_SNOW,
        "leaves": EB_PARTICLES_LEAVES,
        "confetti": EB_PARTICLES_CONFETTI,
        "bubbles": EB_PARTICLES_BUBBLES
    }

# ==============================================================================
# PARTICLE TYPE DEFINITIONS
# Available particle types and their display names
# ==============================================================================

init -990 python in eb:
    import store
    
    # List of available particle types
    PARTICLE_TYPES = ["dust", "hearts", "stars", "sakura", "snow", "leaves", "confetti", "bubbles"]
    
    # Display names shown in settings UI
    PARTICLE_TYPE_NAMES = {
        "dust": "Dust",
        "hearts": "Hearts",
        "stars": "Stars",
        "sakura": "Sakura",
        "snow": "Snow",
        "leaves": "Leaves",
        "confetti": "Confetti",
        "bubbles": "Bubbles"
    }
    
    # Movement modes for each particle type
    # "floating" = random movement (default)
    # "falling" = falls from top to bottom
    PARTICLE_MOVEMENT_MODES = {
        "dust": "floating",
        "hearts": "floating",
        "stars": "floating",
        "sakura": "falling",  # Sakura petals fall
        "snow": "falling",
        "leaves": "falling",
        "confetti": "falling",
        "bubbles": "floating"  # Bubbles float around
    }

# Note: Face pack override removed - face parts are now copied directly to MAS folders

# ==============================================================================
# MAS HOOKS
# Particle initialization and display hooks
# ==============================================================================

init 999 python:
    import store.mas_submod_utils as msu
    
    # Track if particles were temporarily disabled (for transition after games)
    _eb_was_disabled = False
    
    @msu.functionplugin("ch30_preloop", priority=10)
    def _eb_init_particles():
        """Initialize particles before the main loop starts."""
        if persistent._eb_particles_enabled and eb_sprite_manager is None:
            eb_create_particles()
    
    # Use ch30_visual_skip which runs AFTER spaceroom is called
    @msu.functionplugin("ch30_visual_skip", priority=10)
    def _eb_auto_show_particles():
        """Automatically show particles after scene is set up."""
        global _eb_was_disabled
        
        if persistent._eb_particles_enabled and not persistent._eb_temp_disabled:
            # Use dissolve only when returning from a game (was disabled)
            use_transition = _eb_was_disabled
            eb_show_particles(with_transition=use_transition)
            _eb_was_disabled = False
        
        elif persistent._eb_temp_disabled:
            # Track that we were disabled (for next show)
            _eb_was_disabled = True

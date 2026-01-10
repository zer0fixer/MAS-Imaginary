# Imaginary Submod

A comprehensive customization submod for Monika After Story.

## ✨ Features

### 🎨 Visual Packs
Customize Monika's appearance and accessories with sprite packs:

- **Monika**
  - Face (expressions)
  - Arms & Hands (skin tones, accessories)
  - Torso & Head (body base)

- **Accessories**
  - Coffee Mug
  - Hot Chocolate Mug
  - Promise Ring
  - Quetzal Plushie
  - Roses

- **Room**
  - Calendar

- **Games**
  - NOU cards
  - Chess pieces
  - Pong paddles

### ✨ Ambient Particles
Add floating particles behind Monika for atmosphere:
- Multiple particle types (Sakura, Dust, etc.)
- Adjustable particle count (5-30)
- Layer control (Behind background, Behind Monika, In front)
- Auto-hides during games
- Only visible in Monika's current room (submods that move her, like dates or tours, will hide particles)

### 🔧 Easy Configuration
- Settings panel in Submods menu
- Per-category pack selection via Talk → Misc → "Customize visuals"
- Automatic backup and restore of original files

---

# Sprite Pack Structure Guide

This guide helps sprite makers understand where to place their custom packs.

## Folder Structure

> **Note:** The `custom/` folder is located inside the MAS game folder, NOT inside the submod folder.
> Full path: `DDLC/game/mod_assets/monika/custom/`

```
monika/
└── custom/
    ├── face/              # Monika's facial expressions
    │   └── [pack_name]/   # Your pack folder
    │       └── *.png      # Expression files
    │
    ├── arms/              # Arms & Hands
    │   └── [pack_name]/
    │       └── arms-*.png # Only files starting with "arms-"
    │
    ├── torso/             # Torso & Head (body base)
    │   └── [pack_name]/
    │       └── body-*.png # Only files starting with "body-"
    │
    ├── mug/               # Coffee Mug accessory
    │   └── [pack_name]/
    │       └── *.png
    │
    ├── hotchoc_mug/       # Hot Chocolate Mug accessory
    │   └── [pack_name]/
    │       └── *.png
    │
    ├── promisering/       # Promise Ring accessory
    │   └── [pack_name]/
    │       └── *.png      # Use NEW format: 2-10.png, 3-10.png, etc.
    │
    ├── quetzal/           # Quetzal Plushie accessory
    │   └── [pack_name]/
    │       └── *.png
    │
    ├── roses/             # Roses accessory
    │   └── [pack_name]/
    │       └── *.png
    │
    ├── calendar/          # Room calendar
    │   └── [pack_name]/
    │       └── *.png
    │
    ├── nou/               # NOU card game sprites
    │   └── [pack_name]/
    │       └── *.png
    │
    ├── chess/             # Chess game sprites
    │   └── [pack_name]/
    │       └── *.png
    │
    └── pong/              # Pong game sprites
        └── [pack_name]/
            └── *.png
```

## How to Create a Pack

1. **Choose a category** from the list above
2. **Create a folder** with your pack name inside that category
3. **Add your PNG files** following the original MAS naming convention
4. **(Optional)** Add a `preview.png` for pack preview (will be ignored when copying)

### Pack Naming Rules

> ⚠️ **Important naming conventions:**
> - Use **lowercase only** (no capital letters)
> - Use **underscores** `_` to separate words (no spaces)
> - **Start with your creator name** to avoid duplicates and theft
> - Format: `creatorname_packname`

**Good examples:**
- `zerofixer_green_ring`
- `artistname_chess_pastel`
- `modder123_pong_christmas`

**Bad examples:**
- `Green Ring` ❌ (spaces and capitals)
- `green-ring` ❌ (hyphens instead of underscores)
- `my_pack` ❌ (missing creator name)

### Example: Creating a "Green Ring" pack for Promise Ring

```
custom/
└── promisering/
    └── zerofixer_green_ring/       # creatorname_packname format
        ├── 2-10.png                # Required files (match MAS originals)
        ├── 3-10.png
        ├── 5-10.png
        └── preview.png             # Optional preview (ignored)
```

## File Naming Conventions

### For Accessories (promisering, mug, etc.)
Use the **NEW format** (MAS 0.12.16+):
- `0.png`, `2-10.png`, `3-10.png`, etc.
- **Do NOT use** the old `acs-[name]-` prefix
- The submod automatically converts for older MAS versions

### For Arms & Torso
- **Arms**: Files MUST start with `arms-` (e.g., `arms-crossed-10.png`)
- **Torso**: Files MUST start with `body-` (e.g., `body-def-0.png`)


## Incomplete Packs - Don't Worry!

> 💡 **You don't need to include ALL files!**
> 
> If your pack is missing some files, the submod will **automatically offer to complete it** with the default MAS files. This means you can create a pack with only the files you want to modify!

For example, if you only want to change the promise ring appearance but not all poses:
- Just include the files you modified
- The submod will detect missing files
- It will offer to fill them with MAS defaults automatically

## Tips for Sprite Makers

1. **Match the original resolution**
2. **Keep transparency** where applicable
3. **Test your pack** before distributing
4. **You can include only the files you want to change** - missing files will be auto-completed

## MAS Version Compatibility

The submod automatically handles file naming differences between:
- **MAS 0.12.16+** (new folder structure)
- **MAS 0.12.15 and below** (old prefix naming)

Sprite makers only need to provide the new format - the submod converts automatically.

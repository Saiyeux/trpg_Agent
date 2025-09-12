"""
TRPG Agent 数据模块

提供可填充的游戏数据框架，包括角色属性、消耗品和地图系统。
支持扩展和自定义内容。
"""

from .character_data import (
    CharacterAttributes, 
    AttributeType, 
    AttributeDefinition,
    CHARACTER_TEMPLATES,
    create_character
)

from .consumables_data import (
    ConsumableRegistry,
    ConsumableItem,
    ConsumableType,
    EffectType,
    ItemEffect,
    PlayerInventory,
    InventorySlot
)

from .map_data import (
    GameMap,
    MapLocation,
    LocationType,
    Direction,
    InteractableObject,
    LocationConnection,
    create_starter_map,
    create_dungeon_map
)

__all__ = [
    # Character system
    'CharacterAttributes',
    'AttributeType', 
    'AttributeDefinition',
    'CHARACTER_TEMPLATES',
    'create_character',
    
    # Consumables system
    'ConsumableRegistry',
    'ConsumableItem',
    'ConsumableType',
    'EffectType', 
    'ItemEffect',
    'PlayerInventory',
    'InventorySlot',
    
    # Map system
    'GameMap',
    'MapLocation',
    'LocationType',
    'Direction',
    'InteractableObject', 
    'LocationConnection',
    'create_starter_map',
    'create_dungeon_map'
]
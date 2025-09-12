"""
地图数据框架

可填充的地图系统，支持位置、连接关系、场景描述和交互对象。
包含地图生成、路径查找和区域管理功能。
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class LocationType(Enum):
    """位置类型"""
    TOWN = "town"           # 城镇
    WILDERNESS = "wilderness"  # 野外
    DUNGEON = "dungeon"     # 地牢
    ROOM = "room"           # 房间
    SHOP = "shop"           # 商店
    TAVERN = "tavern"       # 酒馆
    FOREST = "forest"       # 森林
    MOUNTAIN = "mountain"   # 山脉
    CAVE = "cave"           # 洞穴


class Direction(Enum):
    """方向"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"
    UP = "up"
    DOWN = "down"


@dataclass
class InteractableObject:
    """可交互对象"""
    id: str
    name: str
    description: str
    object_type: str        # door, chest, npc, lever等
    properties: Dict[str, Any] = field(default_factory=dict)
    can_interact: bool = True
    interaction_text: str = ""


@dataclass
class LocationConnection:
    """位置连接"""
    direction: Direction
    target_location: str
    description: str = ""
    requirements: Dict[str, Any] = field(default_factory=dict)  # 通行要求
    is_blocked: bool = False
    block_reason: str = ""


@dataclass
class MapLocation:
    """地图位置"""
    id: str
    name: str
    location_type: LocationType
    short_description: str
    long_description: str
    connections: List[LocationConnection] = field(default_factory=list)
    objects: List[InteractableObject] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)  # NPC ID列表
    items: List[str] = field(default_factory=list)  # 地面物品ID列表
    properties: Dict[str, Any] = field(default_factory=dict)
    visited: bool = False


class GameMap:
    """游戏地图"""
    
    def __init__(self, map_name: str = "默认地图"):
        self.map_name = map_name
        self.locations: Dict[str, MapLocation] = {}
        self._init_default_locations()
    
    def _init_default_locations(self):
        """初始化默认地图 - 可填充扩展"""
        
        # === 新手村 ===
        
        village_center = MapLocation(
            id="village_center",
            name="新手村中心",
            location_type=LocationType.TOWN,
            short_description="宁静的小村庄中心广场",
            long_description="这里是新手村的中心广场，四周环绕着各种建筑。村民们在广场上来回走动，讨论着日常琐事。中央立着一座古老的石雕喷泉，清澈的水流从中涓涓流出。",
            objects=[
                InteractableObject("fountain", "古老喷泉", "一座精美的石雕喷泉，水声潺潺", "fountain", 
                                 {"can_drink": True, "water_quality": "clean"}),
                InteractableObject("notice_board", "公告板", "村庄的任务公告板", "board",
                                 {"has_quests": True, "quest_count": 3})
            ],
            properties={"safe_zone": True, "respawn_point": True}
        )
        
        tavern = MapLocation(
            id="village_tavern",
            name="暖炉酒馆",
            location_type=LocationType.TAVERN,
            short_description="温暖舒适的小酒馆",
            long_description="这间小酒馆内部温暖舒适，壁炉中火焰跳跃，散发着温暖的光芒。几张木桌散布在房间各处，酒保正在柜台后忙碌着。空气中弥漫着麦酒和烤肉的香味。",
            objects=[
                InteractableObject("bar_counter", "酒吧台", "可以购买食物和饮料", "counter", 
                                 {"shop_type": "tavern", "sells_food": True}),
                InteractableObject("fireplace", "壁炉", "温暖的壁炉", "fireplace",
                                 {"provides_warmth": True, "lit": True})
            ],
            npcs=["bartender_joe"],
            properties={"safe_zone": True, "can_rest": True}
        )
        
        weapon_shop = MapLocation(
            id="village_weapon_shop",
            name="铁匠铺",
            location_type=LocationType.SHOP,
            short_description="村庄的武器装备店",
            long_description="这间铁匠铺内陈列着各种武器和防具。墙上挂着剑、盾牌和长矛，角落里的熔炉还在冒着热气。铁匠的锤击声不时传来，显示着这里繁忙的工作状态。",
            objects=[
                InteractableObject("weapon_rack", "武器架", "陈列各种武器", "rack",
                                 {"shop_type": "weapons", "weapon_types": ["sword", "bow", "staff"]}),
                InteractableObject("anvil", "铁砧", "铁匠工作的铁砧", "anvil",
                                 {"can_repair": True, "upgrade_weapons": True})
            ],
            npcs=["blacksmith_tom"],
            properties={"shop": True, "repair_available": True}
        )
        
        # === 野外区域 ===
        
        village_outskirts = MapLocation(
            id="village_outskirts",
            name="村庄郊外",
            location_type=LocationType.WILDERNESS,
            short_description="村庄周围的田野",
            long_description="村庄外围是一片开阔的田野，金黄的麦田在微风中摇摆。远处可以看到茂密的森林和起伏的山丘。小径蜿蜒通向远方，偶尔有鸟儿飞过天空。",
            objects=[
                InteractableObject("old_scarecrow", "老稻草人", "田野中的稻草人", "scarecrow",
                                 {"contains_items": True, "hidden_stash": True})
            ],
            properties={"encounter_rate": 0.1, "safe_level": 1}
        )
        
        dark_forest = MapLocation(
            id="dark_forest",
            name="幽暗森林",
            location_type=LocationType.FOREST,
            short_description="神秘而危险的森林",
            long_description="这片森林显得阴暗而神秘，高大的树木遮蔽了大部分阳光。林间小径若隐若现，各种奇怪的声音不时从深处传来。空气中弥漫着潮湿和腐叶的味道。",
            objects=[
                InteractableObject("ancient_tree", "古老大树", "一棵巨大的古树", "tree",
                                 {"magical": True, "can_climb": True}),
                InteractableObject("mushroom_circle", "蘑菇圈", "神秘的蘑菇圈", "mushrooms",
                                 {"magical_portal": True, "dangerous": True})
            ],
            properties={"encounter_rate": 0.3, "danger_level": 2, "visibility": "low"}
        )
        
        mountain_path = MapLocation(
            id="mountain_path",
            name="山间小径",
            location_type=LocationType.MOUNTAIN,
            short_description="通往山顶的崎岖小径",
            long_description="这条小径沿着山坡蜿蜒向上，两侧是陡峭的岩壁。山风呼啸而过，带来阵阵寒意。远处可以看到山峰被云雾缭绕，显得既雄伟又神秘。",
            objects=[
                InteractableObject("rope_bridge", "绳索桥", "连接两个山崖的绳桥", "bridge",
                                 {"requires_courage": True, "can_break": True})
            ],
            properties={"altitude": "high", "weather": "cold", "visibility": "good"}
        )
        
        # === 地牢 ===
        
        abandoned_cave = MapLocation(
            id="abandoned_cave",
            name="废弃洞穴",
            location_type=LocationType.CAVE,
            short_description="一个阴暗的废弃洞穴",
            long_description="这个洞穴看起来已经废弃了很久，墙壁上长满了苔藓，地面湿滑难行。深处传来滴水声，偶尔有蝙蝠飞过。洞穴深处似乎有什么东西在移动。",
            objects=[
                InteractableObject("treasure_chest", "宝箱", "一个老旧的木制宝箱", "chest",
                                 {"locked": True, "contains_treasure": True, "lock_difficulty": 3}),
                InteractableObject("cave_painting", "洞穴壁画", "古老的壁画", "painting",
                                 {"historical": True, "provides_lore": True})
            ],
            properties={"dark": True, "dangerous": True, "treasure_possible": True}
        )
        
        # 注册所有位置
        locations = [village_center, tavern, weapon_shop, village_outskirts, 
                    dark_forest, mountain_path, abandoned_cave]
        for location in locations:
            self.locations[location.id] = location
        
        # 设置连接关系
        self._setup_default_connections()
    
    def _setup_default_connections(self):
        """设置默认的位置连接关系"""
        
        # 村庄中心的连接
        self.add_connection("village_center", Direction.NORTH, "village_tavern", "通往温暖的酒馆")
        self.add_connection("village_center", Direction.EAST, "village_weapon_shop", "通往铁匠铺")
        self.add_connection("village_center", Direction.SOUTH, "village_outskirts", "通往村庄郊外")
        
        # 酒馆的连接
        self.add_connection("village_tavern", Direction.SOUTH, "village_center", "返回村庄中心")
        
        # 武器店的连接
        self.add_connection("village_weapon_shop", Direction.WEST, "village_center", "返回村庄中心")
        
        # 村庄郊外的连接
        self.add_connection("village_outskirts", Direction.NORTH, "village_center", "返回村庄中心")
        self.add_connection("village_outskirts", Direction.WEST, "dark_forest", "进入幽暗森林")
        self.add_connection("village_outskirts", Direction.EAST, "mountain_path", "踏上山间小径")
        
        # 幽暗森林的连接
        self.add_connection("dark_forest", Direction.EAST, "village_outskirts", "返回村庄郊外")
        self.add_connection("dark_forest", Direction.SOUTH, "abandoned_cave", "发现隐蔽的洞穴入口")
        
        # 山间小径的连接
        self.add_connection("mountain_path", Direction.WEST, "village_outskirts", "下山返回郊外")
        
        # 废弃洞穴的连接
        self.add_connection("abandoned_cave", Direction.NORTH, "dark_forest", "离开洞穴回到森林")
    
    def add_location(self, location: MapLocation):
        """添加位置"""
        self.locations[location.id] = location
    
    def add_connection(self, from_location: str, direction: Direction, 
                      to_location: str, description: str = "", 
                      requirements: Dict[str, Any] = None):
        """添加位置连接"""
        if from_location not in self.locations:
            return False
        
        connection = LocationConnection(
            direction=direction,
            target_location=to_location,
            description=description,
            requirements=requirements or {}
        )
        
        self.locations[from_location].connections.append(connection)
        return True
    
    def get_location(self, location_id: str) -> Optional[MapLocation]:
        """获取位置信息"""
        return self.locations.get(location_id)
    
    def get_connections(self, location_id: str) -> List[LocationConnection]:
        """获取位置的连接"""
        location = self.get_location(location_id)
        return location.connections if location else []
    
    def can_move(self, from_location: str, direction: Direction, 
                player_attributes: Dict[str, Any] = None) -> Tuple[bool, str]:
        """检查是否可以移动到指定方向"""
        location = self.get_location(from_location)
        if not location:
            return False, "当前位置不存在"
        
        for connection in location.connections:
            if connection.direction == direction:
                if connection.is_blocked:
                    return False, connection.block_reason or "道路被阻挡"
                
                # 检查移动要求
                if connection.requirements and player_attributes:
                    for req_key, req_value in connection.requirements.items():
                        if player_attributes.get(req_key, 0) < req_value:
                            return False, f"需要{req_key}达到{req_value}"
                
                return True, connection.description or "可以前往"
        
        return False, "该方向没有通路"
    
    def get_available_directions(self, location_id: str) -> List[Tuple[Direction, str]]:
        """获取当前位置可用的方向"""
        connections = self.get_connections(location_id)
        return [(conn.direction, conn.description) for conn in connections if not conn.is_blocked]
    
    def find_path(self, start: str, end: str) -> List[str]:
        """查找两点间的路径 (简单的BFS实现)"""
        if start == end:
            return [start]
        
        visited = set()
        queue = [(start, [start])]
        
        while queue:
            current, path = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            location = self.get_location(current)
            if not location:
                continue
            
            for connection in location.connections:
                if not connection.is_blocked:
                    target = connection.target_location
                    if target == end:
                        return path + [target]
                    
                    if target not in visited:
                        queue.append((target, path + [target]))
        
        return []  # 无路径
    
    def get_locations_by_type(self, location_type: LocationType) -> List[MapLocation]:
        """按类型获取位置"""
        return [loc for loc in self.locations.values() if loc.location_type == location_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """导出地图数据"""
        return {
            "map_name": self.map_name,
            "total_locations": len(self.locations),
            "locations": {
                loc_id: {
                    "name": loc.name,
                    "type": loc.location_type.value,
                    "description": loc.short_description,
                    "connections": len(loc.connections),
                    "objects": len(loc.objects),
                    "visited": loc.visited
                }
                for loc_id, loc in self.locations.items()
            }
        }


# 预定义地图模板
def create_starter_map() -> GameMap:
    """创建新手地图"""
    return GameMap("新手冒险地图")


def create_dungeon_map() -> GameMap:
    """创建地牢地图 - 示例扩展"""
    dungeon_map = GameMap("地牢探索")
    
    # 可以在这里添加更多地牢特定的位置
    entrance = MapLocation(
        id="dungeon_entrance",
        name="地牢入口",
        location_type=LocationType.DUNGEON,
        short_description="通往地下深处的石阶",
        long_description="古老的石阶向下延伸，消失在黑暗中。墙壁上的火把提供微弱的光亮，空气中弥漫着潮湿和危险的气息。",
        properties={"entrance": True, "light_source": "torches"}
    )
    
    dungeon_map.add_location(entrance)
    return dungeon_map
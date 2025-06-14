import pygame
import os
import random
from font_manager import font_manager

class MapManager:
    def __init__(self):
        self.current_floor = 1  # 初始樓層
        self.tile_size = 32
        
        # 🆕 地板圖片
        self.floor_sprites = {}
        self.load_floor_images()
        
        # 樓梯圖片
        self.stairs_sprites = {}
        self.load_stairs_images()
        
        # 🆕 商店圖片
        self.shop_sprites = {}
        self.load_shop_images()
        
        # 樓層地圖數據
        self.floor_maps = {
            1: self.create_floor_1(),
            2: self.create_floor_2(),
            3: self.create_floor_3()
        }
        
        # 互動區域（商店、NPC等）
        self.interactions = {
            1: [  # 1樓
                {"type": "shop", "id": "A", "name": "7-11", "x": 50, "y": 350, "width": 80, "height": 60},
                {"type": "shop", "id": "B", "name": "Subway", "x": 200, "y": 250, "width": 80, "height": 60},
                {"type": "shop", "id": "C", "name": "茶壜", "x": 350, "y": 300, "width": 80, "height": 60},
                {"type": "npc", "id": "npc1", "name": "驚慌學生", "x": 500, "y": 400, "width": 30, "height": 30},
                {"type": "stairs", "direction": "up", "x": 450, "y": 100, "width": 96, "height": 48, "target_floor": 2}  # 🆕 加大樓梯尺寸
            ],
            2: [  # 2樓
                {"type": "shop", "id": "D", "name": "和食宣", "x": 100, "y": 200, "width": 80, "height": 60},
                {"type": "shop", "id": "E", "name": "素怡沅", "x": 300, "y": 150, "width": 80, "height": 60},
                {"type": "npc", "id": "npc2", "name": "受傷職員", "x": 200, "y": 300, "width": 30, "height": 30},
                {"type": "stairs", "direction": "up", "x": 450, "y": 90, "width": 96, "height": 48, "target_floor": 3},    # 🆕 加大樓梯尺寸
                {"type": "stairs", "direction": "down", "x": 450, "y": 600, "width": 96, "height": 48, "target_floor": 1}  # 🆕 加大樓梯尺寸
            ],
            3: [  # 3樓
                {"type": "shop", "id": "L", "name": "咖啡廳", "x": 150, "y": 250, "width": 80, "height": 60},
                {"type": "npc", "id": "npc3", "name": "神秘研究員", "x": 400, "y": 200, "width": 30, "height": 30},
                {"type": "npc", "id": "npc4", "name": "最後的研究者", "x": 300, "y": 350, "width": 30, "height": 30},
                {"type": "stairs", "direction": "down", "x": 450, "y": 600, "width": 96, "height": 48, "target_floor": 2}  # 🆕 加大樓梯尺寸
            ]
        }
        
        # 戰鬥區域
        self.combat_zones = {
            1: [
                {"name": "走廊1", "x": 150, "y": 150, "width": 100, "height": 80, "enemies": ["zombie_student"]},
                {"name": "角落", "x": 600, "y": 300, "width": 80, "height": 80, "enemies": ["infected_staff"]}
            ],
            2: [
                {"name": "走廊2", "x": 500, "y": 200, "width": 120, "height": 80, "enemies": ["zombie_student", "infected_staff"]},
                {"name": "廚房", "x": 250, "y": 400, "width": 100, "height": 60, "enemies": ["mutant_zombie"]}
            ],
            3: [
                {"name": "實驗室入口", "x": 100, "y": 100, "width": 150, "height": 100, "enemies": ["alien", "mutant_zombie"]},
                {"name": "研究室", "x": 500, "y": 400, "width": 120, "height": 80, "enemies": ["alien"]}
            ]
        }
        
        # 🔧 修復：物品位置分散，避免重疊
        self.items = {
            1: [
                # 分散在1樓不同區域，避免重疊
                {"name": "醫療包", "type": "healing", "value": 30, "x": 120, "y": 180, "description": "專業醫療包，恢復30血量"},
                {"name": "能量飲料", "type": "healing", "value": 15, "x": 380, "y": 450, "description": "補充體力的能量飲料"},
                {"name": "小型藥劑", "type": "healing", "value": 20, "x": 550, "y": 250, "description": "基礎治療藥劑"}
            ],
            2: [
                # 2樓物品位置
                {"name": "鑰匙卡", "type": "key", "x": 150, "y": 380, "description": "進入三樓實驗室的鑰匙卡"},
                {"name": "研究筆記", "type": "clue", "x": 420, "y": 280, "description": "記錄了重要研究資料的筆記"},
                {"name": "急救包", "type": "healing", "value": 40, "x": 80, "y": 450, "description": "大型急救包，恢復40血量"}
            ],
            3: [
                # 3樓最重要的物品
                {"name": "解藥", "type": "special", "x": 250, "y": 180, "description": "拯救世界的神秘解藥！"},
                {"name": "實驗資料", "type": "clue", "x": 480, "y": 350, "description": "關於病毒研究的重要資料"},
                {"name": "超級藥劑", "type": "healing", "value": 60, "x": 350, "y": 480, "description": "最強效的治療藥劑"}
            ]
        }
        
        # 🆕 新增：物品收集狀態追蹤
        self.collected_items = set()  # 已收集的物品ID
    
    def load_floor_images(self):
        """🆕 載入地板圖片"""
        floor_paths = {
            "floor": "assets/images/floor.png",  # 主要檔名
            "floor_alt": "assets/images/神饃.png",  # 備用檔名
            "tile": "assets/images/tile.png"  # 另一個備用選項
        }
        
        print("🏢 載入地板圖片...")
        
        for floor_type, path in floor_paths.items():
            if os.path.exists(path):
                try:
                    # 載入地板圖片
                    image = pygame.image.load(path).convert_alpha()
                    original_size = image.get_size()
                    print(f"   原始地板圖片尺寸: {original_size}")
                    
                    # 🎨 縮放到64x64像素（配合地板磚塊大小）
                    target_size = 64
                    image = pygame.transform.scale(image, (target_size, target_size))
                    self.floor_sprites[floor_type] = image
                    print(f"✅ 成功載入地板圖片: {floor_type} - {path}")
                    print(f"   縮放後尺寸: {target_size}x{target_size}")
                    break  # 找到第一個可用的圖片就停止
                except Exception as e:
                    print(f"❌ 載入地板圖片失敗: {floor_type} - {e}")
        
        # 檢查是否成功載入地板圖片
        self.use_floor_sprites = len(self.floor_sprites) > 0
        
        if not self.use_floor_sprites:
            print("📦 未找到地板圖片，將使用程式繪製地板")
            print("💡 請將地板圖片放在以下任一位置:")
            for path in floor_paths.values():
                print(f"   - {path}")
        else:
            print(f"🎨 成功載入地板圖片！使用圖片渲染地板")
    
    def load_shop_images(self):
        """🆕 載入商店圖片 - 新增茶壜支援"""
        shop_paths = {
            "711": "assets/images/711.png",  # 你的7-11圖片
            "subway": "assets/images/subway.png",  # 可選的Subway圖片
            "coffee": "assets/images/coffee.png",  # 可選的咖啡廳圖片
            "tea": "assets/images/tea.png"  # 🆕 新增茶壜圖片
        }
        
        print("🏪 載入商店圖片...")
        
        for shop_type, path in shop_paths.items():
            if os.path.exists(path):
                try:
                    # 載入商店圖片
                    image = pygame.image.load(path).convert_alpha()
                    original_size = image.get_size()
                    print(f"   原始商店圖片尺寸: {original_size}")
                    
                    # 🎨 根據商店類型設定不同尺寸
                    if shop_type == "711":
                        # 7-11 調小一點：110x90像素
                        target_width = 110
                        target_height = 90
                    elif shop_type == "subway":
                        # Subway 調大一點：100x78像素
                        target_width = 100
                        target_height = 78
                    elif shop_type == "tea":
                        # 🆕 茶壜設定合適尺寸：100x75像素
                        target_width = 100
                        target_height = 75
                    else:
                        # 其他商店維持原尺寸：80x60像素
                        target_width = 80
                        target_height = 60
                    
                    image = pygame.transform.scale(image, (target_width, target_height))
                    self.shop_sprites[shop_type] = image
                    print(f"✅ 成功載入商店圖片: {shop_type} - {path}")
                    print(f"   縮放後尺寸: {target_width}x{target_height}")
                except Exception as e:
                    print(f"❌ 載入商店圖片失敗: {shop_type} - {e}")
        
        # 檢查是否成功載入商店圖片
        self.use_shop_sprites = len(self.shop_sprites) > 0
        
        if not self.use_shop_sprites:
            print("📦 未找到商店圖片，將使用程式繪製商店")
        else:
            print(f"🎨 成功載入 {len(self.shop_sprites)} 個商店圖片")
    
    def load_stairs_images(self):
        """載入樓梯圖片"""
        stairs_paths = {
            "up": "assets/images/stairs_up.png",
            "down": "assets/images/stairs_down.png"
        }
        
        print("🪜 載入樓梯圖片...")
        
        for direction, path in stairs_paths.items():
            if os.path.exists(path):
                try:
                    # 載入你自己的樓梯圖片
                    image = pygame.image.load(path).convert_alpha()
                    original_size = image.get_size()
                    print(f"   原始圖片尺寸: {original_size}")
                    
                    # 🎨 保持原圖比例，縮放到合適大小
                    # 你可以調整這個目標尺寸來改變樓梯大小
                    target_width = 96  # 可以調整這個數值
                    target_height = 72  # 可以調整這個數值
                    
                    # 縮放到目標尺寸
                    image = pygame.transform.scale(image, (target_width, target_height))
                    self.stairs_sprites[direction] = image
                    print(f"✅ 成功載入樓梯圖片: {direction} - {path}")
                    print(f"   縮放後尺寸: {target_width}x{target_height}")
                except Exception as e:
                    print(f"❌ 載入樓梯圖片失敗: {direction} - {e}")
                    self.stairs_sprites[direction] = None
            else:
                print(f"⚠️ 找不到樓梯圖片: {path}")
                print(f"   請確認你的樓梯圖片已放在正確位置")
                self.stairs_sprites[direction] = None
        
        # 如果沒有載入到圖片，設定標記
        self.use_sprites = any(sprite is not None for sprite in self.stairs_sprites.values())
        
        if not self.use_sprites:
            print("📦 未找到樓梯圖片，將使用像素繪製樓梯")
        else:
            print(f"🎨 成功載入 {len([s for s in self.stairs_sprites.values() if s is not None])} 個樓梯圖片")
            print("💡 如果樓梯太小或太大，可以在 load_stairs_images() 方法中調整 target_width 和 target_height")

    def create_floor_1(self):
        """創建1樓地圖"""
        return {
            "name": "第二餐廳 1樓",
            "background_color": (40, 40, 60),
            "walls": [
                # 外牆
                {"x": 0, "y": 0, "width": 1024, "height": 32},      # 上牆
                {"x": 0, "y": 736, "width": 1024, "height": 32},    # 下牆
                {"x": 0, "y": 0, "width": 32, "height": 768},       # 左牆
                {"x": 992, "y": 0, "width": 32, "height": 768},     # 右牆
                
                # 內部隔間
                {"x": 150, "y": 200, "width": 200, "height": 20},   # 商店隔間
                {"x": 400, "y": 150, "width": 20, "height": 200},   # 垂直隔間
            ]
        }

    def create_floor_2(self):
        """創建2樓地圖"""
        return {
            "name": "第二餐廳 2樓",
            "background_color": (60, 40, 40),
            "walls": [
                # 外牆
                {"x": 0, "y": 0, "width": 1024, "height": 32},
                {"x": 0, "y": 736, "width": 1024, "height": 32},
                {"x": 0, "y": 0, "width": 32, "height": 768},
                {"x": 992, "y": 0, "width": 32, "height": 768},
                
                # 內部隔間
                {"x": 200, "y": 100, "width": 150, "height": 20},
                {"x": 250, "y": 300, "width": 20, "height": 150},
            ]
        }

    def create_floor_3(self):
        """創建3樓地圖"""
        return {
            "name": "第二餐廳 3樓",
            "background_color": (40, 60, 40),
            "walls": [
                # 外牆
                {"x": 0, "y": 0, "width": 1024, "height": 32},
                {"x": 0, "y": 736, "width": 1024, "height": 32},
                {"x": 0, "y": 0, "width": 32, "height": 768},
                {"x": 992, "y": 0, "width": 32, "height": 768},
                
                # 實驗室隔間
                {"x": 100, "y": 200, "width": 300, "height": 20},
                {"x": 350, "y": 200, "width": 20, "height": 200},
            ]
        }

    def change_floor(self, new_floor):
        """切換樓層"""
        if new_floor in self.floor_maps:
            old_floor = self.current_floor
            self.current_floor = new_floor
            print(f"🏢 從 {old_floor} 樓切換到 {new_floor} 樓")
            return True
        return False

    def get_current_floor(self):
        """獲取當前樓層"""
        return self.current_floor

    def check_interaction(self, player_x, player_y, floor):
        """檢查玩家位置是否有互動物件"""
        if floor not in self.interactions:
            return None

        for interaction in self.interactions[floor]:
            # 檢查碰撞
            if (interaction["x"] <= player_x <= interaction["x"] + interaction["width"] and
                interaction["y"] <= player_y <= interaction["y"] + interaction["height"]):
                return interaction

        return None

    def check_combat_zone(self, player_x, player_y, floor):
        """檢查是否進入戰鬥區域"""
        if floor not in self.combat_zones:
            return None

        for zone in self.combat_zones[floor]:
            if (zone["x"] <= player_x <= zone["x"] + zone["width"] and
                zone["y"] <= player_y <= zone["y"] + zone["height"]):
                return zone

        return None

    def remove_combat_zone(self, zone, floor):
        """移除戰鬥區域（戰鬥結束後）"""
        if floor in self.combat_zones and zone in self.combat_zones[floor]:
            self.combat_zones[floor].remove(zone)
            print(f"🗑️ 移除戰鬥區域: {zone['name']} (樓層 {floor})")

    def check_item_pickup(self, player_x, player_y, floor):
        """🆕 檢查是否可以拾取物品"""
        if floor not in self.items:
            return None

        pickup_distance = 30  # 拾取距離

        for item in self.items[floor]:
            # 創建物品ID來追蹤是否已收集
            item_id = f"{floor}_{item['name']}_{item['x']}_{item['y']}"

            # 檢查是否已經收集過
            if item_id in self.collected_items:
                continue

            # 計算距離
            distance = ((player_x - item["x"])**2 + (player_y - item["y"])**2)**0.5

            if distance <= pickup_distance:
                return {"item": item, "item_id": item_id}

        return None

    def collect_item(self, item_id):
        """🆕 收集物品"""
        self.collected_items.add(item_id)
        print(f"📦 收集物品: {item_id}")

    def remove_item(self, item):
        """移除已收集的物品（舊方法，保持兼容性）"""
        for floor_items in self.items.values():
            if item in floor_items:
                floor_items.remove(item)
                break

    def update(self):
        """更新地圖狀態"""
        # 這裡可以添加動態元素的更新邏輯
        pass

    def render(self, screen):
        """渲染當前樓層"""
        current_map = self.floor_maps[self.current_floor]

        # 清除背景
        screen.fill(current_map["background_color"])

        # 渲染地板
        self.render_floor(screen)

        # 渲染牆壁
        self.render_walls(screen, current_map["walls"])

        # 渲染互動區域
        self.render_interactions(screen)

        # 渲染戰鬥區域
        self.render_combat_zones(screen)

        # 渲染物品
        self.render_items(screen)

        # 渲染樓層資訊
        self.render_floor_info(screen)

    def render_floor(self, screen):
        """🆕 渲染地板 - 支援圖片和程式繪製"""
        if self.use_floor_sprites and self.floor_sprites:
            self.render_floor_with_sprites(screen)
        else:
            self.render_floor_with_code(screen)

    def render_floor_with_sprites(self, screen):
        """🆕 使用圖片渲染地板"""
        # 獲取第一個可用的地板圖片
        floor_sprite = None
        for sprite in self.floor_sprites.values():
            if sprite:
                floor_sprite = sprite
                break

        if not floor_sprite:
            # 如果沒有圖片，回退到程式繪製
            self.render_floor_with_code(screen)
            return

        # 使用圖片鋪滿地板
        sprite_size = 64  # 圖片大小

        # 計算需要多少個圖片來填滿螢幕
        cols = (1024 // sprite_size) + 1
        rows = (768 // sprite_size) + 1

        for col in range(cols):
            for row in range(rows):
                x = col * sprite_size
                y = row * sprite_size

                # 確保不超出邊界
                if x < 1024 and y < 768:
                    screen.blit(floor_sprite, (x, y))

        # 移除這行煩人的除錯輸出
        # print(f"🎨 使用圖片渲染地板: {cols}x{rows} 磚塊")

    def render_floor_with_code(self, screen):
        """🆕 使用程式繪製地板（備用方法）"""
        # 簡單的地板磚塊效果
        tile_color = (80, 80, 80)
        for x in range(32, 992, 64):
            for y in range(32, 736, 64):
                if (x // 64 + y // 64) % 2 == 0:
                    pygame.draw.rect(screen, tile_color, (x, y, 64, 64))
                    pygame.draw.rect(screen, (60, 60, 60), (x, y, 64, 64), 1)

    def render_walls(self, screen, walls):
        """渲染牆壁"""
        wall_color = (100, 100, 100)
        for wall in walls:
            pygame.draw.rect(screen, wall_color,
                           (wall["x"], wall["y"], wall["width"], wall["height"]))
            # 牆壁邊框
            pygame.draw.rect(screen, (120, 120, 120),
                           (wall["x"], wall["y"], wall["width"], wall["height"]), 2)

    def render_interactions(self, screen):
        """渲染互動區域"""
        if self.current_floor not in self.interactions:
            return

        for interaction in self.interactions[self.current_floor]:
            if interaction["type"] == "shop":
                self.render_shop(screen, interaction)
            elif interaction["type"] == "npc":
                self.render_npc(screen, interaction)
            elif interaction["type"] == "stairs":
                self.render_stairs(screen, interaction)

    def render_shop(self, screen, shop):
        """渲染商店 - 支援圖片和程式繪製"""
        # 🎨 優先使用圖片渲染
        if self.use_shop_sprites and self.render_shop_with_sprite(screen, shop):
            # 圖片渲染成功，添加商店名稱
            self.render_shop_name(screen, shop)
        else:
            # 備用：程式繪製
            self.render_shop_with_code(screen, shop)
    
    def render_shop_with_sprite(self, screen, shop):
        """🆕 使用圖片渲染商店 - 新增茶壜支援"""
        shop_id = shop["id"]
        shop_name = shop["name"]
        
        # 根據商店名稱或ID選擇對應圖片
        sprite = None
        draw_x = shop["x"]
        draw_y = shop["y"]
        
        if shop_id == "A" and "711" in self.shop_sprites:  # 7-11
            sprite = self.shop_sprites["711"]
            # 7-11 圖片調整位置和大小
            sprite_width = 135
            sprite_height = 101
            # 計算位置：置中但往右移動30像素（15+15）
            x_offset = (shop["width"] - sprite_width) // 2 + 30  # 往右移30像素
            y_offset = (shop["height"] - sprite_height) // 2
            draw_x = shop["x"] + x_offset
            draw_y = shop["y"] + y_offset
        elif shop_name == "Subway" and "subway" in self.shop_sprites:
            sprite = self.shop_sprites["subway"]
        elif shop_name == "咖啡廳" and "coffee" in self.shop_sprites:
            sprite = self.shop_sprites["coffee"]
        elif shop_name == "茶壜" and "tea" in self.shop_sprites:
            # 🆕 茶壜圖片渲染
            sprite = self.shop_sprites["tea"]
            # 茶壜圖片位置微調（可根據需要調整）
            x_offset = (shop["width"] - 100) // 2  # 100是茶壜圖片寬度
            y_offset = (shop["height"] - 75) // 2  # 75是茶壜圖片高度
            draw_x = shop["x"] + x_offset
            draw_y = shop["y"] + y_offset
        
        if sprite:
            # 繪製商店圖片
            screen.blit(sprite, (draw_x, draw_y))
            return True
        
        return False
    
    def render_shop_with_code(self, screen, shop):
        """🆕 程式繪製商店（備用方法）"""
        # 商店背景
        shop_color = (100, 150, 200)
        pygame.draw.rect(screen, shop_color,
                        (shop["x"], shop["y"], shop["width"], shop["height"]))
        pygame.draw.rect(screen, (150, 200, 255),
                        (shop["x"], shop["y"], shop["width"], shop["height"]), 2)

        # 商店名稱
        self.render_shop_name(screen, shop)
    
    def render_shop_name(self, screen, shop):
        """🆕 渲染商店名稱"""
        # 其他商店維持原位置
        text_y = shop["y"] + shop["height"]//2 + 60
        
        name_surface = font_manager.render_text(shop["name"], 18, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(shop["x"] + shop["width"]//2, text_y))
        
        # 名稱背景（讓文字更清楚）
        bg_rect = name_rect.copy()
        bg_rect.inflate(8, 4)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)
        
        screen.blit(name_surface, name_rect)

    def render_npc(self, screen, npc):
        """渲染NPC"""
        # NPC圓形
        npc_color = (255, 200, 100)
        center_x = npc["x"] + npc["width"] // 2
        center_y = npc["y"] + npc["height"] // 2

        pygame.draw.circle(screen, npc_color, (center_x, center_y), 15)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 15, 2)

        # NPC名稱
        name_surface = font_manager.render_text(npc["name"], 14, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(center_x, center_y - 25))
        screen.blit(name_surface, name_rect)

    def render_stairs(self, screen, stairs):
        """渲染樓梯 - 支援圖片和像素繪製"""
        x, y = stairs["x"], stairs["y"]
        width, height = stairs["width"], stairs["height"]
        direction = stairs["direction"]

        # 🎨 優先使用圖片渲染
        if self.use_sprites and direction in self.stairs_sprites and self.stairs_sprites[direction]:
            self.render_stairs_sprite(screen, stairs)
        else:
            # 備用：像素風格樓梯
            self.render_stairs_pixel(screen, stairs)

        # 互動提示
        hint_surface = font_manager.render_text("空白鍵", 12, (255, 255, 0))
        hint_rect = hint_surface.get_rect(center=(x + width//2, y - 20))  # 🆕 調整提示位置
        screen.blit(hint_surface, hint_rect)

    def render_stairs_sprite(self, screen, stairs):
        """使用圖片渲染樓梯"""
        direction = stairs["direction"]
        sprite = self.stairs_sprites[direction]

        if sprite:
            # 繪製樓梯圖片
            screen.blit(sprite, (stairs["x"], stairs["y"]))

            # 添加方向指示效果
            if direction == "up":
                # 上樓梯：添加向上的光效
                pygame.draw.circle(screen, (255, 255, 0, 100),
                                 (stairs["x"] + 48, stairs["y"] + 15), 30, 2)  # 🆕 調整位置和大小
                # 向上箭頭
                arrow_points = [
                    (stairs["x"] + 48, stairs["y"] - 8),   # 🆕 調整箭頭位置
                    (stairs["x"] + 40, stairs["y"] + 8),
                    (stairs["x"] + 56, stairs["y"] + 8)
                ]
                pygame.draw.polygon(screen, (255, 255, 0), arrow_points)
            else:
                # 下樓梯：添加向下的光效
                pygame.draw.circle(screen, (0, 255, 255, 100),
                                 (stairs["x"] + 48, stairs["y"] + 33), 30, 2)  # 🆕 調整位置和大小
                # 向下箭頭
                arrow_points = [
                    (stairs["x"] + 48, stairs["y"] + 60),  # 🆕 調整箭頭位置
                    (stairs["x"] + 40, stairs["y"] + 45),
                    (stairs["x"] + 56, stairs["y"] + 45)
                ]
                pygame.draw.polygon(screen, (0, 255, 255), arrow_points)

    def render_stairs_pixel(self, screen, stairs):
        """像素風格渲染樓梯"""
        x, y = stairs["x"], stairs["y"]
        width, height = stairs["width"], stairs["height"]
        direction = stairs["direction"]

        if direction == "up":
            # 上樓梯：階梯向上
            stair_color = (160, 140, 100)
            highlight_color = (200, 180, 140)

            # 繪製多個階梯
            step_height = height // 4
            for i in range(4):
                step_y = y + (3 - i) * step_height
                step_width = width - i * 8
                step_x = x + i * 4

                # 階梯面
                pygame.draw.rect(screen, stair_color,
                               (step_x, step_y, step_width, step_height))
                # 階梯高光
                pygame.draw.rect(screen, highlight_color,
                               (step_x, step_y, step_width, 2))
                # 階梯邊框
                pygame.draw.rect(screen, (100, 80, 60),
                               (step_x, step_y, step_width, step_height), 1)

            # 上樓箭頭
            arrow_points = [
                (x + width//2, y - 8),      # 🆕 調整箭頭位置和大小
                (x + width//2 - 12, y + 8),
                (x + width//2 + 12, y + 8)
            ]
            pygame.draw.polygon(screen, (255, 255, 0), arrow_points)

        else:
            # 下樓梯：階梯向下
            stair_color = (140, 120, 80)
            shadow_color = (100, 80, 60)

            # 繪製向下的階梯
            step_height = height // 4
            for i in range(4):
                step_y = y + i * step_height
                step_width = width - i * 8
                step_x = x + i * 4

                # 階梯面
                pygame.draw.rect(screen, stair_color,
                               (step_x, step_y, step_width, step_height))
                # 階梯陰影
                pygame.draw.rect(screen, shadow_color,
                               (step_x, step_y + step_height - 2, step_width, 2))
                # 階梯邊框
                pygame.draw.rect(screen, (120, 100, 80),
                               (step_x, step_y, step_width, step_height), 1)

            # 下樓箭頭
            arrow_points = [
                (x + width//2, y + height + 12),    # 🆕 調整箭頭位置和大小
                (x + width//2 - 12, y + height - 3),
                (x + width//2 + 12, y + height - 3)
            ]
            pygame.draw.polygon(screen, (0, 255, 255), arrow_points)

    def render_combat_zones(self, screen):
        """渲染戰鬥區域"""
        if self.current_floor not in self.combat_zones:
            return

        for zone in self.combat_zones[self.current_floor]:
            # 危險區域標示
            danger_color = (255, 0, 0, 50)
            danger_rect = pygame.Rect(zone["x"], zone["y"], zone["width"], zone["height"])

            # 創建半透明表面
            danger_surface = pygame.Surface((zone["width"], zone["height"]))
            danger_surface.set_alpha(50)
            danger_surface.fill((255, 0, 0))
            screen.blit(danger_surface, (zone["x"], zone["y"]))

            # 危險區域邊框
            pygame.draw.rect(screen, (255, 0, 0), danger_rect, 2)

            # 警告文字
            warning_surface = font_manager.render_text("危險區域", 14, (255, 255, 255))
            warning_rect = warning_surface.get_rect(center=(zone["x"] + zone["width"]//2,
                                                          zone["y"] + zone["height"]//2))
            screen.blit(warning_surface, warning_rect)

    def render_items(self, screen):
        """🔧 修復：渲染物品，避免重疊顯示"""
        if self.current_floor not in self.items:
            return

        current_time = pygame.time.get_ticks()

        for item in self.items[self.current_floor]:
            # 創建物品ID檢查是否已收集
            item_id = f"{self.current_floor}_{item['name']}_{item['x']}_{item['y']}"

            # 如果已收集，跳過渲染
            if item_id in self.collected_items:
                continue

            # 🎨 改善：物品渲染效果
            self.render_single_item(screen, item, current_time)

    def render_single_item(self, screen, item, current_time):
        """🆕 渲染單個物品，帶有動畫效果"""
        x, y = item["x"], item["y"]
        item_type = item["type"]

        # 物品光暈效果（呼吸燈）
        pulse = abs((current_time % 2000 - 1000) / 1000.0)  # 0-1-0循環
        glow_alpha = int(100 + 100 * pulse)
        glow_radius = int(25 + 10 * pulse)

        # 物品類型顏色
        item_colors = {
            "healing": (255, 100, 100),
            "key": (255, 255, 0),
            "special": (0, 255, 0),
            "clue": (100, 100, 255)
        }

        base_color = item_colors.get(item_type, (255, 255, 255))

        # 繪製光暈
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*base_color, glow_alpha//2),
                          (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (x - glow_radius, y - glow_radius))

        # 繪製物品圖示
        if item_type == "healing":
            # 醫療包/能量包圖示
            if "醫療" in item["name"]:
                # 紅十字醫療包
                pygame.draw.rect(screen, (255, 255, 255), (x-8, y-8, 16, 16))
                pygame.draw.rect(screen, (255, 0, 0), (x-6, y-6, 12, 12))
                pygame.draw.rect(screen, (255, 255, 255), (x-1, y-6, 2, 12))
                pygame.draw.rect(screen, (255, 255, 255), (x-6, y-1, 12, 2))
            else:
                # 能量飲料瓶
                pygame.draw.rect(screen, (0, 150, 255), (x-4, y-10, 8, 20))
                pygame.draw.rect(screen, (100, 200, 255), (x-3, y-8, 6, 3))
                pygame.draw.circle(screen, (255, 255, 255), (x, y-11), 2)

        elif item_type == "key":
            # 鑰匙卡圖示
            pygame.draw.rect(screen, (255, 255, 0), (x-8, y-6, 16, 12))
            pygame.draw.rect(screen, (200, 200, 0), (x-8, y-6, 16, 12), 1)
            pygame.draw.rect(screen, (255, 255, 255), (x-6, y-4, 12, 8))
            pygame.draw.rect(screen, (100, 100, 100), (x-2, y-2, 4, 4))

        elif item_type == "special":
            # 特殊物品（解藥）
            pygame.draw.circle(screen, (0, 255, 0), (x, y), 12)
            pygame.draw.circle(screen, (0, 200, 0), (x, y), 12, 2)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 8)
            pygame.draw.circle(screen, (0, 255, 0), (x, y), 6)
            # 添加閃爍的十字
            if (current_time // 200) % 2:  # 閃爍效果
                pygame.draw.rect(screen, (255, 255, 255), (x-1, y-6, 2, 12))
                pygame.draw.rect(screen, (255, 255, 255), (x-6, y-1, 12, 2))

        elif item_type == "clue":
            # 線索物品（筆記）
            pygame.draw.rect(screen, (255, 255, 255), (x-6, y-8, 12, 16))
            pygame.draw.rect(screen, (100, 100, 255), (x-6, y-8, 12, 16), 1)
            # 文字線條
            for i in range(3):
                pygame.draw.rect(screen, (100, 100, 255), (x-4, y-6+i*3, 8, 1))

        # 物品名稱（帶背景）
        name_surface = font_manager.render_text(item["name"], 12, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(x, y - 35))

        # 名稱背景
        bg_rect = name_rect.copy()
        bg_rect.inflate(8, 4)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, bg_rect)

        screen.blit(name_surface, name_rect)

        # 物品描述（滑鼠懸停效果模擬）
        if hasattr(item, 'description') and item.get('description'):
            desc_surface = font_manager.render_text(item['description'], 10, (200, 200, 200))
            desc_rect = desc_surface.get_rect(center=(x, y + 25))

            # 描述背景
            desc_bg_rect = desc_rect.copy()
            desc_bg_rect.inflate(6, 2)
            desc_bg_surface = pygame.Surface(desc_bg_rect.size, pygame.SRCALPHA)
            desc_bg_surface.fill((0, 0, 0, 120))
            screen.blit(desc_bg_surface, desc_bg_rect)

            screen.blit(desc_surface, desc_rect)

    def get_item_color(self, item_type):
        """獲取物品類型對應的顏色"""
        colors = {
            "healing": (255, 100, 100),
            "key": (255, 255, 0),
            "special": (0, 255, 0),
            "clue": (100, 100, 255)
        }
        return colors.get(item_type, (255, 255, 255))

    def render_floor_info(self, screen):
        """渲染樓層資訊"""
        current_map = self.floor_maps[self.current_floor]

        # 樓層名稱
        floor_text = f"{current_map['name']}"
        floor_surface = font_manager.render_text(floor_text, 24, (255, 255, 255))
        screen.blit(floor_surface, (10, 10))

        # 樓層數字
        floor_num_text = f"{self.current_floor}F"
        floor_num_surface = font_manager.render_text(floor_num_text, 32, (255, 255, 0))
        screen.blit(floor_num_surface, (screen.get_width() - 80, 10))

        # 🆕 顯示當前樓層物品統計
        if self.current_floor in self.items:
            total_items = len(self.items[self.current_floor])
            collected_count = len([item for item in self.items[self.current_floor]
                                 if f"{self.current_floor}_{item['name']}_{item['x']}_{item['y']}" in self.collected_items])

            item_stats = f"物品: {collected_count}/{total_items}"
            stats_surface = font_manager.render_text(item_stats, 18, (200, 200, 200))
            screen.blit(stats_surface, (10, 40))

        # 🆕 顯示地板渲染狀態
        if self.use_floor_sprites:
            floor_status = "地板: 圖片模式 ✓"
            status_color = (0, 255, 0)
        else:
            floor_status = "地板: 程式繪製"
            status_color = (255, 255, 0)

        status_surface = font_manager.render_text(floor_status, 16, status_color)
        screen.blit(status_surface, (10, 65))

    def reload_stairs_images(self):
        """重新載入樓梯圖片（用於熱更新）"""
        print("🔄 重新載入樓梯圖片...")
        self.stairs_sprites.clear()
        self.load_stairs_images()

    def reload_floor_images(self):
        """🆕 重新載入地板圖片（用於熱更新）"""
        print("🔄 重新載入地板圖片...")
        self.floor_sprites.clear()
        self.load_floor_images()
    
    def reload_shop_images(self):
        """🆕 重新載入商店圖片（用於熱更新）"""
        print("🔄 重新載入商店圖片...")
        self.shop_sprites.clear()
        self.load_shop_images()

    def get_stairs_info(self, floor=None):
        """獲取樓梯資訊"""
        if floor is None:
            floor = self.current_floor

        if floor not in self.interactions:
            return []

        stairs = [item for item in self.interactions[floor] if item["type"] == "stairs"]
        return stairs

    def debug_print_stairs(self):
        """除錯：印出所有樓梯資訊"""
        print("🪜 樓梯偵錯資訊:")
        print(f"   圖片載入狀態: {self.use_sprites}")
        print(f"   載入的圖片: {list(self.stairs_sprites.keys())}")

        for floor, interactions in self.interactions.items():
            stairs = [item for item in interactions if item["type"] == "stairs"]
            if stairs:
                print(f"   {floor}樓樓梯:")
                for stair in stairs:
                    print(f"     - {stair['direction']}: ({stair['x']}, {stair['y']}) -> {stair.get('target_floor', '?')}樓")

    def debug_print_items(self):
        """🆕 除錯：印出所有物品資訊"""
        print("📦 物品偵錯資訊:")
        for floor, items in self.items.items():
            print(f"   {floor}樓物品:")
            for item in items:
                item_id = f"{floor}_{item['name']}_{item['x']}_{item['y']}"
                status = "已收集" if item_id in self.collected_items else "未收集"
                print(f"     - {item['name']}: ({item['x']}, {item['y']}) [{status}]")

        print(f"   總收集數: {len(self.collected_items)}")

    def debug_print_floor_info(self):
        """🆕 除錯：印出地板資訊"""
        print("🏢 地板偵錯資訊:")
        print(f"   使用圖片渲染: {self.use_floor_sprites}")
        print(f"   載入的地板圖片: {list(self.floor_sprites.keys())}")
        if self.use_floor_sprites:
            for floor_type, sprite in self.floor_sprites.items():
                if sprite:
                    size = sprite.get_size()
                    print(f"     - {floor_type}: {size[0]}x{size[1]} 像素")
    
    def debug_print_shop_info(self):
        """🆕 除錯：印出商店圖片資訊"""
        print("🏪 商店圖片偵錯資訊:")
        print(f"   使用圖片渲染: {self.use_shop_sprites}")
        print(f"   載入的商店圖片: {list(self.shop_sprites.keys())}")
        if self.use_shop_sprites:
            for shop_type, sprite in self.shop_sprites.items():
                if sprite:
                    size = sprite.get_size()
                    print(f"     - {shop_type}: {size[0]}x{size[1]} 像素")

    def get_available_items(self, floor=None):
        """🆕 獲取可用物品列表"""
        if floor is None:
            floor = self.current_floor

        if floor not in self.items:
            return []

        available_items = []
        for item in self.items[floor]:
            item_id = f"{floor}_{item['name']}_{item['x']}_{item['y']}"
            if item_id not in self.collected_items:
                available_items.append(item)

        return available_items

    def reset_items(self):
        """🆕 重置所有物品收集狀態"""
        self.collected_items.clear()
        print("🔄 已重置所有物品收集狀態")
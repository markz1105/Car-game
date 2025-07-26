import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 确保中文正常显示
pygame.font.init()
font_path = pygame.font.match_font('simsun')  # 尝试匹配中文字体
if not font_path:
    # 如果找不到中文字体，使用默认字体
    font_path = pygame.font.get_default_font()
font = pygame.font.Font(font_path, 36)
small_font = pygame.font.Font(font_path, 24)

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("马路躲避游戏")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)       # 马路颜色
YELLOW = (255, 255, 0)    # 马路标线颜色
LIGHT_GRAY = (150, 150, 150)  # 路边颜色

# 玩家设置
player_width = 40
player_height = 60
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 8

# 障碍物（车辆）设置
min_car_width = 40
max_car_width = 70
min_car_height = 60
max_car_height = 80
car_speed = 5
cars = []

# 马路设置
road_width = WIDTH * 0.8  # 马路宽度为屏幕的80%
road_left = (WIDTH - road_width) // 2
road_right = road_left + road_width
road_markings = []
for i in range(10):
    road_markings.append({"y": i * 60 - 30, "width": 20, "height": 40})

# 游戏变量
score = 0
clock = pygame.time.Clock()
FPS = 60
spawn_rate = 60  # 每60帧生成一个障碍物
frame_count = 0

def create_car():
    """创建一个新的车辆（随机大小和颜色）"""
    car_width = random.randint(min_car_width, max_car_width)
    car_height = random.randint(min_car_height, max_car_height)
    # 确保车辆在马路范围内生成
    x = random.randint(road_left, int(road_right - car_width))
    y = -car_height
    
    # 随机车辆颜色（排除与马路相近的深色）
    colors = [
        (255, 0, 0), (0, 0, 255), (0, 150, 0), 
        (255, 165, 0), (128, 0, 128), (255, 192, 203)
    ]
    color = random.choice(colors)
    
    return {
        'x': x, 'y': y, 'width': car_width, 
        'height': car_height, 'color': color
    }

def check_collision(player_x, player_y, car):
    """检查玩家是否与车辆碰撞"""
    p_left = player_x
    p_right = player_x + player_width
    p_top = player_y
    p_bottom = player_y + player_height
    
    o_left = car['x']
    o_right = car['x'] + car['width']
    o_top = car['y']
    o_bottom = car['y'] + car['height']
    
    return (p_right > o_left and p_left < o_right and
            p_bottom > o_top and p_top < o_bottom)

def draw_road():
    """绘制马路和标线"""
    # 绘制路边
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, road_left, HEIGHT))
    pygame.draw.rect(screen, LIGHT_GRAY, (road_right, 0, WIDTH - road_right, HEIGHT))
    
    # 绘制马路
    pygame.draw.rect(screen, GRAY, (road_left, 0, road_width, HEIGHT))
    
    # 绘制马路中间的虚线
    for marking in road_markings:
        pygame.draw.rect(
            screen, YELLOW, 
            (road_left + road_width//2 - marking['width']//2, 
             marking['y'], 
             marking['width'], 
             marking['height'])
        )
        # 移动标线，营造移动感
        marking['y'] += car_speed / 2
        if marking['y'] > HEIGHT:
            marking['y'] = -marking['height']

def draw_player():
    """绘制玩家（简化的汽车形状）"""
    # 车身
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))
    # 车窗
    pygame.draw.rect(
        screen, BLUE, 
        (player_x + 5, player_y + 5, player_width - 10, player_height // 3)
    )
    # 车轮
    wheel_size = (8, 12)
    # 左前轮
    pygame.draw.rect(
        screen, BLACK, 
        (player_x - 2, player_y + 10, wheel_size[0], wheel_size[1])
    )
    # 左后轮
    pygame.draw.rect(
        screen, BLACK, 
        (player_x - 2, player_y + player_height - wheel_size[1] - 10, 
         wheel_size[0], wheel_size[1])
    )
    # 右前轮
    pygame.draw.rect(
        screen, BLACK, 
        (player_x + player_width - wheel_size[0] + 2, player_y + 10, 
         wheel_size[0], wheel_size[1])
    )
    # 右后轮
    pygame.draw.rect(
        screen, BLACK, 
        (player_x + player_width - wheel_size[0] + 2, 
         player_y + player_height - wheel_size[1] - 10, 
         wheel_size[0], wheel_size[1])
    )

def draw_car(car):
    """绘制车辆"""
    # 车身
    pygame.draw.rect(
        screen, car['color'], 
        (car['x'], car['y'], car['width'], car['height'])
    )
    # 车窗
    window_color = (200, 200, 255)  # 浅蓝色车窗
    pygame.draw.rect(
        screen, window_color, 
        (car['x'] + 5, car['y'] + 5, car['width'] - 10, car['height'] // 3)
    )
    # 车轮
    wheel_size = (8, 12)
    # 左前轮
    pygame.draw.rect(
        screen, BLACK, 
        (car['x'] - 2, car['y'] + 10, wheel_size[0], wheel_size[1])
    )
    # 左后轮
    pygame.draw.rect(
        screen, BLACK, 
        (car['x'] - 2, car['y'] + car['height'] - wheel_size[1] - 10, 
         wheel_size[0], wheel_size[1])
    )
    # 右前轮
    pygame.draw.rect(
        screen, BLACK, 
        (car['x'] + car['width'] - wheel_size[0] + 2, car['y'] + 10, 
         wheel_size[0], wheel_size[1])
    )
    # 右后轮
    pygame.draw.rect(
        screen, BLACK, 
        (car['x'] + car['width'] - wheel_size[0] + 2, 
         car['y'] + car['height'] - wheel_size[1] - 10, 
         wheel_size[0], wheel_size[1])
    )

def game_over_screen():
    """游戏结束画面"""
    while True:
        screen.fill(BLACK)
        
        # 显示游戏结束文字
        game_over_text = font.render("游戏结束", True, RED)
        score_text = font.render(f"得分: {score}", True, WHITE)
        restart_text = small_font.render("按R键重新开始，按Q键退出", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.update()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # 重新开始游戏
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main_game():
    """主游戏循环"""
    # 声明要使用的全局变量
    global player_x, player_y, cars, score, frame_count, spawn_rate
    
    # 重置游戏状态
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    cars = []
    score = 0
    frame_count = 0
    spawn_rate = 60  # 重置生成速率
    
    running = True
    while running:
        screen.fill(BLACK)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # 玩家控制（限制在马路范围内）
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > road_left:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < road_right - player_width:
            player_x += player_speed
        if keys[pygame.K_a] and player_x > road_left:
            player_x -= player_speed  # A键左移
        if keys[pygame.K_d] and player_x < road_right - player_width:
            player_x += player_speed  # D键右移
        
        # 生成车辆
        frame_count += 1
        if frame_count % spawn_rate == 0:
            cars.append(create_car())
            # 随着分数增加，提高难度
            if score % 5 == 0 and spawn_rate > 10:
                spawn_rate = max(10, spawn_rate - 1)
        
        # 绘制马路
        draw_road()
        
        # 移动和绘制车辆
        for car in cars[:]:
            car['y'] += car_speed
            draw_car(car)
            
            # 检查碰撞
            if check_collision(player_x, player_y, car):
                running = False
            
            # 移除超出屏幕的车辆并增加分数
            if car['y'] > HEIGHT:
                cars.remove(car)
                score += 1
        
        # 绘制玩家
        draw_player()
        
        # 显示分数
        score_display = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_display, (10, 10))
        
        # 刷新屏幕
        pygame.display.update()
        clock.tick(FPS)
    
    # 游戏结束后显示结束画面
    game_over_screen()

# 游戏主循环
while True:
    main_game()
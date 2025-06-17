import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {  # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数:こうかとんRectまたは爆弾Rect
    戻り値：横方向, 縦方向の画面内判定結果
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True  #初期値、画面内
    if rct.left < 0 or WIDTH < rct.right: #横方向の画面外判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向の画面外判定
        tate = False
    return yoko, tate #横方向,縦方向の画面内判定結果を返す

def draw_gameover(screen):
    # ブラックアウト
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.set_alpha(128)
    blackout.fill((0, 0, 0))
    screen.blit(blackout, (0, 0))
    
    # 泣いているこうかとん画像の読み込みと表示
    left_kk_img = pg.image.load("fig/8.png")  # 泣いてるこうかとん画像
    left_kk_img = pg.transform.rotozoom(left_kk_img, 0, 0.9)
    left_kk_rct = left_kk_img.get_rect(center=(350,325))
    screen.blit(left_kk_img, left_kk_rct)

    right_kk_img = pg.image.load("fig/8.png")  # 泣いてるこうかとん画像
    right_kk_img = pg.transform.rotozoom(right_kk_img, 0, 0.9)
    right_kk_rct = right_kk_img.get_rect(center=(750,325))
    screen.blit(right_kk_img, right_kk_rct)

    # "Game Over" テキスト表示
    font = pg.font.SysFont(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT //2))
    screen.blit(txt, txt_rect)

    pg.display.update()  # 表示を反映
    time.sleep(5)  # 5秒待機

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 向きによって画像を回転・反転で切り替える（元画像: fig/3.png）
    base_img = pg.image.load("fig/3.png")
    kk_imgs = {
        (0, 0): pg.transform.rotozoom(base_img, 0, 0.9),
        (-5, 0): pg.transform.rotozoom(base_img, 0, 0.9),
        (-5, +5): pg.transform.rotozoom(base_img, 45, 0.9),
        (0, +5): pg.transform.rotozoom(base_img, 90, 0.9),
        (+5, +5): pg.transform.flip(pg.transform.rotozoom(base_img, 45, 0.9), True, False),
        (+5, 0): pg.transform.flip(pg.transform.rotozoom(base_img, 0, 0.9), True, False),
        (+5, -5): pg.transform.flip(pg.transform.rotozoom(base_img, -45, 0.9), True, False),
        (0, -5): pg.transform.rotozoom(base_img, -90, 0.9),
        (-5, -5): pg.transform.rotozoom(base_img, -45, 0.9),
    }

    
    # 加速度と爆弾画像のリスト
    bb_accs = [a for a in range(1, 11)]
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)

    bb_img = pg.Surface((20,20))#空のSurfaceを作る（爆弾用）
    pg.draw.circle(bb_img,(255,0,0), (10,10), 10)#赤い円を描く
    bb_img.set_colorkey((0,0,0))
    bb_rct = bb_img.get_rect() #爆弾Rectを取得
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5 #爆弾の移動速度
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            draw_gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) #移動をなかったことにする
        # 移動方向に応じてこうかとんの画像を切り替え
        mv_tuple = tuple(sum_mv)
        if mv_tuple in kk_imgs:
            kk_img = kk_imgs[mv_tuple]

        screen.blit(kk_img, kk_rct)
        
        # 時間に応じた爆弾の加速と拡大
        index = min(tmr // 500, 9)
        avx = vx * bb_accs[index]
        avy = vy * bb_accs[index]
        bb_img = bb_imgs[index]
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

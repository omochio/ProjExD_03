import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 3  # 爆弾の初期数
MIN_BOMB_SIZE = 10
MAX_BOMB_SIZE = 80
MIN_BOMB_VELOCITY = -2
MAX_BOMB_VELOCITY = 2


def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate

class Character:
    """
    ゲームキャラクターの基底クラス
    """
    def get_rct(self) -> pg.Rect:
        """
        rectを返す
        """
        return self._rct

def check_collide(c1: Character, c2: Character) -> bool:
    """
    キャラクターの衝突判定を行う
    引数1 c1: キャラクター1
    引数2 c2: キャラクター2
    戻り値: 衝突判定の真理値
    """
    return c1.get_rct().colliderect(c2.get_rct())

class Bird(Character):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        self._rct = self._img.get_rect()
        self._rct.center = xy
        # 回転画像選択用辞書
        self.rot_dict = {
            (0, -1): pg.transform.rotozoom(self._img, 90, 1),
            (1, -1): pg.transform.rotozoom(self._img, 45, 1),
            (1, 0): self._img,
            (1, 1): pg.transform.rotozoom(self._img, -45, 1),
            (0, 1): pg.transform.rotozoom(self._img, -90, 1),
            (-1, 1): pg.transform.rotozoom(pg.transform.flip(self._img, True, False), 45, 1),
            (-1, 0): pg.transform.flip(self._img, True, False),
            (-1, -1): pg.transform.rotozoom(pg.transform.flip(self._img, True, False), -45, 1)
        }



    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """

        # 軸ごとの速度を保持
        bird_vel = [0, 0]
        for k, mv in __class__._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
                bird_vel[0] += mv[0]
                bird_vel[1] += mv[1]
        # 速度に応じて回転
        if (not bird_vel == [0, 0]):
            self._img = self.rot_dict[tuple(bird_vel)]

        if check_bound(screen.get_rect(), self._rct) != (True, True):
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        screen.blit(self._img, self._rct)

class Bomb(Character):
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = random.randint(MIN_BOMB_VELOCITY, MAX_BOMB_VELOCITY), random.randint(MIN_BOMB_VELOCITY, MAX_BOMB_VELOCITY)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen: 画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self._rct)
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)

class Beam(Character):
    def __init__(self, bird: Bird):
        """
        ビームを初期化
        引数 bird: Birdインスタンス
        """
        self._img = pg.transform.rotozoom(pg.image.load("ex03/fig/beam.png"), 0, 2.0)
        self._rct = self._img.get_rect()
        self._rct.centerx = bird.get_rct().centerx + 100
        self._rct.centery = bird.get_rct().centery
        self._vx = +1

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen: 画面Surface
        """
        self._rct.move_ip(self._vx, 0)
        screen.blit(self._img, self._rct)

class Explosion():
    """
    爆発エフェクト
    """
    _min_life = 500
    _max_life = 1000

    def __init__(self, xy: tuple, bframe):
        """
        爆発エフェクトを初期化
        引数1 xy: 爆発位置
        引数2 bframe: 開始フレーム数
        """
        self.bframe = bframe
        img = pg.image.load("ex03/fig/explosion.gif")
        # 爆発パターン
        self._imgs = [
            img, 
            pg.transform.flip(img, True, False),
            pg.transform.flip(img, False, True),
            pg.transform.flip(img, True, True)]
        self._life = random.randint(__class__._min_life, __class__._max_life)
        self.rct = img.get_rect()
        self.rct.center = xy

    def is_playing(self, cframe: float) -> bool:
        """
        再生中かのboolを返す
        引数1 cframe: 現在フレーム数
        """
        return (cframe - self.bframe < self._life)

    def update(self, screen: pg.Surface):
        """
        爆発エフェクトを更新する
        引数1 screen: 画面Surface
        """
        screen.blit(self._imgs[random.randint(0, 3)], self.rct)

class ScoreManager():
    """
    スコア管理を行うクラス
    """
    _point = 100

    def __init__(self):
        self._score = 0

    def add_score(self):
        """
        スコアを加算
        """
        self._score += __class__._point

    def show_score(self, screen: pg.Surface):
        """
        スコアを表示
        引数1 screen: スクリーンサーフェイス
        """
        text = pg.font.SysFont(None, 100).render(f"Score: {self._score}", True, (255, 255, 0))
        screen.blit(text, (0, 0))


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")

    bird = Bird(3, (900, 400))
    bombs = [Bomb((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), random.randint(MIN_BOMB_SIZE, MAX_BOMB_SIZE)) for i in range(NUM_OF_BOMBS)]
    explosions = []
    beam = None
    sm = ScoreManager()

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam = Beam(bird)

        if (len(bombs) <= 0):
            return

        tmr += 1
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if check_collide(bird, bomb):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return

        key_lst = pg.key.get_pressed()
        
        bird.update(key_lst, screen)
        for i, bomb in enumerate(bombs):
            bomb.update(screen)
            if (beam is not None):
                beam.update(screen)
                if (check_collide(beam, bomb)):
                    bird.change_img(6, screen)
                    beam = None
                    explosions.append(Explosion(bomb.get_rct().center, tmr))
                    sm.add_score()
                    bombs.pop(i)

        if (len(explosions) > 0):
            for i, exp in enumerate(explosions):
                if (exp.is_playing(tmr)):
                    exp.update(screen)
                else:
                    explosions.pop(i)

        sm.show_score(screen)

        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

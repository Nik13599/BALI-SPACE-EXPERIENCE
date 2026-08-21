import os, sys, math, time, random, threading
from dataclasses import dataclass
from collections import deque

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')

import numpy as np
import pygame

APP_NAME='BALI SPACE EXPERIENCE'
VERSION='0.1.0'
BASE_W, BASE_H = 1920, 1080


def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

@dataclass
class AudioState:
    bass: float = 0.0
    mid: float = 0.0
    high: float = 0.0
    energy: float = 0.0
    bpm: float = 120.0
    beat: float = 0.0
    active: bool = False

class AudioAnalyzer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.state = AudioState()
        self._lock = threading.Lock()
        self._stop_evt = threading.Event()
        self._beat_times = deque(maxlen=16)
        self._prev_energy = 0.0

    def stop(self):
        self._stop_evt.set()

    def get(self):
        with self._lock:
            return AudioState(**self.state.__dict__)

    def run(self):
        try:
            import soundcard as sc
            speaker = sc.default_speaker()
            if speaker is None:
                raise RuntimeError('No default Windows speaker')
            mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            samplerate = 48000
            block = 2048
            with mic.recorder(samplerate=samplerate, channels=2) as rec:
                while not self._stop_evt.is_set():
                    data = rec.record(numframes=block)
                    if data is None or len(data) == 0:
                        continue
                    mono = np.mean(data, axis=1).astype(np.float32)
                    self._process(mono, samplerate)
        except Exception:
            t0 = time.time()
            while not self._stop_evt.is_set():
                t = time.time() - t0
                pulse = max(0.0, math.sin(t * math.pi * 2 * 2.0)) ** 8
                with self._lock:
                    self.state = AudioState(
                        bass=0.25 + 0.55*pulse,
                        mid=0.18 + 0.18*(math.sin(t*2.1)+1)/2,
                        high=0.12 + 0.12*(math.sin(t*4.7)+1)/2,
                        energy=0.18 + 0.42*pulse,
                        bpm=120.0,
                        beat=pulse,
                        active=False,
                    )
                time.sleep(0.02)

    def _process(self, mono, sr):
        if len(mono) < 32:
            return
        win = np.hanning(len(mono))
        spec = np.abs(np.fft.rfft(mono * win))
        freqs = np.fft.rfftfreq(len(mono), 1.0/sr)
        rms = float(np.sqrt(np.mean(mono*mono)) + 1e-9)

        def band(lo, hi):
            m = (freqs >= lo) & (freqs < hi)
            if not np.any(m): return 0.0
            return float(np.mean(spec[m]))

        bass_raw = band(25, 180)
        mid_raw  = band(180, 2200)
        high_raw = band(2200, 11000)
        bass = np.clip(math.log1p(bass_raw)*0.22, 0, 1)
        mid  = np.clip(math.log1p(mid_raw)*0.18, 0, 1)
        high = np.clip(math.log1p(high_raw)*0.16, 0, 1)
        energy = np.clip(math.log1p(rms*55.0)*0.55, 0, 1)

        now = time.time()
        beat = 0.0
        threshold = max(0.09, self._prev_energy*1.20)
        if energy > threshold and energy > 0.18 and now - (self._beat_times[-1] if self._beat_times else 0) > 0.23:
            beat = 1.0
            self._beat_times.append(now)
        self._prev_energy = self._prev_energy*0.88 + energy*0.12

        bpm = 120.0
        if len(self._beat_times) >= 4:
            ints = np.diff(np.array(self._beat_times, dtype=np.float64))
            ints = ints[(ints > 0.24) & (ints < 1.2)]
            if len(ints):
                bpm = float(60.0/np.median(ints))
                while bpm < 70: bpm *= 2
                while bpm > 180: bpm /= 2

        with self._lock:
            old = self.state
            s = 0.30
            self.state = AudioState(
                bass=old.bass*(1-s)+bass*s,
                mid=old.mid*(1-s)+mid*s,
                high=old.high*(1-s)+high*s,
                energy=old.energy*(1-s)+energy*s,
                bpm=old.bpm*0.88+bpm*0.12,
                beat=max(beat, old.beat*0.72),
                active=True,
            )

class Starfield:
    def __init__(self, count=460):
        self.stars=[]
        for _ in range(count): self.reset_star(None)

    def reset_star(self, star):
        s = [random.uniform(-1.25,1.25), random.uniform(-0.72,0.72), random.uniform(0.06,1.0), random.uniform(0.5,1.7)]
        if star is None: self.stars.append(s)
        else: star[:] = s

    def update_draw(self, surf, dt, speed, warp, beat):
        cx, cy = BASE_W/2, BASE_H/2
        fov=840
        for st in self.stars:
            st[2] -= dt * (0.08 + speed*0.22) * st[3]
            if st[2] <= 0.025:
                self.reset_star(st); st[2]=1.0
            x = cx + (st[0]/st[2])*fov
            y = cy + (st[1]/st[2])*fov
            if x < -100 or x > BASE_W+100 or y < -100 or y > BASE_H+100:
                self.reset_star(st); continue
            b = int(np.clip(100 + 155*(1-st[2]), 100, 255))
            col=(b, min(255,b+15), 255)
            r=max(1,int((1-st[2])*3.5))
            if warp > .15:
                px = cx + (st[0]/(st[2]+0.06+warp*.08))*fov
                py = cy + (st[1]/(st[2]+0.06+warp*.08))*fov
                pygame.draw.line(surf,col,(px,py),(x,y),max(1,r))
            else:
                pygame.draw.circle(surf,col,(int(x),int(y)),r)

class Asteroid:
    def __init__(self): self.reset(True)
    def reset(self, initial=False):
        self.x=random.uniform(-200, BASE_W+300) if initial else -240
        self.y=random.uniform(40, BASE_H-80)
        self.r=random.uniform(10,55)
        self.depth=random.uniform(.3,1.0)
        self.v=random.uniform(25,95)*self.depth
        self.rot=random.uniform(0,math.tau)
        self.rv=random.uniform(-1.2,1.2)
        n=random.randint(7,12)
        self.shape=[random.uniform(.68,1.18) for _ in range(n)]
    def update_draw(self,surf,dt,speed,energy):
        self.x += self.v * dt * (0.55 + speed*1.35)
        self.rot += self.rv*dt*(.6+energy)
        if self.x > BASE_W+180: self.reset(False)
        pts=[]; n=len(self.shape)
        for i,m in enumerate(self.shape):
            a=self.rot+i*math.tau/n
            rr=self.r*m
            pts.append((self.x+math.cos(a)*rr,self.y+math.sin(a)*rr))
        shade=int(45+70*self.depth+35*energy)
        pygame.draw.polygon(surf,(shade,shade-7,shade-12),pts)
        pygame.draw.lines(surf,(min(200,shade+40),shade+20,shade+10),True,pts,max(1,int(self.depth*2)))
        pygame.draw.circle(surf,(max(15,shade-25),)*3,(int(self.x-self.r*.18),int(self.y-self.r*.12)),max(2,int(self.r*.16)))

class Planet:
    def __init__(self):
        self.angle=0.0
        self.surface=pygame.Surface((620,620), pygame.SRCALPHA)
    def draw(self,surf,dt,speed,bass):
        self.angle += dt*(.08+.40*speed)
        ps=self.surface; ps.fill((0,0,0,0)); c=(310,310); R=265
        for i in range(28,0,-1):
            a=int(2+(28-i)*.55)
            pygame.draw.circle(ps,(50,130,255,a),c,R+i*3)
        for rr in range(R,0,-4):
            t=rr/R
            col=(int(10+12*(1-t)),int(25+38*(1-t)),int(52+85*(1-t)))
            pygame.draw.circle(ps,col,c,rr)
        clip=pygame.Surface(ps.get_size(),pygame.SRCALPHA)
        off=(self.angle*95)%520
        for k in range(11):
            x=int((k*120-off)%650)-15
            y=190+int(90*math.sin(k*1.8+self.angle*.4))
            pygame.draw.ellipse(clip,(40,105,85,145),(x,y,150,55))
            pygame.draw.ellipse(clip,(170,205,230,42),(x-45,y-55,240,22))
        m=pygame.Surface(ps.get_size(),pygame.SRCALPHA); pygame.draw.circle(m,(255,255,255,255),c,R)
        clip.blit(m,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
        ps.blit(clip,(0,0))
        for i in range(26):
            a=i*2.39+self.angle*.18; rad=R*random.Random(i).uniform(.15,.92)
            x=c[0]+math.cos(a)*rad*.78; y=c[1]+math.sin(a*1.31)*rad*.55
            pygame.draw.circle(ps,(255,175+int(50*bass),70,120+int(100*bass)),(int(x),int(y)),1+int(2*bass))
        shadow=pygame.Surface(ps.get_size(),pygame.SRCALPHA)
        pygame.draw.ellipse(shadow,(0,0,8,115),(130,45,530,540))
        ps.blit(shadow,(0,0))
        surf.blit(ps,(BASE_W-570,BASE_H-560))

class BaliCharacter:
    def __init__(self):
        img=pygame.image.load(resource_path('assets/bali_astronaut.png')).convert_alpha()
        self.original=img
        self.phase=0.0
    def draw(self,surf,dt,audio):
        self.phase += dt
        tempo=np.clip((audio.bpm-75)/85,0,1)
        self.phase += dt*tempo*.35
        pulse=1.0 + audio.bass*.035 + audio.beat*.025
        bob=math.sin(self.phase*1.25)*18*(.6+tempo)
        sway=math.sin(self.phase*.62)*13
        angle=math.sin(self.phase*.55)*1.9 + audio.beat*1.0
        target_h=int(790*pulse)
        scale=target_h/self.original.get_height()
        target_w=int(self.original.get_width()*scale)
        img=pygame.transform.smoothscale(self.original,(target_w,target_h))
        img=pygame.transform.rotozoom(img,angle,1.0)
        if audio.bass>.35:
            glow=pygame.transform.smoothscale(img,(img.get_width()+int(20*audio.bass),img.get_height()+int(20*audio.bass)))
            glow.set_alpha(int(25+50*audio.bass))
            surf.blit(glow,(BASE_W*.47-glow.get_width()/2+sway,BASE_H*.49-glow.get_height()/2+bob),special_flags=pygame.BLEND_RGBA_ADD)
        surf.blit(img,(BASE_W*.47-img.get_width()/2+sway,BASE_H*.49-img.get_height()/2+bob))

class App:
    def __init__(self):
        pygame.init(); pygame.font.init()
        flags=pygame.FULLSCREEN|pygame.DOUBLEBUF
        self.screen=pygame.display.set_mode((0,0),flags)
        pygame.display.set_caption(APP_NAME)
        self.canvas=pygame.Surface((BASE_W,BASE_H)).convert()
        self.clock=pygame.time.Clock()
        self.running=True
        self.show_hud=True
        self.starfield=Starfield()
        self.asteroids=[Asteroid() for _ in range(18)]
        self.planet=Planet()
        self.character=BaliCharacter()
        self.audio=AudioAnalyzer(); self.audio.start()
        self.font=pygame.font.SysFont('segoeui',24)
        self.small=pygame.font.SysFont('segoeui',17)
        self.big=pygame.font.SysFont('segoeui',34,bold=True)
        self.warp=0.0

    def draw_background(self,audio,dt):
        c=self.canvas
        c.fill((2,4,13))
        neb=pygame.Surface((BASE_W,BASE_H),pygame.SRCALPHA)
        t=time.time()
        for i in range(7):
            x=int(BASE_W*(.08+i*.16)+math.sin(t*.07+i)*45)
            y=int(BASE_H*(.18+(i%3)*.23))
            r=190+45*(i%2)
            col=(70+15*(i%2),18,72+24*(i%3),20)
            pygame.draw.circle(neb,col,(x,y),r)
        c.blit(neb,(0,0),special_flags=pygame.BLEND_RGBA_ADD)
        tempo=np.clip((audio.bpm-75)/85,0,1)
        speed=.35 + tempo*1.25 + audio.energy*1.8
        target_warp=1.0 if (audio.energy>.58 and audio.bass>.48) else audio.energy*.25
        self.warp += (target_warp-self.warp)*min(1,dt*4)
        self.starfield.update_draw(c,dt,speed,self.warp,audio.beat)
        self.planet.draw(c,dt,speed,audio.bass)
        for a in sorted(self.asteroids,key=lambda q:q.depth): a.update_draw(c,dt,speed,audio.energy)

    def draw_hud(self,audio):
        if not self.show_hud: return
        panel=pygame.Surface((360,112),pygame.SRCALPHA); panel.fill((3,6,15,145))
        panel.blit(self.big.render('BALI SPACE',True,(245,245,245)),(18,12))
        panel.blit(self.small.render('AUDIO REACTIVE VISUAL SYSTEM',True,(210,170,95)),(20,51))
        src='SYSTEM AUDIO' if audio.active else 'DEMO / WAITING FOR AUDIO'
        panel.blit(self.small.render(f'{src}  •  {audio.bpm:0.0f} BPM',True,(170,185,210)),(20,78))
        self.canvas.blit(panel,(28,28))
        x,y=BASE_W-312,42
        pygame.draw.rect(self.canvas,(20,28,45),(x,y,260,14),border_radius=7)
        pygame.draw.rect(self.canvas,(205,156,70),(x,y,int(260*audio.energy),14),border_radius=7)
        self.canvas.blit(self.small.render('MUSIC ENERGY',True,(180,190,215)),(x,y+22))

    def present(self):
        sw,sh=self.screen.get_size(); aspect=BASE_W/BASE_H
        if sw/sh>aspect:
            h=sh; w=int(h*aspect)
        else:
            w=sw; h=int(w/aspect)
        frame=pygame.transform.smoothscale(self.canvas,(w,h))
        self.screen.fill((0,0,0)); self.screen.blit(frame,((sw-w)//2,(sh-h)//2)); pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt=min(.05,self.clock.tick(60)/1000.0)
                for e in pygame.event.get():
                    if e.type==pygame.QUIT: self.running=False
                    elif e.type==pygame.KEYDOWN:
                        if e.key in (pygame.K_ESCAPE,pygame.K_q): self.running=False
                        elif e.key in (pygame.K_h,pygame.K_F1): self.show_hud=not self.show_hud
                audio=self.audio.get()
                self.draw_background(audio,dt)
                self.character.draw(self.canvas,dt,audio)
                if audio.beat>.15:
                    flash=pygame.Surface((BASE_W,BASE_H),pygame.SRCALPHA)
                    flash.fill((255,178,65,int(18*audio.beat)))
                    self.canvas.blit(flash,(0,0),special_flags=pygame.BLEND_RGBA_ADD)
                self.draw_hud(audio)
                self.present()
        finally:
            self.audio.stop(); pygame.quit()

if __name__=='__main__':
    App().run()

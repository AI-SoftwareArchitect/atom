import pygame
import random
import math
import numpy as np
from pygame import gfxdraw

# Pygame başlatma
pygame.init()

# Ekran ayarları
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geliştirilmiş Atom Simülasyonu - Gerçekçi Etkileşimler")

# Renkler
BACKGROUND = (5, 5, 15)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
WHITE = (220, 220, 220)
YELLOW = (255, 255, 100)
CYAN = (0, 255, 255)
PURPLE = (200, 100, 255)

# Performans ayarları
MAX_ATOMS = 1500
ATOM_DRAW_SIZE = 3
UPDATE_FRACTION = 0.3
INTERACTION_DISTANCE = 30

# Element özellikleri (proton, elektron, kütle, renk, isim)
ELEMENTS = {
    1: (1, 1, 1.0, (200, 200, 255), "Hidrojen"),
    6: (6, 6, 12.0, (80, 80, 80), "Karbon"),
    7: (7, 7, 14.0, (0, 0, 200), "Nitrojen"),
    8: (8, 8, 16.0, (255, 50, 50), "Oksijen"),
    11: (11, 11, 23.0, (255, 200, 50), "Sodyum"),
    17: (17, 17, 35.5, (50, 255, 50), "Klor"),
    26: (26, 26, 56.0, (200, 100, 50), "Demir"),
    29: (29, 29, 63.5, (200, 150, 50), "Bakır"),
    79: (79, 79, 197.0, (255, 215, 0), "Altın")
}

# Atom sınıfı
class Atom:
    __slots__ = ('x', 'y', 'protons', 'neutrons', 'electrons', 'mass', 'charge', 
                 'vx', 'vy', 'radius', 'color', 'name', 'bonded_atoms', 'bond_strength')
    
    def __init__(self, x, y, protons):
        self.x = x
        self.y = y
        self.protons = protons
        
        # Element özelliklerini al
        if protons in ELEMENTS:
            p, e, m, color, name = ELEMENTS[protons]
            self.electrons = e
            self.mass = m
            self.color = color
            self.name = name
        else:
            # Bilinmeyen element için varsayılan değerler
            self.electrons = protons
            self.mass = protons * 2
            self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            self.name = f"Element-{protons}"
        
        self.neutrons = round(self.mass) - protons
        self.charge = self.protons - self.electrons
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.radius = ATOM_DRAW_SIZE + (self.mass / 20)  # Kütleye göre boyut
        self.bonded_atoms = []  # Bağlı olduğu atomlar
        self.bond_strength = 0  # Bağ gücü
    
    def draw(self, surface):
        # Atomu ekrana çiz
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))
        
        # Bağları çiz
        for other_atom, strength in self.bonded_atoms:
            if id(self) < id(other_atom):  # Her bağı sadece bir kez çiz
                alpha = min(255, int(strength * 50))
                bond_color = (255, 255, 255, alpha)
                
                # Kalınlığı bağ gücüne göre ayarla
                thickness = max(1, int(strength / 2))
                
                # Çizgi çiz
                pygame.draw.line(
                    surface, 
                    bond_color, 
                    (int(self.x), int(self.y)), 
                    (int(other_atom.x), int(other_atom.y)), 
                    thickness
                )

# Madde sınıfı
class Matter:
    __slots__ = ('x', 'y', 'width', 'height', 'state', 'density', 'atoms', 'color', 'element_type')
    
    def __init__(self, x, y, width, height, state, density=0.5, element_type=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state
        self.density = density
        self.atoms = []
        self.element_type = element_type
        self.color = self.determine_color()
        self.create_atoms()
        
    def determine_color(self):
        if self.state == 'solid':
            return (100, 100, 200, 100)
        elif self.state == 'liquid':
            return (200, 100, 100, 100)
        else:  # gas
            return (200, 200, 100, 70)
        
    def create_atoms(self):
        # Maddeyi oluşturan atomları yarat
        atom_count = min(int(self.width * self.height * self.density), MAX_ATOMS // 4)
        
        # Element tipi belirle
        if self.element_type is None:
            if self.state == 'solid':
                element_choices = [6, 8, 26, 29]  # Katılar: C, O, Fe, Cu
            elif self.state == 'liquid':
                element_choices = [1, 8, 11, 17]  # Sıvılar: H, O, Na, Cl
            else:  # gas
                element_choices = [1, 7, 8]  # Gazlar: H, N, O
        else:
            element_choices = [self.element_type]
        
        for _ in range(atom_count):
            x = random.uniform(self.x, self.x + self.width)
            y = random.uniform(self.y, self.y + self.height)
            
            protons = random.choice(element_choices)
            atom = Atom(x, y, protons)
            
            # Maddenin durumuna göre başlangıç hızı belirle
            if self.state == 'solid':
                atom.vx = random.uniform(-0.2, 0.2)
                atom.vy = random.uniform(-0.2, 0.2)
            elif self.state == 'liquid':
                atom.vx = random.uniform(-0.8, 0.8)
                atom.vy = random.uniform(-0.8, 0.8)
            else:  # gas
                atom.vx = random.uniform(-2.0, 2.0)
                atom.vy = random.uniform(-2.0, 2.0)
                
            self.atoms.append(atom)
    
    def draw(self, surface):
        # Madde sınırlarını çiz
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill(self.color)
        surface.blit(s, (self.x, self.y))
        
        # Atomları çiz
        for atom in self.atoms:
            atom.draw(surface)

# Fizik motoru
class PhysicsEngine:
    __slots__ = ('width', 'height', 'gravity', 'coulomb_constant', 'bond_formation_energy', 
                 'bond_breaking_energy', 'thermal_energy', 'frame_count')
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity = 0.1
        self.coulomb_constant = 800
        self.bond_formation_energy = 5
        self.bond_breaking_energy = 10
        self.thermal_energy = 0.5
        self.frame_count = 0
        
    def update(self, atoms):
        self.frame_count += 1
        
        # Her karede sadece bir kısmını güncelle
        update_count = int(len(atoms) * UPDATE_FRACTION)
        if update_count < 1:
            update_count = 1
            
        for _ in range(update_count):
            idx = random.randint(0, len(atoms) - 1)
            atom = atoms[idx]
            
            # Diğer atomlarla etkileşim
            for other in atoms:
                if atom is other:
                    continue
                    
                dx = other.x - atom.x
                dy = other.y - atom.y
                distance_sq = dx*dx + dy*dy
                
                if distance_sq < 1:
                    distance_sq = 1
                    dx = random.uniform(-1, 1)
                    dy = random.uniform(-1, 1)
                
                distance = math.sqrt(distance_sq)
                
                # Sadece yakın atomlarla etkileşim
                if distance < INTERACTION_DISTANCE:
                    # Kimyasal bağ oluşumu
                    self.handle_bond_formation(atom, other, distance)
                    
                    # Coulomb etkileşimi (yükler arası)
                    coulomb_force = self.coulomb_constant * atom.charge * other.charge / distance_sq
                    
                    # Van der Waals kuvveti (nötr atomlar arası çekim)
                    vanderwaals_force = 0
                    if atom.charge == 0 and other.charge == 0:
                        vanderwaals_force = -500 / (distance_sq + 10)  # Çekim kuvveti
                    
                    # Toplam kuvvet
                    total_force = coulomb_force + vanderwaals_force
                    
                    # Bağlı atomlar için çekim kuvveti
                    is_bonded = any(bonded_atom is other for bonded_atom, _ in atom.bonded_atoms)
                    if is_bonded:
                        bond_strength = next(strength for bonded_atom, strength in atom.bonded_atoms if bonded_atom is other)
                        total_force -= bond_strength * 100 / (distance_sq + 1)
                    
                    # Kuvvet vektörü
                    force_x = total_force * dx / distance
                    force_y = total_force * dy / distance
                    
                    # İvme (F = ma)
                    acceleration_x = force_x / atom.mass
                    acceleration_y = force_y / atom.mass
                    
                    # Hızı güncelle
                    atom.vx += acceleration_x
                    atom.vy += acceleration_y
            
            # Yerçekimi (gazlar için daha az)
            gravity_factor = 1.0
            if abs(atom.vx) > 2.0 or abs(atom.vy) > 2.0:  # Gaz benzeri davranış
                gravity_factor = 0.3
            atom.vy += self.gravity * gravity_factor
            
            # Termal hareket (rastgele)
            atom.vx += random.uniform(-self.thermal_energy, self.thermal_energy)
            atom.vy += random.uniform(-self.thermal_energy, self.thermal_energy)
            
            # Hızı pozisyona uygula
            atom.x += atom.vx
            atom.y += atom.vy
            
            # Sınır kontrolü
            self.handle_boundaries(atom)
            
            # Bağları güncelle
            self.update_bonds(atom)
            
            # Sürtünme
            atom.vx *= 0.98
            atom.vy *= 0.98
            
        return atoms
    
    def handle_bond_formation(self, atom1, atom2, distance):
        # Bağ oluşumu için koşullar
        can_bond = (
            distance < 15 and  # Yeterince yakın
            atom1 not in [bond[0] for bond in atom2.bonded_atoms] and  # Zaten bağlı değil
            atom2 not in [bond[0] for bond in atom1.bonded_atoms] and
            len(atom1.bonded_atoms) < (4 if atom1.protons == 6 else 2) and  # Karbon 4 bağ yapabilir
            len(atom2.bonded_atoms) < (4 if atom2.protons == 6 else 2) and
            random.random() < 0.05  # Rastgele şans
        )
        
        if can_bond:
            # Bağ gücünü hesapla (elementlere göre)
            bond_strength = self.calculate_bond_strength(atom1, atom2)
            
            # Bağ oluştur
            atom1.bonded_atoms.append((atom2, bond_strength))
            atom2.bonded_atoms.append((atom1, bond_strength))
    
    def calculate_bond_strength(self, atom1, atom2):
        # Basit bir bağ gücü hesaplama
        base_strength = 10
        
        # Element kombinasyonlarına göre bağ gücü
        element_pair = tuple(sorted([atom1.protons, atom2.protons]))
        
        bond_strengths = {
            (1, 1): 8,      # H-H
            (1, 8): 15,     # H-O (su)
            (1, 6): 12,     # H-C
            (6, 6): 20,     # C-C
            (6, 8): 18,     # C-O
            (8, 8): 16,     # O-O
            (11, 17): 25,   # Na-Cl (tuz)
        }
        
        return bond_strengths.get(element_pair, base_strength)
    
    def update_bonds(self, atom):
        # Bağları kontrol et ve zayıf olanları kopar
        for i in range(len(atom.bonded_atoms) - 1, -1, -1):
            other_atom, strength = atom.bonded_atoms[i]
            
            # Bağ koparma koşulları
            dx = other_atom.x - atom.x
            dy = other_atom.y - atom.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 25 or random.random() < 0.001:  # Çok uzak veya rastgele kopma
                atom.bonded_atoms.pop(i)
                # Diğer atomdan da bu bağı kaldır
                for j in range(len(other_atom.bonded_atoms) - 1, -1, -1):
                    if other_atom.bonded_atoms[j][0] is atom:
                        other_atom.bonded_atoms.pop(j)
                        break
    
    def handle_boundaries(self, atom):
        # Ekran sınırlarında yansıma
        if atom.x < 0:
            atom.x = 0
            atom.vx = -atom.vx * 0.8
        elif atom.x > self.width:
            atom.x = self.width
            atom.vx = -atom.vx * 0.8
            
        if atom.y < 0:
            atom.y = 0
            atom.vy = -atom.vy * 0.8
        elif atom.y > self.height:
            atom.y = self.height
            atom.vy = -atom.vy * 0.8

# Ana fonksiyon
def main():
    clock = pygame.time.Clock()
    physics_engine = PhysicsEngine(WIDTH, HEIGHT)
    
    # Farklı elementlerden oluşan maddeler
    matters = [
        Matter(100, 100, 100, 100, 'solid', 0.4, 6),   # Karbon (katı)
        Matter(300, 400, 120, 80, 'liquid', 0.5, 1),   # Hidrojen (sıvı)
        Matter(500, 200, 150, 120, 'gas', 0.3, 8),     # Oksijen (gaz)
        Matter(700, 500, 80, 80, 'solid', 0.6, 26),    # Demir (katı)
    ]
    
    # Tüm atomları topla
    all_atoms = []
    for matter in matters:
        all_atoms.extend(matter.atoms)
    
    # Yazı tipleri
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 36)
    
    # Ana döngü
    running = True
    paused = False
    show_help = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Rastgele yeni bir madde ekle
                    state = random.choice(['solid', 'liquid', 'gas'])
                    element = random.choice(list(ELEMENTS.keys()))
                    x = random.randint(0, WIDTH-100)
                    y = random.randint(0, HEIGHT-100)
                    width = random.randint(50, 120)
                    height = random.randint(50, 120)
                    density = random.uniform(0.3, 0.6)
                    
                    new_matter = Matter(x, y, width, height, state, density, element)
                    matters.append(new_matter)
                    all_atoms.extend(new_matter.atoms)
                    
                    if len(all_atoms) > MAX_ATOMS:
                        all_atoms = all_atoms[:MAX_ATOMS]
                        
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset
                    matters = [
                        Matter(100, 100, 100, 100, 'solid', 0.4, 6),
                        Matter(300, 400, 120, 80, 'liquid', 0.5, 1),
                        Matter(500, 200, 150, 120, 'gas', 0.3, 8),
                        Matter(700, 500, 80, 80, 'solid', 0.6, 26),
                    ]
                    all_atoms = []
                    for matter in matters:
                        all_atoms.extend(matter.atoms)
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key == pygame.K_g:
                    # Yerçekimini aç/kapa
                    physics_engine.gravity = 0 if physics_engine.gravity > 0 else 0.1
        
        # Ekranı temizle
        screen.fill(BACKGROUND)
        
        # Fizik güncellemeleri
        if not paused:
            all_atoms = physics_engine.update(all_atoms)
        
        # Madde ve atomları çiz
        for matter in matters:
            matter.draw(screen)
        
        # Bilgi paneli
        pygame.draw.rect(screen, (30, 30, 50, 200), (10, 10, 300, 150))
        fps = int(clock.get_fps())
        text = font.render(f"Atom Sayısı: {len(all_atoms)} | FPS: {fps}", True, WHITE)
        screen.blit(text, (20, 20))
        
        bond_count = sum(len(atom.bonded_atoms) for atom in all_atoms) // 2
        text2 = font.render(f"Kimyasal Bağlar: {bond_count}", True, CYAN)
        screen.blit(text2, (20, 45))
        
        text3 = font.render(f"Yerçekimi: {'Açık' if physics_engine.gravity > 0 else 'Kapalı'}", True, YELLOW)
        screen.blit(text3, (20, 70))
        
        # Kontrol bilgileri
        text4 = font.render("Boşluk: Yeni Madde | P: Duraklat | R: Sıfırla", True, GREEN)
        screen.blit(text4, (20, 95))
        
        text5 = font.render("H: Yardım | G: Yerçekimi", True, GREEN)
        screen.blit(text5, (20, 120))
        
        # Duraklatma mesajı
        if paused:
            pause_text = title_font.render("DURAKLATILDI", True, YELLOW)
            screen.blit(pause_text, (WIDTH//2 - 100, 10))
        
        # Yardım ekranı
        if show_help:
            help_surface = pygame.Surface((WIDTH-100, HEIGHT-100), pygame.SRCALPHA)
            help_surface.fill((10, 10, 30, 230))
            screen.blit(help_surface, (50, 50))
            
            help_title = title_font.render("Atom Simülasyonu - Yardım", True, YELLOW)
            screen.blit(help_title, (WIDTH//2 - 150, 70))
            
            helps = [
                "• Bu simülasyon atomların gerçekçi etkileşimlerini gösterir",
                "• Atomlar birbirleriyle kimyasal bağlar oluşturabilir",
                "• Farklı elementler farklı özelliklere sahiptir",
                "• Beyaz çizgiler kimyasal bağları temsil eder",
                "• Katılar daha yavaş, gazlar daha hızlı hareket eder",
                "• Yerçekimi gaz atomlarını daha az etkiler",
                "",
                "KONTROLLER:",
                "• Boşluk: Rastgele yeni madde ekle",
                "• P: Simülasyonu duraklat/devam ettir",
                "• R: Simülasyonu sıfırla",
                "• G: Yerçekimini aç/kapa",
                "• H: Bu yardım ekranını göster/gizle"
            ]
            
            for i, help_text in enumerate(helps):
                text = font.render(help_text, True, WHITE)
                screen.blit(text, (70, 120 + i*25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()

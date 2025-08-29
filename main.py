#By Cesar Gabriel Castillo Chavez
#By Joel Flores Reyes
#By Gael Sanchez Mora 

import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import io, sys
import board

# -------- utilidades juego --------
def set_bats():
    while True:
        b1, b2 = random.randint(1, 20), random.randint(1, 20)
        if b1 != b2:
            return [b1, b2]

def set_pits(bats):
    while True:
        p1, p2 = random.randint(1, 20), random.randint(1, 20)
        if p1 != p2 and p1 not in bats and p2 not in bats:
            return [p1, p2]

def set_wumpus(home, pits, bats):
    while True:
        w = random.randint(1, 20)
        if w != home and w not in pits and w not in bats:
            return w

def set_home(wumpus, bats, pits, prev_home):
    while True:
        h = random.randint(1, 20)
        if h != prev_home and h != wumpus and h not in bats and h not in pits:
            return h

# -------- GUI --------
class WumpusGUI(tk.Tk):
    COLOR_BG = "#101418"
    COLOR_EDGE = "#8B5A2B"   # café
    COLOR_NODE = "#D9D9D9"   # sala normal
    COLOR_NODE_OUTLINE = "#30343A"
    COLOR_PIT = "#1FAA59"    # verde
    COLOR_BAT = "#8A2BE2"    # morado
    COLOR_PLAYER = "#2F88FF" # azul
    COLOR_TEXT = "#E6E6E6"

    def _init_(self):
        super()._init_()
        self.title("Hunt the Wumpus - Tk")
        self.configure(bg=self.COLOR_BG)
        self.resizable(False, False)

        self.board = board.dodecahedron

        # estado
        self.arrows = 5
        self.bats = []
        self.pits = []
        self.wumpus = None
        self.home = None
        self.dead = False
        self.wumpus_dead = False

        # salas peligrosas descubiertas por el jugador
        self.discovered_hazards = set()

        # canvas
        self.W, self.H = 900, 650
        self.canvas = tk.Canvas(self, width=self.W, height=self.H, bg=self.COLOR_BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=12, pady=12)

        # panel lateral
        side = tk.Frame(self, bg=self.COLOR_BG)
        side.grid(row=0, column=1, sticky="ns", padx=(0,12), pady=12)

        self.lbl_room = tk.Label(side, text="Sala actual: -", fg=self.COLOR_TEXT, bg=self.COLOR_BG, font=("Segoe UI", 13, "bold"))
        self.lbl_room.pack(anchor="w", pady=(0,8))

        self.lbl_neighbors = tk.Label(side, text="Vecinas: -", fg=self.COLOR_TEXT, bg=self.COLOR_BG, font=("Segoe UI", 11))
        self.lbl_neighbors.pack(anchor="w", pady=(0,8))

        self.lbl_arrows = tk.Label(side, text="Flechas: 5", fg=self.COLOR_TEXT, bg=self.COLOR_BG, font=("Segoe UI", 11))
        self.lbl_arrows.pack(anchor="w", pady=(0,16))

        btn_shoot = ttk.Button(side, text="Disparar", command=self.on_shoot)
        btn_help  = ttk.Button(side, text="Ayuda", command=self.on_help)
        btn_reset = ttk.Button(side, text="Reiniciar", command=self.reset_game)
        btn_quit  = ttk.Button(side, text="Salir", command=self.destroy)
        for b in (btn_shoot, btn_help, btn_reset, btn_quit):
            b.pack(fill="x", pady=4)

        # estilo ttk
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=8)

        # geometría nodos
        self.node_radius = 18
        self.player_radius = 8
        self.node_coords = self._compute_node_positions()
        self.node_items = {}  # room -> (circle_id, text_id)
        self.edge_items = []
        self.player_item = None

        self._draw_graph_base()
        self.reset_game()

    # ----- dibujo base -----
    def _compute_node_positions(self):
        cx, cy = self.W//2 - 40, self.H//2
        r = min(self.W, self.H) * 0.40
        coords = {}
        for i in range(1, 21):
            ang = 2*math.pi*(i-0.25)/20.0
            x = cx + r*math.cos(ang)
            y = cy + r*math.sin(ang)
            coords[i] = (x, y)
        return coords

    def _draw_graph_base(self):
        # aristas
        for room, adj in self.board.items():
            x1, y1 = self.node_coords[room]
            for key in ("room1", "room2", "room3"):
                r2 = adj[key]
                if room < r2:  # evitar duplicados
                    x2, y2 = self.node_coords[r2]
                    line = self.canvas.create_line(x1, y1, x2, y2, fill=self.COLOR_EDGE, width=3, capstyle=tk.ROUND)
                    self.edge_items.append(line)

        # nodos
        for room in range(1, 21):
            x, y = self.node_coords[room]
            c = self.canvas.create_oval(
                x-self.node_radius, y-self.node_radius,
                x+self.node_radius, y+self.node_radius,
                fill=self.COLOR_NODE, outline=self.COLOR_NODE_OUTLINE, width=2
            )
            t = self.canvas.create_text(x, y, text=str(room), fill="black", font=("Segoe UI", 11, "bold"))
            self.node_items[room] = (c, t)
            self.canvas.tag_bind(c, "<Button-1>", lambda e, r=room: self.try_move_to(r))
            self.canvas.tag_bind(t, "<Button-1>", lambda e, r=room: self.try_move_to(r))

    def _colorize_nodes(self):
        # reset
        for room, (c, _) in self.node_items.items():
            self.canvas.itemconfig(c, fill=self.COLOR_NODE, outline=self.COLOR_NODE_OUTLINE, width=2)

        # dibujar solo los peligros ya descubiertos
        for room in self.discovered_hazards:
            if room in self.pits:
                c, _ = self.node_items[room]
                self.canvas.itemconfig(c, fill=self.COLOR_PIT)
            if room in self.bats:
                c, _ = self.node_items[room]
                self.canvas.itemconfig(c, fill=self.COLOR_BAT)

    def _place_player(self):
        x, y = self.node_coords[self.home]
        if self.player_item is None:
            self.player_item = self.canvas.create_oval(
                x-self.player_radius, y-self.player_radius,
                x+self.player_radius, y+self.player_radius,
                fill=self.COLOR_PLAYER, outline="white", width=1.5
            )
        else:
            self.canvas.coords(self.player_item, x-self.player_radius, y-self.player_radius,
                               x+self.player_radius, y+self.player_radius)

    def _update_hud(self):
        neigh = self._neighbors(self.home)
        self.lbl_room.config(text=f"Sala actual: {self.home}")
        self.lbl_neighbors.config(text=f"Vecinas: {', '.join(map(str, neigh))}")
        self.lbl_arrows.config(text=f"Flechas: {self.arrows}")

    def _neighbors(self, room):
        a = self.board[room]
        return [a["room1"], a["room2"], a["room3"]]

    # ----- ciclo de juego -----
    def reset_game(self):
        self.arrows = 5
        self.bats = set_bats()
        self.pits = set_pits(self.bats)
        self.wumpus = set_wumpus(0, self.pits, self.bats)
        self.home = set_home(self.wumpus, self.bats, self.pits, 0)
        self.dead = False
        self.wumpus_dead = False
        self.discovered_hazards.clear()  # limpiar salas reveladas
        self._colorize_nodes()
        self._place_player()
        self._update_hud()
        self.after(80, self._hazard_messages)

    def try_move_to(self, dest_room):
        if self.dead or self.wumpus_dead:
            return
        neigh = self._neighbors(self.home)
        if dest_room == self.home:
            messagebox.showinfo("Movimiento", "Ya estás en esa sala.")
            return
        if dest_room not in neigh:
            messagebox.showwarning("Movimiento inválido", "Solo puedes moverte a salas vecinas.")
            return

        self.home = dest_room
        self._place_player()
        self._update_hud()

        # Si entraste a una sala peligrosa, quedará revelada
        if self.home in self.pits or self.home in self.bats:
            self.discovered_hazards.add(self.home)
            self._colorize_nodes()

        # eventos al entrar
        # Wumpus en la misma sala
        if self.home == self.wumpus:
            if random.randint(1, 100) > 25:
                self.dead = True
                messagebox.showerror("Game Over", "TSK TSK TSK - ¡El Wumpus te atrapó!")
                return
            else:
                messagebox.showinfo("Suerte", "¡Chocaste algo y salió corriendo! (El Wumpus se reubica)")
                self.wumpus = set_wumpus(self.home, self.pits, self.bats)

        if self.home in self.pits:
            self.dead = True
            messagebox.showerror("Game Over", "YYYIIIEEEE ¡Caíste en un pozo!")
            return

        if self.home in self.bats:
            messagebox.showwarning("Murciélagos", "¡ZAP! Los super murciélagos te cargan a otra sala…")
            self.home = set_home(self.wumpus, self.bats, self.pits, self.home)
            self._place_player()
            self._update_hud()
            # si caíste sobre algo, puede revelarse también
            if self.home in self.pits or self.home in self.bats:
                self.discovered_hazards.add(self.home)
                self._colorize_nodes()
            self.after(50, self._post_bat_check)
            return

        self._hazard_messages()

    def _post_bat_check(self):
        if self.home == self.wumpus:
            if random.randint(1, 100) > 25:
                self.dead = True
                messagebox.showerror("Game Over", "TSK TSK TSK - ¡El Wumpus te atrapó!")
                return
            else:
                messagebox.showinfo("Suerte", "¡Chocaste algo y salió corriendo! (El Wumpus se reubica)")
                self.wumpus = set_wumpus(self.home, self.pits, self.bats)

        if self.home in self.pits:
            self.dead = True
            messagebox.showerror("Game Over", "YYYIIIEEEE ¡Caíste en un pozo!")
            return

        self._hazard_messages()

    def _hazard_messages(self):
        neigh = self._neighbors(self.home)
        msgs = []
        if self.wumpus in neigh:
            msgs.append("¡Hueles a Wumpus!")
        if any(n in self.bats for n in neigh):
            msgs.append("Murciélagos cerca…")
        if any(n in self.pits for n in neigh):
            msgs.append("Sientes una corriente de aire… (pozo cerca)")
        if msgs:
            messagebox.showinfo("Advertencias", "\n".join(msgs))

    # ----- disparo -----
    def on_shoot(self):
        if self.dead or self.wumpus_dead:
            return
        if self.arrows < 1:
            messagebox.showwarning("Flechas", "Ya no te quedan flechas.")
            return

        n = simpledialog.askinteger("Disparo", "Número de salas (1-5). 0 = Cancelar", minvalue=0, maxvalue=5, parent=self)
        if n is None or n == 0:
            return

        path = [self.home]
        for i in range(1, n+1):
            r = simpledialog.askinteger("Disparo", f"Sala #{i} (vecina de la anterior):", minvalue=1, maxvalue=20, parent=self)
            if r is None:
                return
            path.append(r)

        self._shoot_arrow(path)

    def _shoot_arrow(self, arrow_path):
        self.arrows -= 1
        messagebox.showinfo("Disparo", "¡Twaaaang!")
        self._update_hud()
        if self.arrows < 1:
            messagebox.showwarning("Flechas", "Esa fue tu última flecha.")

        for idx in range(1, len(arrow_path)):
            prev_room, curr_room = arrow_path[idx-1], arrow_path[idx]
            if curr_room not in self._neighbors(prev_room):
                messagebox.showinfo("Flecha", "¡Smack! La flecha pegó en la pared.")
                return
            if curr_room == self.wumpus:
                self.wumpus_dead = True
                messagebox.showinfo("Victoria", "¡Auuuu! Mataste al Wumpus. Hee Hee - ¡Te verá la próxima vez!")
                return
            if curr_room == self.home:
                self.dead = True
                messagebox.showerror("Game Over", "¡Auch! ¡Te disparaste a ti mismo!")
                return

        messagebox.showinfo("Flecha", "¡Smack! La flecha no dio en nada útil.")

    # ----- ayuda (captura stdout) -----
    def on_help(self):
        buf, old = io.StringIO(), sys.stdout
        try:
            sys.stdout = buf
            board.instructions()
        except Exception:
            messagebox.showerror("Instrucciones", "No se pudieron cargar las instrucciones.")
            return
        finally:
            sys.stdout = old
        texto = buf.getvalue().strip() or "Instrucciones no disponibles."
        messagebox.showinfo("Instrucciones", texto)

if __name__=="_main_":
    app=WumpusGUI()
    app.mainloop()

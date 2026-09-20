import tkinter as tk
from tkinter import messagebox
from .theme import COLORS

class ControlCenter(tk.Tk):
    MODULES=[
        ("FIXE","Dashboard Postpaid / Fixe","▣","fixe"),
        ("FTTH","Contrôles Fibre","⌁","ftth"),
        ("INTERCONNECT","Contrôles Interconnect","⇄","interconnect"),
        ("SIMBOX","Contrôles SIMBOX","▤","simbox"),
        ("A2P / P2A","Messaging Revenue Assurance","✉","a2p_p2a"),
        ("FRANCHISE","Contrôles Franchise","◆","franchise"),
    ]
    def __init__(self):
        super().__init__(); self.title("RA Control Center"); self.geometry("1380x820"); self.minsize(1120,680); self.configure(bg=COLORS["bg"]); self.build()

    def build(self):
        h=tk.Frame(self,bg=COLORS["bg"],height=92); h.pack(fill="x",padx=34,pady=(24,0)); h.pack_propagate(False)
        tk.Label(h,text="◈",font=("Segoe UI",30,"bold"),fg=COLORS["accent"],bg=COLORS["bg"]).pack(side="left",padx=(0,12))
        b=tk.Frame(h,bg=COLORS["bg"]); b.pack(side="left",pady=5)
        tk.Label(b,text="RA CONTROL CENTER",font=("Segoe UI",20,"bold"),fg=COLORS["text"],bg=COLORS["bg"]).pack(anchor="w")
        tk.Label(b,text="Revenue Assurance • Central Control",font=("Segoe UI",9),fg=COLORS["muted"],bg=COLORS["bg"]).pack(anchor="w")
        s=tk.Frame(h,bg=COLORS["panel"],highlightbackground=COLORS["border"],highlightthickness=1); s.pack(side="right",pady=8)
        tk.Label(s,text="●",fg=COLORS["success"],bg=COLORS["panel"]).pack(side="left",padx=(14,5),pady=10)
        tk.Label(s,text="Système opérationnel",font=("Segoe UI",9,"bold"),fg=COLORS["text"],bg=COLORS["panel"]).pack(side="left",padx=(0,14))
        body=tk.Frame(self,bg=COLORS["bg"]); body.pack(fill="both",expand=True,padx=34)
        tk.Label(body,text="Modules Revenue Assurance",font=("Segoe UI",22,"bold"),fg=COLORS["text"],bg=COLORS["bg"]).pack(anchor="w",pady=(8,5))
        tk.Label(body,text="Sélectionnez un domaine pour ouvrir son environnement de contrôle.",font=("Segoe UI",10),fg=COLORS["muted"],bg=COLORS["bg"]).pack(anchor="w",pady=(0,22))
        g=tk.Frame(body,bg=COLORS["bg"]); g.pack(fill="both",expand=True)
        for i,m in enumerate(self.MODULES): self.card(g,m).grid(row=i//3,column=i%3,sticky="nsew",padx=7,pady=7)
        for c in range(3): g.grid_columnconfigure(c,weight=1)
        for r in range(2): g.grid_rowconfigure(r,weight=1)
        f=tk.Frame(self,bg=COLORS["sidebar"],height=42); f.pack(fill="x",side="bottom"); f.pack_propagate(False)
        tk.Label(f,text="Revenue Assurance • RA Control Center",font=("Segoe UI",8),fg=COLORS["muted"],bg=COLORS["sidebar"]).pack(side="left",padx=25)
        tk.Label(f,text="v1.0",font=("Consolas",8),fg=COLORS["muted"],bg=COLORS["sidebar"]).pack(side="right",padx=25)

    def card(self,p,m):
        name,desc,icon,key=m; 
        c=tk.Frame(p,bg=COLORS["panel"],highlightbackground=COLORS["border"],highlightthickness=1,cursor="hand2")
        ib=tk.Frame(c,bg=COLORS["panel_2"],width=64,height=64); 
        ib.pack(anchor="w",padx=22,pady=(24,18)); 
        ib.pack_propagate(False)
        tk.Label(ib,text=icon,font=("Segoe UI",25,"bold"),fg=COLORS["accent"],bg=COLORS["panel_2"]).pack(expand=True)
        tk.Label(c,text=name,font=("Segoe UI",15,"bold"),fg=COLORS["text"],bg=COLORS["panel"]).pack(anchor="w",padx=22)
        tk.Label(c,text=desc,font=("Segoe UI",9),fg=COLORS["muted"],bg=COLORS["panel"],wraplength=290,justify="left").pack(anchor="w",padx=22,pady=(7,18))
        tk.Frame(c,height=1,bg=COLORS["border"]).pack(fill="x",padx=22)
        q=tk.Frame(c,bg=COLORS["panel"]); q.pack(fill="x",padx=22,pady=16)
        tk.Label(q,text="Ouvrir le module",font=("Segoe UI",9,"bold"),fg=COLORS["accent"],bg=COLORS["panel"]).pack(side="left")
        tk.Label(q,text="→",font=("Segoe UI",17,"bold"),fg=COLORS["accent"],bg=COLORS["panel"]).pack(side="right")
        def click(e=None): self.open(key)
        def enter(e=None): c.configure(highlightbackground=COLORS["accent"])
        def leave(e=None): c.configure(highlightbackground=COLORS["border"])
        for w in c.winfo_children(): w.bind("<Button-1>",click); w.bind("<Enter>",enter); w.bind("<Leave>",leave)
        c.bind("<Button-1>",click); c.bind("<Enter>",enter); c.bind("<Leave>",leave); return c
    
    def open(self,key):
        if key!="fixe":
            messagebox.showinfo(key.upper(),f"Le module {key.upper()} sera ajouté prochainement.",parent=self); 
            return
        try: 
            from modules.fixe.dashboard import Dashboard
        except ImportError as e:
            messagebox.showerror("Dashboard FIXE","Impossible de charger le module FIXE.\n\n"+str(e),parent=self); 
            return
        
        w=tk.Toplevel(self); 
        w.title("RA • FIXE"); 
        w.geometry("1500x950"); 
        w.minsize(1250, 800); 
        w.configure(bg=COLORS["bg"])

        #w.transient(self)
        w.lift()
        w.focus_force()


        try:
            w.tk.call("tk", "scaling", 1.20)
        except Exception:
            pass

        try: 
            Dashboard(w,perimetre="FXL",mode_execution="COMMIT")
        except TypeError: 
            Dashboard(w)
        except Exception as e:
            w.destroy(); 
            messagebox.showerror("Erreur Dashboard FIXE",str(e),parent=self)

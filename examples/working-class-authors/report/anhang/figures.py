# -*- coding: utf-8 -*-
import json, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

M=json.load(open('out/tr_measures.json')); flow=json.load(open('out/flow.json'))
BG='#FDF6E3'; FG='#586E75'; GRID='#EEE8D5'
plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,
 'text.color':FG,'axes.labelcolor':FG,'xtick.color':FG,'ytick.color':FG,'axes.edgecolor':GRID,
 'font.size':11,'axes.titlesize':13,'axes.titleweight':'bold','font.family':'DejaVu Sans'})
DOM=['A·Kultur','B·Politik','C·Wirtschaft','D·Medien']
CSTR=['#6C71C4','#D33682','#859900','#268BD2']  # structure colours
CCAT=['#268BD2','#2AA198','#B58900','#DC322F']   # Etablierte/Anwärter/Bewahrende/Enttäuschte
INEQ=LinearSegmentedColormap.from_list('ineq',['#46CDB8','#E8B14C','#E8694C'])

# ---- Fig 1 : cascade 3 niveaux, empirique vs symétrique ----
c=M['cascade']; fig,ax=plt.subplots(figsize=(7,4.2))
labels=['transversal\n(zw. Strukturen)','horizontal\n(zw. Sequenzen)','vertikal\n(zw. Kategorien)']
emp=[c['transversal'],c['horizontal'],c['vertical']]; base=[0,0,c['vertical_baseline']]
x=np.arange(3); w=0.38
ax.bar(x-w/2,emp,w,label='empirisch (Kohorte)',color='#E8694C')
ax.bar(x+w/2,base,w,label='symmetrischer Referenzzustand',color='#93A1A1',alpha=.7)
for i,v in enumerate(emp): ax.text(i-w/2,v+.012,f'{v:.2f}',ha='center',fontsize=10,fontweight='bold')
for i,v in enumerate(base):
    if v>0: ax.text(i+w/2,v+.012,f'{v:.2f}',ha='center',fontsize=9,color=FG)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0,.6); ax.set_ylabel('Gini-Ungleichheit')
ax.set_title('Kaskade der drei Ungleichheitsebenen (§5.17)')
ax.legend(frameon=False,fontsize=9); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
for s in ['top','right']: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('out/fig1_kaskade.png',dpi=150); plt.close()

# ---- Fig 2 : vertikal par structure (apex homogénéise / dominé stratifie) ----
vx=M['vertGiniX']; fig,ax=plt.subplots(figsize=(7,4.2))
b=ax.bar(DOM,vx,color=CSTR,width=.6)
for i,v in enumerate(vx): ax.text(i,v+.015,f'{v:.2f}',ha='center',fontweight='bold')
ax.axhline(c['vertical_baseline'],ls='--',color=FG,lw=1)
ax.text(3.4,c['vertical_baseline']+.01,'sym. Referenz 0,40',ha='right',fontsize=8,color=FG)
ax.annotate('Apex homogenisiert\n(nur Etablierte)',xy=(1,vx[1]),xytext=(1,.30),ha='center',fontsize=9,
  arrowprops=dict(arrowstyle='->',color=FG))
ax.annotate('Beherrschte stratifiziert\n(Etablierte + Enttäuschte)',xy=(2,vx[2]),xytext=(2,.55),ha='center',fontsize=9,
  arrowprops=dict(arrowstyle='->',color=FG))
ax.set_ylim(0,.8); ax.set_ylabel('vertikale Ungleichheit (Gini)')
ax.set_title('Vertikale Ungleichheit je Struktur')
ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
for s in ['top','right']: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('out/fig2_vertikal_struktur.png',dpi=150); plt.close()

# ---- Fig 3 : heatmap structure x séquence (g), avec S ----
g=np.array(M['g']); Sn=np.array(M['S'])
fig,ax=plt.subplots(figsize=(6.8,4.6))
im=ax.imshow(g,cmap='YlGnBu',vmin=0,vmax=1,aspect='auto')
ax.set_xticks(range(4)); ax.set_xticklabels(['Seq. A','Seq. B','Seq. C','Seq. D'])
ax.set_yticks(range(4)); ax.set_yticklabels([f'{DOM[x]}\n(S={Sn[x]*100:.0f}%)' for x in range(4)])
for i in range(4):
    for j in range(4):
        v=g[i,j]
        if v>0.005: ax.text(j,i,f'{v*100:.0f}',ha='center',va='center',
                            color='white' if v>.5 else FG,fontsize=10,fontweight='bold')
ax.set_title('Sequenzgrößen g[Struktur][Sequenz] (% je Struktur)')
plt.colorbar(im,fraction=.046,pad=.04,label='Anteil')
plt.tight_layout(); plt.savefig('out/fig3_struktur_sequenz.png',dpi=150); plt.close()

# ---- Fig 4 : composition des catégories par structure ----
act=np.array(M['act']); g3=np.array(M['g']); 
comp=np.zeros((4,4))
for x in range(4):
    for s in range(4):
        comp[x]+=g3[x][s]*np.array(act[x][s])
comp=comp/comp.sum(1,keepdims=True)
fig,ax=plt.subplots(figsize=(7,4.2)); bottom=np.zeros(4)
names=['Etablierte','Anwärter','Bewahrende','Enttäuschte']
for c4 in range(4):
    ax.bar(DOM,comp[:,c4],bottom=bottom,color=CCAT[c4],label=names[c4],width=.6)
    bottom+=comp[:,c4]
ax.set_ylim(0,1); ax.set_ylabel('Anteil der Akteurkategorien')
ax.set_title('Zusammensetzung der Akteurkategorien je Struktur')
ax.legend(frameon=False,fontsize=9,ncol=4,loc='upper center',bbox_to_anchor=(.5,-.12))
for s in ['top','right']: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('out/fig4_kategorien.png',dpi=150); plt.close()

# ---- Fig 5 : flux transversal (structure -> structure) ----
F=np.array(flow,dtype=float); fig,ax=plt.subplots(figsize=(6.2,5))
im=ax.imshow(F,cmap=INEQ,aspect='auto')
ax.set_xticks(range(4)); ax.set_xticklabels(['→ '+d.split('·')[1] for d in DOM],rotation=20,ha='right')
ax.set_yticks(range(4)); ax.set_yticklabels(['von '+d.split('·')[1] for d in DOM])
for i in range(4):
    for j in range(4):
        if F[i,j]>0: ax.text(j,i,int(F[i,j]),ha='center',va='center',
                             color='white' if F[i,j]>F.max()*.55 else FG,fontweight='bold')
ax.set_title('Transversale Übergänge (Strukturwechsel)')
plt.colorbar(im,fraction=.046,pad=.04,label='Anzahl Übergänge')
plt.tight_layout(); plt.savefig('out/fig5_flux.png',dpi=150); plt.close()
print("5 figures écrites")

# ---- Fig 6 : atypicité origine->destination, cohorte vs base victorienne ----
fig,ax=plt.subplots(figsize=(7.2,4.4))
cats=['atteint le col blanc\n(HISCLASS I–V)','atteint l\'élite prof.\n(HISCLASS I–II)']
cohort=[79,62]; base=[8,0.2]   # base : ~5-10% classe moyenne ; ~0,2% sommet (Miles 1999)
x=np.arange(2); w=0.38
ax.bar(x-w/2,cohort,w,label='cohorte (fils de pères ouvriers, n=29)',color='#E8694C')
ax.bar(x+w/2,base,w,label='classe ouvrière anglaise 1839–1914 (Miles 1999)',color='#93A1A1')
for i,v in enumerate(cohort): ax.text(i-w/2,v+1.5,f'{v:.0f}%',ha='center',fontweight='bold')
for i,v in enumerate(base): ax.text(i+w/2,v+1.5,(f'{v:.1f}%' if v<1 else f'~{v:.0f}%'),ha='center',fontsize=9,color=FG)
ax.set_ylim(0,90); ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylabel('% des hommes nés ouvriers')
ax.set_title('Sortie de la classe ouvrière : cohorte vs population de référence')
ax.legend(frameon=False,fontsize=9,loc='upper right'); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
for s in ['top','right']: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('out/fig6_atypicite.png',dpi=150); plt.close()
print("fig6 écrite")

# ---- Fig 7 : comparaison B (intensité à résolution dégradée) ----
fig,ax=plt.subplots(figsize=(7.6,4.5))
labels=['Übertritt manuell→nicht-manuell\n(intra-vital)','Aufstieg ungelernt→gelernt\n(gewöhnliche Fluidität)']
cohort=[52,29]; ref=[5,40]
x=np.arange(2); w=0.38
ax.bar(x-w/2,cohort,w,label='Kohorte',color='#E8694C')
ax.bar(x+w/2,ref,w,label='Referenz (Miles / Long 2013)',color='#93A1A1')
for i,v in enumerate(cohort): ax.text(i-w/2,v+1.5,f'{v:.0f}%',ha='center',fontweight='bold')
for i,v in enumerate(ref): ax.text(i+w/2,v+1.5,f'~{v:.0f}%',ha='center',fontsize=9,color=FG)
ax.text(0,-13,'distinktiv (Grenzüberschreitung)',ha='center',fontsize=8.5,color='#E8694C',style='italic')
ax.text(1,-13,'unauffällig — Palier wird übersprungen',ha='center',fontsize=8.5,color=FG,style='italic')
ax.set_ylim(0,90); ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel('% der Akteure')
ax.set_title('Vergleich B — Intensität bei angeglichener Auflösung')
ax.legend(frameon=False,fontsize=9,loc='upper right'); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.annotate('Residuum (kohortenintern): Richtungsumkehrungen 37% → 11%\nbei dekadischer Auflösung — vom Zensus nicht erfassbar',
  xy=(0.5,0.0),xytext=(0.5,72),fontsize=8,ha='center',color=FG,
  bbox=dict(boxstyle='round,pad=0.4',fc='#EEE8D5',ec='none'))
plt.tight_layout(); plt.savefig('out/fig7_vergleich_AB.png',dpi=150); plt.close()
print("fig7 écrite")

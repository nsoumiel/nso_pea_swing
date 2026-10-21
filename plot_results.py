"""Optional plotting helper; requires matplotlib. Not used by the trading bot."""
import csv,datetime,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=pathlib.Path(__file__).resolve().parent
fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True,gridspec_kw={'height_ratios':[2,1]})
for name,label,color in [('monthly10','Mensuelle 10 mois','#17746d'),('weekly200','Hebdomadaire 200 séances','#b77a19'),('buy_hold','Achat-conservation','#5366ad')]:
    rows=list(csv.DictReader(open(root/f'results/validation_{name}_equity.csv')))
    dates=[datetime.date.fromisoformat(r['date']) for r in rows];v=[float(r['equity']) for r in rows];peak=5000;dd=[]
    for e in v:peak=max(peak,e);dd.append(100*(e/peak-1))
    axes[0].plot(dates,v,label=label,color=color);axes[1].plot(dates,dd,color=color)
axes[0].set_title('PEA — 5 000 € simulés du 02/01/2020 au 20/10/2026',loc='left',fontweight='bold')
axes[0].set_ylabel('Valeur nette de liquidation (€)');axes[1].set_ylabel('Baisse depuis le sommet (%)');axes[0].legend(loc='upper left')
for ax in axes:ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
fig.text(.1,.015,'Parts entières • Frais Bourse Direct + 0,10 % par côté • Source : Yahoo • Simulation rétrospective',fontsize=9,color='#555555')
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(root/'results/comparaison.png',dpi=150)

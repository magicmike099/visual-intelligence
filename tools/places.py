import json
d=json.load(open('paris.json'))
LON0,LAT0,KX,KY=d['origin']
T="""s|Gare du Nord|48.8809|2.3553
s|Gare de l'Est|48.8768|2.3592
s|Gare de Lyon|48.8443|2.3735
s|Gare Saint-Lazare|48.8763|2.3253
s|Gare Montparnasse|48.8410|2.3210
s|Gare d'Austerlitz|48.8420|2.3655
s|Gare de Bercy|48.8390|2.3826
m|Tour Eiffel|48.8584|2.2945
m|Musée du Louvre|48.8606|2.3376
m|Notre-Dame de Paris|48.8530|2.3499
m|Sacré-Cœur|48.8867|2.3431
m|Arc de Triomphe (Étoile)|48.8738|2.2950
m|Panthéon|48.8462|2.3459
m|Centre Pompidou|48.8606|2.3522
m|Musée d'Orsay|48.8600|2.3266
m|Les Invalides|48.8566|2.3125
m|Opéra Garnier|48.8720|2.3316
m|Opéra Bastille|48.8521|2.3700
m|Hôtel de Ville|48.8566|2.3522
m|Galeries Lafayette|48.8738|2.3320
m|Grand Rex|48.8706|2.3477
m|Sorbonne|48.8488|2.3430
m|Tour Montparnasse|48.8421|2.3220
m|Bibliothèque François-Mitterrand|48.8336|2.3765
m|Accor Arena (Bercy)|48.8386|2.3785
m|Parc des Princes|48.8414|2.2530
m|Paris Expo Porte de Versailles|48.8323|2.2875
q|Place de la Bastille|48.8532|2.3692
q|Place de la République|48.8675|2.3637
q|Place de la Nation|48.8484|2.3958
q|Place de la Concorde|48.8656|2.3212
q|Place de Clichy|48.8836|2.3274
q|Place d'Italie|48.8310|2.3557
q|Place de la Madeleine|48.8700|2.3245
q|Place des Vosges|48.8556|2.3655
q|Place du Tertre (Montmartre)|48.8865|2.3408
q|Place Monge (Mouffetard)|48.8425|2.3500
q|Place Denfert-Rochereau|48.8339|2.3324
q|Trocadéro|48.8626|2.2875
q|Châtelet|48.8584|2.3474
q|Les Halles|48.8620|2.3470
q|Pigalle|48.8820|2.3373
q|Barbès-Rochechouart|48.8838|2.3497
q|Belleville|48.8722|2.3767
q|Ménilmontant|48.8664|2.3834
q|Oberkampf|48.8647|2.3689
q|Voltaire|48.8578|2.3800
q|Saint-Michel|48.8534|2.3440
q|Saint-Germain-des-Prés|48.8539|2.3338
q|Odéon|48.8520|2.3390
q|Le Marais (Saint-Paul)|48.8552|2.3608
q|Arts et Métiers|48.8654|2.3562
q|Strasbourg-Saint-Denis|48.8697|2.3541
q|Grands Boulevards|48.8716|2.3431
q|Champs-Élysées (Franklin D. Roosevelt)|48.8690|2.3090
q|Stalingrad|48.8843|2.3685
q|Batignolles|48.8824|2.3215
q|Ternes|48.8781|2.2981
q|Passy|48.8576|2.2858
q|Bir-Hakeim|48.8539|2.2894
q|Porte Maillot|48.8780|2.2830
q|Porte de Clignancourt|48.8975|2.3445
q|Porte de la Chapelle|48.8977|2.3592
q|Porte de Bagnolet|48.8645|2.4087
q|Porte de Vincennes|48.8470|2.4105
q|Porte d'Orléans|48.8235|2.3255
q|Porte d'Italie|48.8190|2.3595
q|Porte de Versailles|48.8323|2.2875
q|Cité Universitaire|48.8205|2.3380
q|La Villette|48.8938|2.3930
q|Canal Saint-Martin|48.8710|2.3655
p|Jardin du Luxembourg|48.8462|2.3372
p|Jardin des Tuileries|48.8635|2.3275
p|Jardin des Plantes|48.8440|2.3590
p|Parc des Buttes-Chaumont|48.8809|2.3828
p|Cimetière du Père-Lachaise|48.8614|2.3933
p|Parc Monceau|48.8796|2.3088
p|Champ de Mars|48.8556|2.2986"""
pl=[]
for line in T.splitlines():
    k,n,a,b=line.split('|'); a=float(a);b=float(b)
    pl.append([n,k,round((b-LON0)*KX),round((a-LAT0)*KY)])
d['places']=pl
json.dump(d,open('paris.json','w'),separators=(',',':'),ensure_ascii=False)
print(len(pl))

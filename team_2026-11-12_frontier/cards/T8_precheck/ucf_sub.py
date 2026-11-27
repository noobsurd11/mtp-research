import csv, json, sys, os, collections
root=sys.argv[1]
rel={}
for split in ('train','test'):
    d=os.path.join(root,'training','data',split,'images')
    for f in os.listdir(d): rel[os.path.splitext(f)[0]]=split
imgcls=collections.defaultdict(set); area=collections.defaultdict(list)
with open(os.path.join(root,'AnnotationsCombined.csv')) as fh:
    for r in csv.DictReader(fh):
        st=os.path.splitext(r['filename'])[0]
        if st not in rel: continue
        a=json.loads(r['region_attributes'] or '{}').get('Defect_Class')
        if a: imgcls[st].add(a)
cnt=collections.Counter(); 
for split in ('train','test'):
    c=collections.Counter()
    for st,s in rel.items():
        if s!=split: continue
        for a in imgcls.get(st,()): c[a]+=1
        k=imgcls.get(st,set())
        if 'Crack_Isolated' in k: c['_iso_img']+=1
        if 'Crack_Closed' in k and not ({'Crack_Isolated','Crack_Resistive'}&k): c['_closed_only_img']+=1
        if {'Crack_Isolated','Crack_Resistive'}&k: c['_iso_or_res_img']+=1
    print(split, sum(1 for s in rel.values() if s==split), dict(sorted(c.items())))

# Same-physical-cell check by local feature matching (lead, 15 Nov 2026). P532 images only (open cells).
import csv, re, sys, os, numpy as np, cv2
D='/home/noob/work/bench_reads/stageA/dup/run1/'; R='/home/noob/work/bench_data/roots/cv5v2_v1_f1/labeled/images/'
rows=[r for r in csv.DictReader(open(D+'pairs_labelled.tsv'), delimiter='\t')]
def parts(s):
    m=re.match(r'([A-Z]+)_(\d+)_(r\d+_c\d+)$', s); return m.groups() if m else (s.split('_')[0], None, None)
cl=cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)); sift=cv2.SIFT_create(nfeatures=3000)
cache={}
def feats(stem):
    if stem not in cache:
        p=R+stem+'.png'
        if not os.path.exists(p): cache[stem]=None
        else:
            im=cl.apply(cv2.imread(p, cv2.IMREAD_GRAYSCALE)); k,d=sift.detectAndCompute(im, None); cache[stem]=(k,d)
    return cache[stem]
bf=cv2.BFMatcher(cv2.NORM_L2)
def inliers(a,b):
    fa,fb=feats(a),feats(b)
    if fa is None or fb is None or fa[1] is None or fb[1] is None or len(fa[0])<8 or len(fb[0])<8: return None
    m=bf.knnMatch(fa[1], fb[1], k=2); good=[x for x,y in (p for p in m if len(p)==2) if x.distance<0.75*y.distance]
    if len(good)<6: return (0,len(good),0.0)
    pa=np.float32([fa[0][g.queryIdx].pt for g in good]); pb=np.float32([fb[0][g.trainIdx].pt for g in good])
    M,mask=cv2.estimateAffinePartial2D(pa,pb,method=cv2.RANSAC,ransacReprojThreshold=3.0)
    if M is None: return (0,len(good),0.0)
    sc=float(np.hypot(M[0,0],M[1,0]))
    return (int(mask.sum()), len(good), sc)
P=lambda r: r['a_set']=='P532' and r['b_set']=='P532'
known=[r for r in rows if r['known_same_cell']=='1' and P(r)]
cand=[r for r in rows if r['category']=='P532_crossfold' and parts(r['a'])[0]==parts(r['b'])[0] and parts(r['a'])[2] and parts(r['a'])[2]==parts(r['b'])[2]]
out=[]
for tag,L in (('known',known),('cand',cand)):
    for r in L:
        v=inliers(r['a'],r['b'])
        if v is None: continue
        out.append((tag,r['a'],r['a_fold'],r['b'],r['b_fold'],r['ncc'],r['cos'],v[0],v[1],round(v[2],3)))
w=csv.writer(open(sys.argv[1],'w'),delimiter='\t'); w.writerow(['tag','a','a_fold','b','b_fold','ncc','cos','inliers','good','scale']); w.writerows(out)
kn=sorted(x[7] for x in out if x[0]=='known'); cn=sorted((x for x in out if x[0]=='cand'), key=lambda x:-x[7])
print('known same-cell P532 pairs:', len(kn), 'inliers min/quartiles/max', kn[0], kn[len(kn)//4], kn[len(kn)//2], kn[3*len(kn)//4], kn[-1])
print('candidates (cross-fold, same source, same grid position):', len(cn))
for x in cn[:14]: print(x)
import collections
print('candidate inlier histogram:', sorted(collections.Counter(min(x[7]//10*10,100) for x in cn).items()))

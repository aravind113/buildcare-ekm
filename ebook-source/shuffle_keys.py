import re,random,glob,sys
LET=re.compile(r'(?<![\w\-+])[A-D](?![\w\-+])')
def process(path,seed):
    s=open(path,encoding='utf-8').read()
    head,rest=s.split('@mcq\n',1)
    mcq,tail=rest.split('@revision',1)
    blocks=[b for b in re.split(r'\n\s*\n',mcq.strip('\n')) if b.strip()]
    rng=random.Random(seed)
    parsed=[]
    for b in blocks:
        lines=b.strip('\n').split('\n')
        q=lines[0]; opts={}; ans=None; exp=[]
        for l in lines[1:]:
            m=re.match(r'^([ABCD]): (.*)$',l)
            if m: opts[m.group(1)]=m.group(2); continue
            if l.startswith('ANS: '): ans=l[5:].strip(); continue
            exp.append(l)
        parsed.append((q,opts,ans,'\n'.join(exp)))
    # decide which are shufflable
    idx=[i for i,(q,o,a,e) in enumerate(parsed) if len(o)==4 and not LET.search(e) and not any(('ഇവയെല്ലാം' in t or 'മുകളിലെ എല്ലാം' in t) for t in o.values())]
    order=list(idx); rng.shuffle(order)
    targets=['A','B','C','D']
    # count fixed answers
    cnt={k:0 for k in targets}
    for i,(q,o,a,e) in enumerate(parsed):
        if i not in idx: cnt[a]+=1
    out={}
    for i in order:
        # choose the letter with the lowest count (random tiebreak)
        mn=min(cnt.values()); cands=[k for k in targets if cnt[k]==mn]
        t=rng.choice(cands); cnt[t]+=1
        q,o,a,e=parsed[i]
        correct=o[a]; others=[o[k] for k in 'ABCD' if k!=a]
        rng.shuffle(others)
        new={}
        it=iter(others)
        for k in targets:
            new[k]=correct if k==t else next(it)
        out[i]=(q,new,t,e)
    res=[]
    for i,(q,o,a,e) in enumerate(parsed):
        if i in out: q,o,a,e=out[i]
        blk=[q]+[f'{k}: {o[k]}' for k in 'ABCD']+[f'ANS: {a}',e]
        res.append('\n'.join(blk))
    new='\n\n'.join(res)+'\n'
    open(path,'w',encoding='utf-8').write(head+'@mcq\n'+new+'@revision'+tail)
    final={k:0 for k in targets}
    for i,(q,o,a,e) in enumerate(parsed):
        final[out[i][2] if i in out else a]+=1
    return len(parsed),len(idx),final
for n in range(1,21):
    p=f'chapters/ch{n:02d}.txt'
    # always start from original
    import shutil; shutil.copy(f'chapters_orig/ch{n:02d}.txt',p)
    print(n,process(p,1000+n))

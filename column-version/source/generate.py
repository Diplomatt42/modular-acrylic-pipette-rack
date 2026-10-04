# SPDX-License-Identifier: CC-BY-4.0
# Attribution: Diplomatt42; see ../ATTRIBUTION.md.
"""Regenerate the shared-shelf acrylic box from portable JSON inputs.

DXFs describe finished parts in inches. STEP uses millimetres. No laser kerf
offset is baked into either format. See README.md before modifying fit values.
"""
from pathlib import Path
import argparse, csv, json, math
import cadquery as cq
import ezdxf
from ezdxf import units, bbox

MM_PER_INCH = 25.4

def require(condition, message):
    if not condition:
        raise ValueError(message)

def rectangle(x,y,w,h):
    return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]

def panel_outline(width,bottom,top,tabwidth,clear,projection):
    p=[(0,projection)]
    for c in bottom:
        a,b=c-tabwidth/2,c+tabwidth/2
        p.extend([(a,projection),(a,0),(b,0),(b,projection)])
    p.extend([(width,projection),(width,projection+clear)])
    for c in reversed(top):
        a,b=c-tabwidth/2,c+tabwidth/2
        p.extend([(b,projection+clear),(b,2*projection+clear),
                  (a,2*projection+clear),(a,projection+clear)])
    p.append((0,projection+clear))
    return p

def add_loop(msp,pts,r):
    tangents=[]
    for i,p in enumerate(pts):
        prev,nxt=pts[i-1],pts[(i+1)%len(pts)]
        u=[p[k]-prev[k] for k in range(2)]
        v=[nxt[k]-p[k] for k in range(2)]
        lu,lv=math.hypot(*u),math.hypot(*v)
        require(min(lu,lv)>1e-9,'Outline has a zero-length edge.')
        u=[k/lu for k in u];v=[k/lv for k in v]
        angle=math.acos(max(-1,min(1,sum(u[k]*v[k] for k in range(2)))))
        d=r*math.tan(angle/2)
        require(d<min(lu,lv)/2+1e-9,'Corner radius is too large for a feature.')
        a=tuple(p[k]-u[k]*d for k in range(2))
        b=tuple(p[k]+v[k]*d for k in range(2))
        sign=1 if u[0]*v[1]-u[1]*v[0]>0 else -1
        center=(a[0]-u[1]*r*sign,a[1]+u[0]*r*sign)
        tangents.append((a,b,center,sign))
    for i,(a,b,c,sign) in enumerate(tangents):
        msp.add_line(tangents[i-1][1],a,dxfattribs={'layer':'0'})
        start,end=(a,b) if sign>0 else (b,a)
        sa=math.degrees(math.atan2(start[1]-c[1],start[0]-c[0]))%360
        ea=math.degrees(math.atan2(end[1]-c[1],end[0]-c[0]))%360
        msp.add_arc(c,r,sa,ea,dxfattribs={'layer':'0'})

def write_dxf(path,loops,r):
    doc=ezdxf.new('R2010');doc.units=units.IN
    doc.header['$MEASUREMENT']=0;doc.header['$LUNITS']=2
    doc.header['$LUPREC']=6
    for loop in loops:
        add_loop(doc.modelspace(),loop,r)
    doc.saveas(path)
    read=ezdxf.readfile(path);audit=read.audit()
    require(not audit.errors and not audit.fixes,f'DXF audit failed: {path.name}')
    ends=[]
    for e in read.modelspace():
        require(e.dxftype() in ('LINE','ARC') and e.dxf.layer=='0','Unexpected cutting entity.')
        ends.extend([tuple(e.dxf.start)[:2],tuple(e.dxf.end)[:2]]
                    if e.dxftype()=='LINE' else [tuple(e.start_point)[:2],tuple(e.end_point)[:2]])
    require(all(sum(math.dist(p,q)<1e-8 for q in ends)==2 for p in ends),
            f'Open or ambiguous contour: {path.name}')
    graph={}
    for i in range(0,len(ends),2):
        a,b=[tuple(round(k,8) for k in p) for p in ends[i:i+2]]
        graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
    pending=set(graph);components=0
    while pending:
        components+=1;stack=[pending.pop()]
        while stack:
            for q in graph[stack.pop()]:
                if q in pending:
                    pending.remove(q);stack.append(q)
    require(components==len(loops),'Unexpected contour count.')
    return read

def solid_from_dxf(path,t):
    shape=cq.importers.importDXF(str(path)).wires().toPending().extrude(t).val()
    require(shape.isValid() and len(shape.Solids())==1,f'Invalid part: {path.name}')
    return shape.scale(MM_PER_INCH)

def box_distance(a,b):
    x,y,w,h=a;X,Y,W,H=b
    return math.hypot(max(x-X-W,X-x-w,0),max(y-Y-H,Y-y-h,0))

def collision_check(parts):
    checked=0
    for i,(name,a) in enumerate(parts):
        A=a.BoundingBox()
        for other,b in parts[i+1:]:
            checked+=1;B=b.BoundingBox()
            overlap=[min(getattr(A,k+'max'),getattr(B,k+'max'))-
                     max(getattr(A,k+'min'),getattr(B,k+'min')) for k in 'xyz']
            if all(v>1e-6 for v in overlap):
                require(a.intersect(b).Volume()<1e-5,f'Colliding bodies: {name}, {other}')
    return checked

def make_stack(shelf,side,back,n,column,t,proj,pitch,margin,bw,bd,iw,cw):
    mm=MM_PER_INCH
    parts=[(f'Shelf_{i}',shelf.translate((0,0,i*pitch*mm))) for i in range(n+1)]
    for level in range(n):
        z=t-proj+level*pitch
        for label,x in [('Left',margin),('Right',margin+bw-t)]:
            for pos,y in ([('Front',0),('Rear',bd-cw)] if column else [('Full',0)]):
                p=side.rotate((0,0,0),(1,1,1),120).translate((x*mm,y*mm,z*mm))
                parts.append((f'{label}_{pos}_{level}',p))
        p=back.rotate((0,0,0),(1,0,0),90).translate(((margin+t)*mm,bd*mm,z*mm))
        parts.append((f'Back_{level}',p))
    return parts

def export_assembly(path,parts,expected_size):
    pairs=collision_check(parts)
    assembly=cq.Assembly(name=path.stem)
    for name,part in parts:
        assembly.add(part,name=name,color=cq.Color(.4,.7,.85,.55))
    assembly.export(str(path))
    read=cq.importers.importStep(str(path)).val();bb=read.BoundingBox()
    require(read.isValid() and len(read.Solids())==len(parts),'STEP reimport failed.')
    require(abs(read.Volume()-sum(p.Volume() for _,p in parts))<.001,'STEP volume changed.')
    require(abs(bb.zmin)<1e-6,'Bottom shelf is not on the counter plane.')
    for actual,expected in zip((bb.xlen,bb.ylen,bb.zlen),expected_size):
        require(abs(actual-expected*MM_PER_INCH)<1e-5,'Assembly dimensions changed.')
    return {'bodies':len(parts),'collision_pairs_checked':pairs,'STEP_reimport':'pass',
            'overall_dimensions_mm':[v*MM_PER_INCH for v in expected_size]}

def nest_rectangles(items,width,height,gap,margin):
    """Conservative bounding-box nesting, not a minimum-sheet proof."""
    usable_w=width-2*margin;usable_h=height-2*margin
    require(min(usable_w,usable_h)>0,'Sheet margins exceed the bed size.')
    bins=[]
    for name,w,h in sorted(items,key=lambda p:(max(p[1:]),p[1]*p[2]),reverse=True):
        require((w<=usable_w and h<=usable_h) or (h<=usable_w and w<=usable_h),
                f'{name} cannot fit on the configured laser bed with its edge margin.')
        best=None
        for bi,bin in enumerate(bins):
            for fi,(x,y,fw,fh) in enumerate(bin['free']):
                for rotate,(W,H) in enumerate([(w+gap,h+gap),(h+gap,w+gap)]):
                    if W<=fw+1e-9 and H<=fh+1e-9:
                        score=(min(fw-W,fh-H),max(fw-W,fh-H),bi,fi,rotate)
                        if best is None or score<best[0]:
                            best=(score,bi,x,y,W,H,rotate)
        if best is None:
            bins.append({'free':[(0,0,usable_w+gap,usable_h+gap)],'placed':[]})
            bi=len(bins)-1;W,H=(w+gap,h+gap) if w<=usable_w and h<=usable_h else (h+gap,w+gap)
            best=((0,),bi,0,0,W,H,int(W==h+gap and w!=h))
        _,bi,x,y,W,H,rotate=best;bin=bins[bi]
        split=[]
        for X,Y,FW,FH in bin['free']:
            if x>=X+FW-1e-9 or x+W<=X+1e-9 or y>=Y+FH-1e-9 or y+H<=Y+1e-9:
                split.append((X,Y,FW,FH));continue
            if x>X:split.append((X,Y,x-X,FH))
            if x+W<X+FW:split.append((x+W,Y,X+FW-x-W,FH))
            if y>Y:split.append((X,Y,FW,y-Y))
            if y+H<Y+FH:split.append((X,y+H,FW,Y+FH-y-H))
        unique=list(dict.fromkeys(r for r in split if min(r[2:])>1e-8))
        bin['free']=[a for i,a in enumerate(unique) if not any(i!=j and a[0]>=b[0]-1e-9
                    and a[1]>=b[1]-1e-9 and a[0]+a[2]<=b[0]+b[2]+1e-9
                    and a[1]+a[3]<=b[1]+b[3]+1e-9 for j,b in enumerate(unique))]
        bin['placed'].append((name,x+margin,y+margin,h if rotate else w,w if rotate else h,bool(rotate)))
    for bin in bins:
        p=bin['placed']
        for name,x,y,w,h,rot in p:
            require(x>=margin-1e-8 and y>=margin-1e-8 and x+w<=width-margin+1e-8
                    and y+h<=height-margin+1e-8,'Nested part exceeds the bed.')
        for i,a in enumerate(p):
            for b in p[i+1:]:
                _,x,y,w,h,_=a;_,X,Y,W,H,_=b
                require(x+w+gap<=X+1e-8 or X+W+gap<=x+1e-8 or y+h+gap<=Y+1e-8
                        or Y+H+gap<=y+1e-8,'Nested parts overlap or violate spacing.')
    return [b['placed'] for b in bins]

def generate(config_path,profile_path,out):
    cfg=json.loads(config_path.read_text());profile=json.loads(profile_path.read_text())
    require(cfg['schema_version']==1 and profile['schema_version']==1,'Unsupported JSON schema.')
    require(cfg['variant'] in ('solid','column'),'Variant must be solid or column.')
    column=cfg['variant']=='column'
    g=cfg['geometry_mm'];j=cfg['joints_mm'];mm=MM_PER_INCH
    bw,bd,bh,t,margin,cw=[g[k]/mm for k in ('body_width','body_depth','single_box_overall_height',
                                          'stock_model_thickness','shelf_overhang','column_width')]
    proj,r,st,sc,bt,bc,clearance=[j[k]/mm for k in ('tab_projection','corner_radius','side_tab_width',
                                          'side_slot_length_clearance','back_tab_width',
                                          'back_slot_length_clearance','slot_thickness_clearance')]
    require(all(math.isfinite(v) and v>0 for v in (bw,bd,bh,t,margin,cw,proj,r,st,sc,bt,bc,clearance)),
            'All geometric lengths and slip-fit clearances must be finite and positive.')
    require(proj<t,'Tab projection must be shorter than stock thickness to keep the base flat.')
    iw=bw-2*t;clear=bh-2*t;pitch=clear+t;sw=bw+2*margin;sd=bd+margin
    require(clear>2*r and iw>bt+2*r,'Width or height is too small for the joints.')
    require(bd>2*cw,'Front and rear column zones must remain separate.')
    # One common shelf works in both variants. Lower and upper walls deliberately
    # use different slot sets so opposing tabs never occupy the same slot.
    a=.3125*cw;b=.6875*cw
    side_a=[a,bd-cw+a];side_b=[b,bd-cw+b]
    back_a=[iw*f for f in cfg['back_tab_fractions']['bottom']]
    back_b=[iw*f for f in cfg['back_tab_fractions']['top']]
    require(len(back_a)==len(back_b)==2,'Each back edge requires two tabs.')
    for width,centers,tab in [(cw,[a,b],st),(iw,back_a+back_b,bt)]:
        require(all(tab/2+r<c<width-tab/2-r for c in centers),'A tab lies beyond its panel edge.')
    slot_t=t+clearance;side_slot=st+sc;back_slot=bt+bc
    slots=[]
    for x in [margin+t/2,margin+bw-t/2]:
        for y in side_a+side_b:
            slots.append((x-slot_t/2,y-side_slot/2,slot_t,side_slot))
    for x in back_a+back_b:
        slots.append((margin+t+x-back_slot/2,bd-t/2-slot_t/2,back_slot,slot_t))
    edge=min(min(x,y,sw-x-w,sd-y-h) for x,y,w,h in slots)
    web=min(box_distance(a,b) for i,a in enumerate(slots) for b in slots[i+1:])
    limits=profile['feature_limits_mm']
    require(edge*mm>=limits['minimum_slot_to_edge'],'Slot-to-edge bridge is too small.')
    require(web*mm>=limits['minimum_web'],'Slot-to-slot web is too small.')
    require(min(slot_t,side_slot,back_slot)*mm>=limits['minimum_hole_width'],'Slot width is too small.')
    n=cfg['stack_compartments'];racks=profile['racks_to_nest']
    require(isinstance(n,int) and not isinstance(n,bool) and 1<=n<=50,'Compartment count must be 1..50.')
    require(isinstance(racks,int) and not isinstance(racks,bool) and 1<=racks<=100,'Rack count must be 1..100.')
    loops={
        'shelf':[rectangle(0,0,sw,sd)]+[rectangle(*s) for s in slots],
        'column' if column else 'side_panel':[panel_outline(cw if column else bd,[a] if column else side_a,
                [b] if column else side_b,st,clear,proj)],
        'back_panel':[panel_outline(iw,back_a,back_b,bt,clear,proj)]}
    bounds={'shelf':(sw,sd),'column' if column else 'side_panel':(cw if column else bd,clear+2*proj),
            'back_panel':(iw,clear+2*proj)}
    quantities={'shelf':n+1,'column' if column else 'side_panel':(4 if column else 2)*n,'back_panel':n}
    for folder in ('cutting','models','laser_layouts','calibration'):
        (out/folder).mkdir(parents=True,exist_ok=True)
    # Inputs are copied alongside derived outputs, making alternate runs reviewable.
    (out/'design_parameters_used.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (out/'laser_profile_used.json').write_text(json.dumps(profile,indent=2)+'\n')
    shapes={};part_report={}
    for name,L in loops.items():
        dxf=out/'cutting'/f'{name}.dxf';doc=write_dxf(dxf,L,r)
        part=solid_from_dxf(dxf,t);shapes[name]=part
        cq.exporters.export(part,str(out/'models'/f'part_{name}.step'))
        bb=bbox.extents(doc.modelspace());size=[bb.size.x,bb.size.y]
        require(all(abs(v-e)<1e-7 for v,e in zip(size,bounds[name])),'DXF envelope differs from design.')
        part_report[name]={'DXF_audit':'pass','contours':len(L),'bounds_mm':[v*mm for v in size],
                           'net_area_mm2':part.Volume()/(t*mm),'quantity_per_rack':quantities[name]}
    side=shapes['column' if column else 'side_panel'];shelf=shapes['shelf'];back=shapes['back_panel']
    assemblies={}
    for count,filename in [(1,'one_complete_box.step'),(n,f'{n}_compartment_stack.step')]:
        parts=make_stack(shelf,side,back,count,column,t,proj,pitch,margin,bw,bd,iw,cw)
        assemblies[filename]=export_assembly(out/'models'/filename,parts,(sw,sd,count*clear+(count+1)*t))
    with (out/'cut_list.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['part','quantity_per_rack','quantity_to_nest','width_mm','height_mm','stock_thickness_mm'])
        for name,(w,h) in bounds.items():
            writer.writerow([name,quantities[name],quantities[name]*racks,w*mm,h*mm,t*mm])
    bed=profile['bed_mm'];gap=profile['part_spacing_mm']/mm;edge_margin=profile['edge_margin_mm']/mm
    require(gap>=0 and edge_margin>=0,'Bed spacing and margins must be nonnegative.')
    kerf=profile['measured_kerf_mm']
    require(kerf is None or (math.isfinite(kerf) and kerf>=0),'Kerf must be null or nonnegative.')
    items=[(name,w,h) for name,(w,h) in bounds.items() for _ in range(quantities[name]*racks)]
    sheets=nest_rectangles(items,bed['width']/mm,bed['height']/mm,gap,edge_margin)
    layout_report=[]
    for index,placed in enumerate(sheets,1):
        layout_loops=[]
        for name,x,y,w,h,rotate in placed:
            for L in loops[name]:
                if rotate:
                    L=[(bounds[name][1]-py,px) for px,py in L]
                layout_loops.append([(px+x,py+y) for px,py in L])
        filename=f'sheet_{index:02}.dxf'
        write_dxf(out/'laser_layouts'/filename,layout_loops,r)
        layout_report.append({'file':filename,'parts':[{'part':name,'x_mm':x*mm,'y_mm':y*mm,
                              'width_mm':w*mm,'height_mm':h*mm,'rotated_90':rot} for name,x,y,w,h,rot in placed]})
    # Fit ladder: unlabelled CUT-only drawing plus a separate slot map CSV.
    tests=profile['fit_coupon_clearances_mm']
    require(1<=len(tests)<=20 and all(math.isfinite(v) and v>0 for v in tests),'Invalid coupon clearances.')
    coupon_w=max(50/mm,side_slot+12/mm);row_pitch=max(t+max(tests)/mm+6/mm,8/mm)
    coupon_h=(len(tests)+1)*row_pitch
    coupon_loops=[rectangle(0,0,coupon_w,coupon_h)]
    for i,v in enumerate(tests):
        slotwidth=t+v/mm
        coupon_loops.append(rectangle((coupon_w-side_slot)/2,(i+1)*row_pitch-slotwidth/2,side_slot,slotwidth))
    write_dxf(out/'calibration'/'fit_ladder.dxf',coupon_loops,r)
    write_dxf(out/'calibration'/'fit_probe.dxf',[rectangle(0,0,st,25/mm)],r)
    with (out/'calibration'/'slot_map.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['slot_from_bottom','nominal_clearance_mm','finished_slot_width_mm'])
        writer.writerows((i+1,v,t*mm+v) for i,v in enumerate(tests))
    warnings=['Geometry is validated; physical fit, load capacity and stack stability remain untested.',
              'DXFs are finished-part geometry. Apply compensation once in CAM, never both in DXF and CAM.',
              'Nested layouts use rectangular envelopes; sheet count is conservative, not an optimum guarantee.',
              'Manual assembly requires temporary support while upper walls are uncapped.']
    if kerf is None:
        warnings.append('Laser kerf is unmeasured. Cut the fit coupon before producing the full rack.')
    report={'revision':cfg['revision'],'variant':cfg['variant'],'units':'mm except DXF (inch)',
            'clear_height_mm':clear*mm,'clear_width_mm':iw*mm,'repeat_pitch_mm':pitch*mm,
            'slot_width_mm':slot_t*mm,'slot_to_edge_min_mm':edge*mm,'slot_to_slot_min_mm':web*mm,
            'nominal_counter_tab_clearance_mm':(t-proj)*mm,'parts':part_report,'assemblies':assemblies,
            'racks_nested':racks,'nested_sheet_count':len(sheets),'layouts':layout_report,
            'laser_kerf_mm':kerf,'kerf_applied_to_DXF':False,'warnings':warnings}
    (out/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'variant':cfg['variant'],'output':str(out),'sheet_count':len(sheets),
                      'clear_height_mm':clear*mm,'validation':'pass'},indent=2))
    return report

def main():
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=root/'design_parameters.json')
    parser.add_argument('--laser-profile',type=Path,default=root/'laser_profile.json')
    parser.add_argument('--output',type=Path,default=root/'generated')
    args=parser.parse_args()
    require(not args.output.exists() or not any(args.output.iterdir()),
            'Output folder must be new or empty. Use --output to preserve earlier revisions.')
    generate(args.config,args.laser_profile,args.output)

if __name__=='__main__':
    main()

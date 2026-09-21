"""Exterior structural rhythm: buttresses and actual blind recessed openings.

Executed by 20_exterior with its mesh helpers. No interior or decorative tracery.
"""
import math
import bpy

glass = material("Unresolved exterior glazing (neutral)", (0.035,0.05,0.06))
door = material("West door placeholder (no sculpture)", (0.13,0.035,0.025))


def local_polygon(points, centre, tangent, normal, depth):
    return [(centre[0]+u*tangent[0]+depth*normal[0], centre[1]+u*tangent[1]+depth*normal[1],z) for u,z in points]


def pointed(width, bottom, top):
    rise=math.sqrt(3)*width/2
    spring=top-rise
    assert spring>bottom
    # Two intersecting circular arcs (equilateral pointed arch), not a rounded arch.
    points=[(-width/2,bottom),(width/2,bottom)]
    for i in range(9):
        angle=i*math.pi/3/8
        points.append((-width/2+width*math.cos(angle),spring+width*math.sin(angle)))
    for i in range(1,9):
        angle=2*math.pi/3+i*math.pi/3/8
        points.append((width/2+width*math.cos(angle),spring+width*math.sin(angle)))
    return points


def shaped_prism(name, profile, centre, tangent, normal, inner, outer, mat, keys):
    n=len(profile)
    verts=local_polygon(profile,centre,tangent,normal,inner)+local_polygon(profile,centre,tangent,normal,outer)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,"OPENINGS",mat,keys)


def opening(target, name, centre, tangent, normal, width, bottom, top, mat=glass, keys=()):
    profile=pointed(width,bottom,top)
    recess=p("opening_recess")
    # 1 cm construction allowance only: prevents coincident Boolean/backing faces.
    cutter=shaped_prism("CUT_"+name,profile,centre,tangent,normal,-recess,0.01,mat,keys)
    bpy.context.view_layer.objects.active=target
    modifier=target.modifiers.new("Recess_"+name,"BOOLEAN")
    modifier.operation="DIFFERENCE"
    modifier.solver="EXACT"
    modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    panel=shaped_prism(name,profile,centre,tangent,normal,-recess,-recess+0.01,mat,list(keys)+["opening_recess"])
    panel["evidence_status"]="inferred exterior recess with opaque backing; glazing pattern unresolved"


def two_windows(target,name,centre,tangent,normal,width=None):
    for level in ("lower","upper"):
        keys=["window_width",f"window_{level}_sill_z",f"window_{level}_top_z"]
        opening(target,f"Window_{name}_{level}",centre,tangent,normal,width or p("window_width"),
                p(f"window_{level}_sill_z"),p(f"window_{level}_top_z"),keys=keys)


def buttress(name,centre,normal,tower=False):
    tangent=(-normal[1],normal[0])
    levels=[0,p("buttress_mid_z"),p("buttress_top_z"),p("wall_eave_z")]
    if tower:
        levels=[0,p("wall_eave_z"),p("main_ridge_z"),p("tower_shaft_z")]
    for i,stage in enumerate(("base","mid","top")):
        width=p("buttress_width_"+stage)
        depth=p("buttress_depth_"+stage)
        poly=[(centre[0]+u*tangent[0]+d*normal[0],centre[1]+u*tangent[1]+d*normal[1])
              for u,d in ((-width/2,-0.01),(width/2,-0.01),(width/2,depth),(-width/2,depth))]
        prism(f"Buttress_{name}_{stage}",poly,levels[i+1],"BUTTRESSES",stone,
              ["buttress_width_"+stage,"buttress_depth_"+stage,"buttress_mid_z","buttress_top_z","wall_eave_z"],bottom=levels[i])


# Nave facade modules follow the existing roof bays.
bay=(p("nave_east_x")-p("nave_west_x"))/p("side_roof_bays")
for side in (-1,1):
    for i in range(int(p("side_roof_bays"))):
        x=p("nave_west_x")+(i+0.5)*bay
        two_windows(body,f"nave_{side}_{i}",(x,side*w),(1,0),(0,side))
    for i in range(int(p("side_roof_bays"))+1):
        buttress(f"nave_{side}_{i}",(p("nave_west_x")+i*bay,side*w),(0,side))

for name,angle in (("east",0),("north",math.pi/2),("south",-math.pi/2)):
    arc=[(shoulder+h*math.cos(-math.pi/2+i*math.pi/5),h*math.sin(-math.pi/2+i*math.pi/5)) for i in range(6)]
    for i in range(5):
        a,b=arc[i:i+2]
        length=math.dist(a,b)
        tangent=((b[0]-a[0])/length,(b[1]-a[1])/length)
        normal=(tangent[1],-tangent[0])
        centre=((a[0]+b[0])/2,(a[1]+b[1])/2)
        two_windows(body,f"{name}_facet_{i}",rotate([centre],angle)[0],rotate([tangent],angle)[0],rotate([normal],angle)[0])
    for i,point in enumerate(arc):
        normal=((point[0]-shoulder)/h,point[1]/h)
        buttress(f"{name}_polygon_{i}",rotate([point],angle)[0],rotate([normal],angle)[0])
    for side in (-1,1):
        # Covered junctions are not exterior facades and get no hidden openings.
        if (name=="east" and side==1) or (name=="north" and side==-1):
            continue
        start=w if (name=="north" and side==1) or (name=="south" and side==-1) else h
        count=1 if start==w else 2
        span=(shoulder-start)/count
        for i in range(count):
            centre=(start+(i+0.5)*span,side*h)
            two_windows(body,f"{name}_straight_{side}_{i}",rotate([centre],angle)[0],
                        rotate([(1,0)],angle)[0],rotate([(0,side)],angle)[0],width=min(p("window_width"),span-p("buttress_width_base")))

for label,sign in (("north",1),("south",-1)):
    target=bpy.data.objects["Tower_"+label]
    y=sign*ty
    # West face and outer flank, both supported by current photographs.
    for face,centre,tangent,normal in (("west",(tx-td/2,y),(0,1),(-1,0)),
                                       ("outer",(tx,y+sign*tw/2),(1,0),(0,sign))):
        opening(target,f"Tower_window_{label}_{face}_lower",centre,tangent,normal,p("window_width"),
                p("buttress_mid_z"),p("window_upper_top_z"),keys=["window_width","buttress_mid_z","window_upper_top_z"])
        opening(target,f"Tower_window_{label}_{face}_upper",centre,tangent,normal,p("window_width"),
                p("tower_window_upper_sill_z"),p("tower_window_upper_top_z"),keys=["window_width","tower_window_upper_sill_z","tower_window_upper_top_z"])
    for ex in (-1,1):
        for ey in (-1,1):
            corner=(tx+ex*td/2,y+ey*tw/2)
            buttress(f"tower_{label}_{ex}_{ey}_x",corner,(ex,0),True)
            buttress(f"tower_{label}_{ex}_{ey}_y",corner,(0,ey),True)

opening(bpy.data.objects["West_hall"],"West_portal",(tx-td/2,0),(0,1),(-1,0),p("portal_width"),0,p("portal_top_z"),door,
        ["portal_width","portal_top_z"])
opening(bpy.data.objects["West_hall"],"West_central_window",(tx-td/2,0),(0,1),(-1,0),p("portal_width"),
        p("window_upper_sill_z"),p("window_upper_top_z"),keys=["portal_width","window_upper_sill_z","window_upper_top_z"])
print("STRUCTURAL EXTERIOR: buttresses and recessed openings generated",flush=True)

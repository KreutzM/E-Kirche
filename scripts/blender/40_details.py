"""Evidence-led, simplified exterior detail. Not a printable detail specification."""
from mathutils import Vector


def tube(name, points, normal, radius, group="TRACERY", closed=False, keys=()):
    """Closed eight-sided swept mesh, including caps on open paths."""
    points=[Vector(v) for v in points]
    normal=Vector(normal).normalized()
    verts=[]
    for i,point in enumerate(points):
        before=points[(i-1)%len(points)] if closed or i else point
        after=points[(i+1)%len(points)] if closed or i<len(points)-1 else point
        tangent=(after-before).normalized()
        side=tangent.cross(normal).normalized()
        for j in range(8):
            v=point+radius*(math.cos(j*math.tau/8)*side+math.sin(j*math.tau/8)*normal)
            verts.append(tuple(v))
    faces=[]
    for i in range(len(points) if closed else len(points)-1):
        k=(i+1)%len(points)
        for j in range(8):
            faces.append((i*8+j,i*8+(j+1)%8,k*8+(j+1)%8,k*8+j))
    if not closed:
        faces.extend([tuple(reversed(range(8))),tuple(range((len(points)-1)*8,len(points)*8))])
    return mesh(name,verts,faces,group,stone,keys)


def path_on_wall(spec, points, depth=0):
    return local_polygon(points,spec["centre"],spec["tangent"],spec["normal"],depth)


def moulding(spec,name,profile,radius,closed=False,depth=0):
    return tube(name,path_on_wall(spec,profile,depth),(*spec["normal"],0),radius,closed=closed,
                keys=spec["keys"]+["tracery_radius","window_frame_radius","window_rose_ratio"])


# Unite only the already-overlapping upper tower masses so actual recesses cut
# every layer. No changes to the main tower core or photographic cameras.
for label,sign in (("north",1),("south",-1)):
    upper=bpy.data.objects["Tower_upper_octagon_"+label]
    bpy.context.view_layer.objects.active=upper
    for index in range(2):
        other=bpy.data.objects["Tower_gabled_stage_"+label+str(index)]
        mod=upper.modifiers.new("Upper_stage_union","BOOLEAN")
        mod.operation="UNION"; mod.solver="EXACT"; mod.object=other
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(other,do_unlink=True)
    for index,(nx,ny) in enumerate(((1,0),(-1,0),(0,1),(0,-1))):
        centre=(tx+nx*tw/2,sign*ty+ny*tw/2)
        opening(upper,f"Gable_window_{label}_{index}",centre,(-ny,nx),(nx,ny),
                p("tower_gable_opening_width"),p("tower_gable_opening_sill_z"),p("tower_gable_opening_top_z"),
                keys=["tower_gable_opening_width","tower_gable_opening_sill_z","tower_gable_opening_top_z"])
    for ex in (-1,1):
        for ey in (-1,1):
            x,y=tx+ex*tw/2,sign*ty+ey*tw/2
            r=p("pinnacle_radius")
            z=p("tower_shaft_z")
            keys=["pinnacle_radius","pinnacle_body_height","pinnacle_tip_height","tower_shaft_z","tower_width"]
            prism(f"Pinnacle_base_{label}_{ex}_{ey}",rect(x-r,x+r,y-r,y+r),z+p("pinnacle_body_height"),"DETAIL",stone,keys,bottom=z)
            cone(f"Pinnacle_tip_{label}_{ex}_{ey}",(x,y),r,z+p("pinnacle_body_height"),z+p("pinnacle_tip_height"),stone,"DETAIL",keys)

# Central stone clock gable replaces the formerly exposed plain roof triangle.
west=dict(centre=(tx-td/2-p("west_gable_depth"),0),tangent=(0,1),normal=(-1,0),keys=["west_gable_tip_z","west_gable_depth","west_clock_radius","west_clock_center_z"])
gable_face=shaped_prism("West_clock_gable",[(-ty+tw/2,p("wall_eave_z")),(ty-tw/2,p("wall_eave_z")),(0,p("west_gable_tip_z"))],
                        west["centre"],west["tangent"],west["normal"],-p("west_gable_depth"),0,stone,west["keys"])
opening(gable_face,"Clock_window",west["centre"],west["tangent"],west["normal"],p("west_clock_window_width"),p("wall_eave_z")+.3,p("west_clock_window_top_z"),
        keys=["west_clock_window_width","wall_eave_z","west_clock_window_top_z"])
moulding(west,"West_gable_raking_moulding",[(-ty+tw/2,p("wall_eave_z")),(0,p("west_gable_tip_z")),(ty-tw/2,p("wall_eave_z"))],p("window_frame_radius"))
metal=material("Clock | dark weathered metal",(.08,.095,.10))
clock_z=p("west_clock_center_z"); clock_r=p("west_clock_radius")
def clock_line(name,profile,closed=False):
    obj=moulding(west,name,profile,p("tracery_radius")*.65,closed,depth=.25)
    obj.data.materials.clear(); obj.data.materials.append(metal)
clock_line("Clock_ring",[(clock_r*math.cos(i*math.tau/48),clock_z+clock_r*math.sin(i*math.tau/48)) for i in range(48)],True)
for i in range(12):
    angle=i*math.tau/12
    clock_line(f"Clock_tick_{i}",[(clock_r*f*math.sin(angle),clock_z+clock_r*f*math.cos(angle)) for f in (.84,1.05)])
clock_line("Clock_hands",[(-clock_r*.4,clock_z+clock_r*.45),(0,clock_z),(clock_r*.3,clock_z-clock_r*.72)])

for spec in opening_specs:
    name=spec["name"]
    width,bottom,top=spec["width"],spec["bottom"],spec["top"]
    if name.startswith("Turret_"):
        continue
    frame=p("window_frame_radius")
    # U outline: start at right sill, traverse arch and return to left sill.
    outline=pointed(width+2*frame,bottom,top+frame)[1:]+[(-width/2-frame,bottom)]
    moulding(spec,"Frame_"+name,outline,frame)
    if name == "West_portal":
        for layer in range(1,int(p("portal_archivolt_count"))):
            offset=frame*2.3*layer
            outline=pointed(width+2*offset,bottom,top+offset)[1:]+[(-width/2-offset,bottom)]
            moulding(spec,f"Portal_archivolt_{layer}",outline,frame,depth=offset/2)
        shaped_prism("Portal_tympanum",pointed(width,p("portal_door_head_z"),top),spec["centre"],spec["tangent"],spec["normal"],-.29,-.08,stone,["portal_door_head_z","portal_width","portal_top_z"])
        moulding(spec,"Portal_central_mullion",[(0,0),(0,p("portal_door_head_z"))],frame,depth=-.1)
        moulding(spec,"Portal_lintel",[(-width/2,p("portal_door_head_z")),(width/2,p("portal_door_head_z"))],frame,depth=-.1)
        continue
    # Repeated two-light and circular-oculus pattern. Annex keeps a deliberately
    # simplified round motif rather than claiming an exact trefoil reconstruction.
    radius=min(p("tracery_radius"),width*.04)
    rose=p("window_rose_ratio")*width
    rose_z=top-.70*width
    ring=[(rose*math.cos(i*math.tau/32),rose_z+rose*math.sin(i*math.tau/32)) for i in range(32)]
    moulding(spec,"Rose_"+name,ring,radius,True,depth=-.12)
    apex=top-1.04*width
    for index,offset in enumerate((-width/4,width/4)):
        profile=pointed(width/2-2*radius,bottom,apex)
        arch=[(u+offset,z) for u,z in profile[1:]]+[(offset-width/4+radius,bottom)]
        moulding(spec,f"Lancet_{name}_{index}",arch,radius,depth=-.12)
    # Transoms give tall openings scale without inventing the interior.
    for index in range(1,4):
        z=bottom+(apex-bottom)*index/4
        moulding(spec,f"Transom_{name}_{index}",[(-width/2,z),(width/2,z)],radius*.45,depth=-.22)

# Continuous simple belt courses around the exposed nave and choir, following
# existing footprint edges. Junction segments inside another mass are omitted.
for side in (-1,1):
    for key in ("window_upper_sill_z","wall_eave_z"):
        tube(f"Nave_cornice_{side}_{key}",[(p("nave_west_x"),side*w,p(key)),(p("nave_east_x"),side*w,p(key))],
             (0,side,0),p("window_frame_radius"),"DETAIL",keys=[key,"window_frame_radius"])
for name,angle in (("east",0),("north",math.pi/2),("south",-math.pi/2)):
    arc=[(shoulder+h*math.cos(-math.pi/2+i*math.pi/int(p("conch_facets"))),h*math.sin(-math.pi/2+i*math.pi/int(p("conch_facets")))) for i in range(int(p("conch_facets"))+1)]
    for key in ("window_upper_sill_z","wall_eave_z"):
        tube(f"Choir_cornice_{name}_{key}",[(x,y,p(key)) for x,y in rotate(arc,angle)],(0,0,1),p("window_frame_radius"),"DETAIL",keys=[key,"window_frame_radius","conch_facets"])
print("DETAILS: paired lancets, roses, arch mouldings, pinnacles and portal",flush=True)

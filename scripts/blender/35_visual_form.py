"""PR 1 structural form corrections; no textures, tracery or print claims."""

# Horizontal massing bands make tower storeys legible without ornate profiles.
projection=p("structural_belt_projection")
thickness=p("structural_belt_height")
for label,sign in (("north",1),("south",-1)):
    # The intermediate buttress setback is NOT a belt across the tall openings.
    for key in ("wall_eave_z","tower_shaft_z"):
        prism(f"Tower_stage_band_{label}_{key}",
              rect(tx-td/2-projection,tx+td/2+projection,sign*ty-tw/2-projection,sign*ty+tw/2+projection),
              p(key)+thickness,"TOWERS",stone,[key,"structural_belt_projection","structural_belt_height"],bottom=p(key))
    # East and inward shaft faces are visible above the roofline.
    target=bpy.data.objects["Tower_"+label]
    for face,centre,tangent,normal in (("east",(tx+td/2,sign*ty),(0,1),(1,0)),
                                      ("inner",(tx,sign*(ty-tw/2)),(1,0),(0,-sign))):
        opening(target,f"Tower_window_{label}_{face}_upper",centre,tangent,normal,p("window_width"),
                max(p("main_ridge_z"),p("tower_window_upper_sill_z")),p("tower_window_upper_top_z"),
                keys=["window_width","main_ridge_z","tower_window_upper_sill_z","tower_window_upper_top_z"])

# Annex: two-storey openings and piers, formerly a featureless box.
sx,sy=p("sacristy_center_x"),p("sacristy_center_y")
dx,dy=p("sacristy_size_x")/2,p("sacristy_size_y")/2
annex=bpy.data.objects["Sacristy_envelope"]
for face,centre,tangent,normal,half in (("north",(sx,sy+dy),(1,0),(0,1),dx),
                                       ("east",(sx+dx,sy),(0,1),(1,0),dy)):
    for index,u in enumerate((-half/2,half/2)):
        xy=(centre[0]+u*tangent[0],centre[1]+u*tangent[1])
        for level in ("lower","upper"):
            opening(annex,f"Sacristy_{face}_{index}_{level}",xy,tangent,normal,p("sacristy_window_width"),
                    p(f"sacristy_{level}_sill_z"),p(f"sacristy_{level}_top_z"),
                    keys=["sacristy_window_width",f"sacristy_{level}_sill_z",f"sacristy_{level}_top_z"])
    for index,u in enumerate((-half,0,half)):
        xy=(centre[0]+u*tangent[0],centre[1]+u*tangent[1])
        for stage,bottom,top in (("base",0,p("sacristy_upper_sill_z")),("top",p("sacristy_upper_sill_z"),p("sacristy_eave_z"))):
            width=p("buttress_width_"+stage)
            depth=p("buttress_depth_"+stage)
            poly=[(xy[0]+v*tangent[0]+d*normal[0],xy[1]+v*tangent[1]+d*normal[1])
                  for v,d in ((-width/2,-.01),(width/2,-.01),(width/2,depth),(-width/2,depth))]
            prism(f"Sacristy_pier_{face}_{index}_{stage}",poly,top,"BUTTRESSES",stone,
                  ["buttress_width_"+stage,"buttress_depth_"+stage,"sacristy_upper_sill_z","sacristy_eave_z"],bottom=bottom)
for key in ("sacristy_upper_sill_z","sacristy_eave_z"):
    prism("Sacristy_band_"+key,rect(sx-dx-projection,sx+dx+projection,sy-dy-projection,sy+dy+projection),
          p(key),"MASSING",stone,[key,"structural_belt_projection","structural_belt_height"],bottom=p(key)-thickness)

# Cover the formerly exposed flat connector with a sloping roof, terminating
# against the existing annex pyramid. It uses only existing envelope dimensions.
x0,x1=h,sx-dx
y0,y1=sy-dy,sy+dy
z=p("sacristy_eave_z")
high=min(p("wall_eave_z"),p("sacristy_roof_z"))
mesh("Sacristy_connector_roof",[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),
     (x0,y0,high),(x1,y0,z+thickness),(x1,y1,z+thickness),(x0,y1,high)],
     [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],"ROOFS",slate,
     ["sacristy_eave_z","sacristy_roof_z","wall_eave_z","structural_belt_height"])

# Distinguish the existing modern lantern from a solid featureless chimney.
turret=bpy.data.objects["Crossing_turret_envelope"]
radius=p("crossing_turret_radius")
for index in range(8):
    angle=(index+1)*math.tau/8
    normal=(math.cos(angle),math.sin(angle))
    tangent=(-normal[1],normal[0])
    centre=tuple(v*radius*math.cos(math.pi/8) for v in normal)
    opening(turret,f"Turret_lantern_{index}",centre,tangent,normal,p("turret_lantern_width"),
            p("turret_lantern_sill_z"),p("turret_lantern_head_z"),
            keys=["turret_lantern_width","turret_lantern_sill_z","turret_lantern_head_z","crossing_turret_radius"])
print("VISUAL FORM: tower stages, annex and lantern completed",flush=True)

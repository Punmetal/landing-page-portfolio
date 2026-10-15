# Bake K2O_Logo_001.blend into a web-ready GLB.
#   metal parts (Metal / Scratched metal / Brushed Steel) -> one mesh, one UV atlas,
#     baked base color + ORM (AO, roughness, metallic) + tangent normal
#   neon tubes -> emissive material (glTF emissive + emissive_strength)
#   glass panel + water drops -> transmission material (KHR_materials_transmission + ior)
#
# usage (Blender 4.2+):
#   blender -b K2O_Logo_001.blend --python scripts/blender/bake-k2o-logo.py -- out.glb tex_dir [size] [glow]
# or with the bpy module (pip install bpy):
#   python scripts/blender/bake-k2o-logo.py in.blend out.glb tex_dir [size] [glow]
# Takes ~10 minutes on CPU. Writes the GLB, the baked PNGs and a baked .blend into tex_dir.
import bpy, sys, os, numpy as np, mathutils

if '--' in sys.argv:  # running inside the blender binary: the .blend is already open
    args = sys.argv[sys.argv.index('--') + 1:]
    SRC = bpy.data.filepath
else:
    args = sys.argv[1:]
    SRC = args.pop(0)
OUT, TEX = args[0], args[1]
SIZE = int(args[2]) if len(args) > 2 else 2048
GLOW_STRENGTH = float(args[3]) if len(args) > 3 else 1.5
os.makedirs(TEX, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
sc.frame_set(1)
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.render.bake.margin = 8

BAKE_MATS = {'Metal', 'Scratched metal', 'Brushed Steel Procedural'}
NEON_MATS = {'glass light neon'}

def select_only(objs, active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]

# Empty actions only; drop them so nothing gets exported as animation
for o in bpy.data.objects:
    o.animation_data_clear()

# 1. everything to real meshes, modifiers + transforms applied
objs = [o for o in sc.objects if o.type in ('MESH', 'CURVE') and o.visible_get()]
for o in objs:
    if o.type == 'MESH' and o.data.users > 1:
        o.data = o.data.copy()
select_only(objs)
bpy.ops.object.convert(target='MESH')
objs = [o for o in sc.objects if o.type == 'MESH']
select_only(objs)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def mats_of(o):
    return {s.material.name for s in o.material_slots if s.material}

metal = [o for o in objs if mats_of(o) & BAKE_MATS]
neon = [o for o in objs if mats_of(o) & NEON_MATS]
glass = [o for o in objs if o not in metal and o not in neon]
print('metal', len(metal), 'neon', len(neon), 'glass', [o.name for o in glass])

# 2. metal: keep each object's render UV as "SrcUV" so the materials sample
#    exactly what they did before, then join and lay out a fresh atlas "BakeUV"
for o in metal:
    uvs = o.data.uv_layers
    if not uvs:
        uvs.new(name='SrcUV')
    src = next((u for u in uvs if u.active_render), uvs[0])
    for u in list(uvs):
        if u != src:
            uvs.remove(u)
    uvs[0].name = 'SrcUV'
select_only(metal)
bpy.ops.object.join()
m = bpy.context.view_layer.objects.active
m.name = 'K2O_Metal'
src_uv = m.data.uv_layers['SrcUV']
bake_uv = m.data.uv_layers.new(name='BakeUV')
src_uv.active_render = True
m.data.uv_layers.active = bake_uv  # bake target
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004, area_weight=1.0, scale_to_bounds=True)
bpy.ops.uv.pack_islands(margin=0.004, rotate=True)
bpy.ops.object.mode_set(mode='OBJECT')

# real displacement does not survive glTF: turn it into bump so it lands in the normal map
for s in m.material_slots:
    if s.material:
        s.material.displacement_method = 'BUMP'

def new_img(name, data):
    img = bpy.data.images.new(name, SIZE, SIZE, alpha=False, float_buffer=True)
    img.colorspace_settings.name = 'Non-Color' if data else 'sRGB'
    return img

def with_target(img, fn):
    """Point every metal material at img (active image node) and run fn."""
    added = []
    for s in m.material_slots:
        nt = s.material.node_tree
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = img
        nt.nodes.active = n; added.append((nt, n))
    fn()
    for nt, n in added:
        nt.nodes.remove(n)

def bake_input(img, socket_name):
    """Route a Principled input (linked or constant) into an Emission shader and bake EMIT."""
    undo = []
    for s in m.material_slots:
        nt = s.material.node_tree
        p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
        old = out.inputs['Surface'].links[0].from_socket
        em = nt.nodes.new('ShaderNodeEmission')
        inp = p.inputs[socket_name]
        if inp.is_linked:
            nt.links.new(inp.links[0].from_socket, em.inputs['Color'])
        else:
            v = inp.default_value
            em.inputs['Color'].default_value = (v[0], v[1], v[2], 1) if hasattr(v, '__len__') else (v, v, v, 1)
        nt.links.new(em.outputs[0], out.inputs['Surface'])
        undo.append((nt, em, old, out))
    sc.cycles.samples = 8
    with_target(img, lambda: bpy.ops.object.bake(type='EMIT', use_clear=True))
    for nt, em, old, out in undo:
        nt.links.new(old, out.inputs['Surface'])
        nt.nodes.remove(em)

select_only([m])
imgs = {}
print('bake base color'); imgs['base'] = new_img('K2O_BaseColor', False); bake_input(imgs['base'], 'Base Color')
print('bake roughness'); imgs['rough'] = new_img('rough', True); bake_input(imgs['rough'], 'Roughness')
print('bake metallic'); imgs['metal'] = new_img('metal', True); bake_input(imgs['metal'], 'Metallic')
print('bake normal'); imgs['normal'] = new_img('K2O_Normal', True)
sc.cycles.samples = 8
sc.render.bake.normal_space = 'TANGENT'
with_target(imgs['normal'], lambda: bpy.ops.object.bake(type='NORMAL', use_clear=True))
print('bake ao'); imgs['ao'] = new_img('ao', True)
sc.cycles.samples = 64
with_target(imgs['ao'], lambda: bpy.ops.object.bake(type='AO', use_clear=True))

# neon glow: light the metal with the original neon only (black world, glass hidden)
# and bake the lighting, used as an emissive map since glTF viewers have no GI
print('bake neon glow')
GLOW = SIZE // 2
w = bpy.data.worlds.new('Black'); sc.world = w
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs[1].default_value = 0
for ob in glass:
    ob.hide_render = True
imgs['glow'] = bpy.data.images.new('glow', GLOW, GLOW, alpha=False, float_buffer=True)
imgs['glow'].colorspace_settings.name = 'Non-Color'
sc.cycles.samples = 384
with_target(imgs['glow'], lambda: bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, use_clear=True))
for ob in glass:
    ob.hide_render = False
g = np.array(imgs['glow'].pixels[:], dtype=np.float32).reshape(GLOW, GLOW, 4)
lum = g[..., :3].max(axis=2)
g[..., :3] /= max(np.percentile(lum[lum > 0], 99.5), 1e-6)
# soften bake noise: 5x5 box blur, then clamp
k = 2; pad = np.pad(g[..., :3], ((k, k), (k, k), (0, 0)), mode='edge')
acc = sum(pad[y:y + GLOW, x:x + GLOW] for y in range(2 * k + 1) for x in range(2 * k + 1)) / (2 * k + 1) ** 2
g[..., :3] = np.clip(acc, 0, 1); g[..., 3] = 1
glow_img = bpy.data.images.new('K2O_Glow', GLOW, GLOW, alpha=False, float_buffer=True)
glow_img.pixels[:] = g.ravel()

# pack ORM: R = AO, G = roughness, B = metallic (glTF convention)
px = lambda img: np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
orm = np.ones((SIZE * SIZE, 4), dtype=np.float32)
orm[:, 0] = px(imgs['ao'])[:, 0]
orm[:, 1] = px(imgs['rough'])[:, 0]
orm[:, 2] = px(imgs['metal'])[:, 0]
imgs['orm'] = new_img('K2O_ORM', True)
imgs['orm'].pixels[:] = orm.ravel()

def save(img, name):
    img.filepath_raw = os.path.join(TEX, name + '.png')
    img.file_format = 'PNG'
    img.save()
    return bpy.data.images.load(img.filepath_raw, check_existing=False)

base_png = save(imgs['base'], 'K2O_BaseColor')
orm_png = save(imgs['orm'], 'K2O_ORM'); orm_png.colorspace_settings.name = 'Non-Color'
nrm_png = save(imgs['normal'], 'K2O_Normal'); nrm_png.colorspace_settings.name = 'Non-Color'
glow_png = save(glow_img, 'K2O_Glow')
save(imgs['ao'], 'ao'); save(imgs['rough'], 'rough'); save(imgs['metal'], 'metal')

# final metal material, BakeUV only
mat = bpy.data.materials.new('K2O Metal')
nt = mat.node_tree; nt.nodes.clear()
p = nt.nodes.new('ShaderNodeBsdfPrincipled')
o = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(p.outputs[0], o.inputs[0])
tb = nt.nodes.new('ShaderNodeTexImage'); tb.image = base_png
nt.links.new(tb.outputs['Color'], p.inputs['Base Color'])
to = nt.nodes.new('ShaderNodeTexImage'); to.image = orm_png
sep = nt.nodes.new('ShaderNodeSeparateColor')
nt.links.new(to.outputs['Color'], sep.inputs[0])
nt.links.new(sep.outputs['Green'], p.inputs['Roughness'])
nt.links.new(sep.outputs['Blue'], p.inputs['Metallic'])
tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = nrm_png
nm = nt.nodes.new('ShaderNodeNormalMap')
nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
nt.links.new(nm.outputs['Normal'], p.inputs['Normal'])
te = nt.nodes.new('ShaderNodeTexImage'); te.image = glow_png
nt.links.new(te.outputs['Color'], p.inputs['Emission Color'])
p.inputs['Emission Strength'].default_value = GLOW_STRENGTH
# occlusion: the glTF exporter reads a group named "glTF Material Output"
grp = bpy.data.node_groups.get('glTF Material Output') or bpy.data.node_groups.new('glTF Material Output', 'ShaderNodeTree')
if 'Occlusion' not in [i.name for i in grp.interface.items_tree]:
    grp.interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')
g = nt.nodes.new('ShaderNodeGroup'); g.node_tree = grp
nt.links.new(sep.outputs['Red'], g.inputs['Occlusion'])
m.data.materials.clear(); m.data.materials.append(mat)
m.data.uv_layers.remove(m.data.uv_layers['SrcUV'])
m.data.uv_layers['BakeUV'].active_render = True

# 3. neon: emissive red, core pushed bright (the original used emission 254 + a facing ramp)
neon_mat = bpy.data.materials.new('K2O Neon')
nt = neon_mat.node_tree
p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value = (1.0, 0.08, 0.05, 1)
p.inputs['Roughness'].default_value = 0.25
p.inputs['Emission Color'].default_value = (1.0, 0.06, 0.03, 1)
p.inputs['Emission Strength'].default_value = 6.0
for ob in neon:
    ob.data.materials.clear(); ob.data.materials.append(neon_mat)
select_only(neon); bpy.ops.object.join()
n_obj = bpy.context.view_layer.objects.active; n_obj.name = 'K2O_Neon'
for u in list(n_obj.data.uv_layers):
    n_obj.data.uv_layers.remove(u)

# 4. glass panel and water drops: clear transmission (empty slots get glass)
def glass_mat(name, ior, rough):
    gm = bpy.data.materials.new(name)
    p = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (1, 1, 1, 1)
    p.inputs['Transmission Weight'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough
    p.inputs['IOR'].default_value = ior
    return gm
g_glass = glass_mat('K2O Glass', 1.45, 0.04)
# small drops render black with transmission in three.js: use a faint alpha-blended gloss instead
g_drop = bpy.data.materials.new('K2O Water')
p = next(n for n in g_drop.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
p.inputs['Base Color'].default_value = (1, 1, 1, 1)
p.inputs['Roughness'].default_value = 0.05
p.inputs['Alpha'].default_value = 0.3
g_drop.surface_render_method = 'BLENDED'
for ob in glass:
    for s in ob.material_slots:
        s.material = g_drop if (s.material and s.material.name == 'water drop') else g_glass
    for u in list(ob.data.uv_layers):
        ob.data.uv_layers.remove(u)
    ob.name = 'K2O_Glass'

# 5. center on the origin, 1 unit wide, delete everything else
final = [m, n_obj] + glass
for ob in [o for o in sc.objects if o not in final]:
    bpy.data.objects.remove(ob, do_unlink=True)
pts = [ob.matrix_world @ v.co for ob in final for v in ob.data.vertices]
mn = mathutils.Vector([min(p[i] for p in pts) for i in range(3)])
mx = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
c, k = (mn + mx) / 2, 1.0 / (mx.x - mn.x)
for ob in final:
    ob.data.transform(mathutils.Matrix.Scale(k, 4) @ mathutils.Matrix.Translation(-c))
    ob.data.update()
print('size', tuple(round(v * k, 3) for v in (mx - mn)))
for ob in final:
    print(ob.name, 'tris', sum(len(p.vertices) - 2 for p in ob.data.polygons))

select_only(final)
bpy.ops.export_scene.gltf(
    filepath=OUT, export_format='GLB', use_selection=True, export_yup=True,
    export_apply=True, export_animations=False, export_cameras=False, export_lights=False,
    export_draco_mesh_compression_enable=False, export_image_format='AUTO',
)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(TEX, 'K2O_Logo_baked.blend'))
print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')

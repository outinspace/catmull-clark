import math
from fractions import Fraction

def avg_verts(verts):
  ax, ay, az = Fraction(0), Fraction(0), Fraction(0)
  for (vx, vy, vz) in verts:
    ax += vx
    ay += vy
    az += vz
  return (ax/len(verts), ay/len(verts), az/len(verts))

def face_edges(fs):
  edges = []
  for f_index in range(len(fs)):
    face = fs[f_index]
    f_edges = [(face[v_index - 1], face[v_index], f_index) for v_index in range(len(face))]
    edges.extend(f_edges)
  return set(
    (frozenset([v1, v2]), frozenset([f1, f2])) 
    for (v1, v2, f1) in edges
    for (v3, v4, f2) in edges if v1 in [v3, v4] and v2 in [v4, v3] and f1 != f2
  )

def adjacent_edges(corner_point, edges):
  return [(vs, fs) for (vs, fs) in edges if corner_point in vs]
  
def edge_point(edge, faces):
  (e_verts, e_faces) = edge
  face_points = [avg_verts(faces[e_face_index]) for e_face_index in e_faces]
  return avg_verts(list(e_verts) + face_points)

def add_points(points):
  x, y, z = Fraction(0), Fraction(0), Fraction(0)
  for (x1, y1, z1) in points:
    x += x1
    y += y1
    z += z1
  return (x, y, z)

def mult_point_const(p, c):
  (x, y, z) = p
  cf = Fraction(c)
  return (x * cf, y * cf, z * cf)

def div_point_const(p, c):
  (x, y, z) = p
  cf = Fraction(c)
  return (x/cf, y/cf, z/cf)

input_file = open("cube.obj", "w")
input_faces = []

# cube
input_faces.append(((0,0,0), (0,1,0), (1,1,0), (1,0,0)))
input_faces.append(((0,0,0), (0,0,1), (0,1,1), (0,1,0)))
input_faces.append(((0,0,0), (1,0,0), (1,0,1), (0,0,1)))
input_faces.append(((0,0,1), (1,0,1), (1,1,1), (0,1,1)))
input_faces.append(((1,0,0), (1,1,0), (1,1,1), (1,0,1)))
input_faces.append(((0,1,0), (0,1,1), (1,1,1), (1,1,0)))

def catmull_clark(faces):
  edges = face_edges(faces)

  corner_points = set()
  for face_verts in faces:
    for vert in face_verts:
      corner_points.add(vert)

  new_faces = []
  for corner_point in corner_points:
    adj_edges = adjacent_edges(corner_point, edges)

    # Calculate new corner point
    adj_faces = set()
    for e_verts, e_faces in adj_edges:
      for f in e_faces:
        adj_faces.add(f)
    F = avg_verts([avg_verts(faces[fi]) for fi in adj_faces])
    R = avg_verts([avg_verts(e_verts) for (e_verts, e_faces) in adj_edges])
    new_corner_point = div_point_const(
      add_points([
        F, 
        mult_point_const(R, 2), 
        mult_point_const(corner_point, len(adj_faces) - 3)]
      ),
      len(adj_faces)
    )

    # Calculate new faces for corner point
    for adj_face_index in adj_faces:
      # Find 2 bounding edges adjacent to corner point
      bounding_edges = [edge for edge in adj_edges if adj_face_index in edge[1]]
      if len(bounding_edges) != 2:
        print('Not 2 bounding edges to a corner point face')
      
      e1 = bounding_edges[0]
      e_verts1, e_faces1 = e1
      e2 = bounding_edges[1]
      e_verts2, e_faces2 = e2
      common_face_index = list(e_faces1.intersection(e_faces2))[0]

      # Order vertices based on parent face (Clockwise v. Counter-clockwise)
      face_point = avg_verts(faces[common_face_index])
      edge_point1 = edge_point(e1, faces)
      edge_point2 = edge_point(e2, faces)
      output_points = []
      for point in faces[common_face_index]:
        if point == corner_point:
          output_points.append(new_corner_point)
        elif point in e_verts1:
          output_points.append(edge_point1)
        elif point in e_verts2:
          output_points.append(edge_point2)
        else:
          output_points.append(face_point)
      new_faces.append((output_points[0], output_points[1], output_points[2], output_points[3]))
  return new_faces

output_faces = input_faces
for i in range(3):
  print('Catmull-Clark iteration {}'.format(i+1))
  output_faces = catmull_clark(output_faces)

# Convert faces to vertices
vertices = set()
for face in output_faces:
  for vert in face:
    vertices.add(vert)

v_list = list(vertices)
vertice_strs = ["v {} {} {}".format(float(x), float(y), float(z)) for (x,y,z) in v_list]

face_strs = []

for face_vs in output_faces:
  indices = [v_list.index(face_v) + 1 for face_v in face_vs]
  face_strs.append("f {} {} {} {}".format(*indices))

string = "\n".join(vertice_strs) + "\n" + "\n".join(face_strs)

input_file.write(string)




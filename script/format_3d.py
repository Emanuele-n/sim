# Script to generate .obj and .msh files from an STL file. They are needed for the FEM simulation. 
""" 
.obj files: The Wavefront OBJ (Object) file format is a widely used format for representing 3D geometry. 
It stores information about vertices, normals, texture coordinates, and face connectivity. In the context of Sofa, 
.obj files are typically used to define the shape and appearance of objects in a simulation. 
For example, if you want to simulate a sofa, you can create or obtain an .obj file that describes its geometry 
(vertex positions, polygons, etc.) along with any associated material properties such as textures and colors.
The .obj file can then be loaded into Sofa to create the corresponding object within the simulation.

.msh files: The .msh file format is not specific to Sofa but is commonly used in finite element analysis (FEA) and computational physics.
It is a binary or ASCII file format that stores information about the mesh, which is a discretized representation of an
object's geometry used for numerical calculations. A mesh consists of nodes (vertices) and elements (e.g., triangles or tetrahedra) 
that connect these nodes to form a meshed surface or volume. In the context of Sofa, .msh files can be used to import 
pre-defined meshes or generate custom meshes for objects in a simulation. The .msh file contains the necessary data to define
the mesh topology, node positions, and element connectivity.

In both cases, when using Sofa, you would typically load these files into the framework using appropriate components or plugins 
provided by Sofa. These components can interpret the data in the files and create the corresponding simulation objects with the 
desired geometry and mesh. """ 


import argparse
import gmsh
import trimesh
import vtk
import pyvista as pv
import meshio

def convert_stl_to_msh(stl_file_path, msh_file_path):
    # Start gmsh
    gmsh.initialize()
    gmsh.model.add('model')

    # Merge the STL file
    gmsh.merge(stl_file_path)

    # Set meshing algorithm (2: 2D, 6: Frontal-Delaunay)
    gmsh.option.setNumber("Mesh.Algorithm", 6)

    # Generate 2D mesh
    gmsh.model.mesh.generate(2)

    # Save the mesh in MSH format
    gmsh.write(msh_file_path)

    # Finalize gmsh
    gmsh.finalize()

# Use function
#convert_stl_to_msh('skull.stl', 'skull.msh')

def convert_stl_to_obj(stl_path, obj_path):
    # Load the STL file
    mesh = trimesh.load(stl_path)

    # Save as OBJ
    mesh.export(obj_path)

# Example usage:
#convert_stl_to_obj("skull.stl", "skull.obj")
#convert_stl_to_obj("data/mesh/1dof_catheter.STL", "data/mesh/1dof_catheter.obj")

# Better using gmsh software (open terminal type "gmsh")
def stl_to_vtk(stl_filename, vtk_filename):

    ## Using vtk
    # Read STL
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stl_filename)

    # Write VTK
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(vtk_filename)
    writer.SetInputConnection(reader.GetOutputPort())
    writer.Write()

    ## Using pyvista
    # Read STL
    #mesh = pv.read(stl_filename)

    # Write VTK
    #mesh.save(vtk_filename)

    ## Using meshio
    # Read STL
    #mesh = meshio.read(stl_filename)

    # Write VTK
    #meshio.write(vtk_filename, mesh)
    

# Example usage:
# stl_to_vtk("input.stl", "output.vtk")
#stl_to_vtk("data/mesh/1dof_catheter.stl", "data/mesh/1dof_catheter.vtk") 

def main():
    # Define the command line arguments using argparse
    parser = argparse.ArgumentParser(description="Convert 3D file formats.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file.")
    
    # Parse the arguments
    args = parser.parse_args()

    # Extract the file extensions to determine the conversion type
    input_extension = args.input.split('.')[-1].lower()
    output_extension = args.output.split('.')[-1].lower()

    # Depending on the extensions, call the appropriate conversion function
    if input_extension == "stl" and output_extension == "msh":
        convert_stl_to_msh(args.input, args.output)
    elif input_extension == "stl" and output_extension == "obj":
        convert_stl_to_obj(args.input, args.output)
    elif input_extension == "stl" and output_extension == "vtk":
        stl_to_vtk(args.input, args.output)
    else:
        print(f"Conversion from {input_extension} to {output_extension} is not supported.")

# Uncomment the following line to run the program
if __name__ == "__main__":
    main()





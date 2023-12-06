from landxmlconvertor.classes.mesh2dm_reader import Mesh2DMReader
from landxmlconvertor.classes.mesh_elements import MeshFace, MeshVertex


def test_read(test_data_mesh2dm):
    mesh_2d = Mesh2DMReader(test_data_mesh2dm)

    assert isinstance(mesh_2d, Mesh2DMReader)
    assert all([isinstance(x, MeshVertex) for x in mesh_2d.points])
    assert all([isinstance(x, MeshFace) for x in mesh_2d.faces])

    assert all([isinstance(x.id, int) for x in mesh_2d.points])
    assert all([isinstance(x.x, float) for x in mesh_2d.points])
    assert all([isinstance(x.y, float) for x in mesh_2d.points])
    assert all([isinstance(x.z, float) for x in mesh_2d.points])

    assert all([isinstance(x.id, int) for x in mesh_2d.faces])
    assert all([all([isinstance(y, int) for y in x.points_ids]) for x in mesh_2d.faces])
